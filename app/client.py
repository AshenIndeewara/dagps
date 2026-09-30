import asyncio
import json
import re
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
from fastapi import HTTPException

from app.config import GPS_BASE_URL, GPS_TZ, get_credentials

session = {"mds": "", "cust_id": ""}
login_lock = asyncio.Lock()

RENAME = {"weidu": "lat", "jingdu": "lng", "su": "speed", "hangxiang": "heading"}
DROP = {"ljingdu", "lweidu"}
TIME_FIELDS = ("sys_time", "datetime", "heart_time", "server_time")

address_cache: dict[tuple[float, float], str] = {}

http = httpx.AsyncClient(
    base_url=GPS_BASE_URL,
    timeout=30,
    follow_redirects=True,
    headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
        "origin": GPS_BASE_URL,
        "referer": f"{GPS_BASE_URL}/Skins/DefaultIndex/",
        "x-requested-with": "XMLHttpRequest",
    },
)


def between(text: str, start: str, end: str) -> str:
    try:
        return text.split(start)[1].split(end)[0]
    except IndexError:
        return ""


def parse(text: str) -> Any:
    text = text.strip()
    m = re.match(r"^[\w.$]+\((.*)\);?$", text, re.S)
    if m:
        text = m.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise HTTPException(502, f"Unexpected upstream response: {text[:200]}")


def fill(d: dict[str, Any] | None) -> dict[str, str]:
    return {
        k: str(v).replace("{mds}", session["mds"]).replace("{cust}", session["cust_id"])
        for k, v in (d or {}).items()
    }


async def login() -> None:
    user, password = get_credentials()
    http.cookies.clear()
    r = await http.post(
        "/LoginByUser.aspx",
        params={"method": "loginSystem"},
        data={
            "userName": user,
            "pwd_": "",
            "loginType": "ENTERPRISE",
            "loginUrl": f"{GPS_BASE_URL}/Skins/DefaultIndex/",
            "pwd": password,
            "timeZone": str(GPS_TZ),
            "language": "en",
            "x": "72",
            "y": "9",
            "monitor": "0",
        },
    )
    login_id = between(r.text, "login_id=", "&")
    mds = between(r.text, "mds=", '"')
    if not (login_id and mds):
        raise HTTPException(502, "Login failed - check GPS_USER / GPS_PASSWORD")

    r = await http.get(
        "/dealer/sendRedirect.aspx",
        params={"logOut": "", "login_id": login_id, "mds": mds},
    )
    session["mds"] = between(r.text, "mds=", '"') or mds
    session["cust_id"] = between(r.text, "login_id=", "&") or login_id


async def call(method: str, url: str, params: dict[str, Any] | None = None, data: dict[str, Any] | None = None) -> str:
    for _ in range(2):
        if not session["mds"]:
            async with login_lock:
                if not session["mds"]:
                    await login()
        r = await http.request(method, url, params=fill(params), data=fill(data) or None)
        if "top.loginouts" in r.text:
            session["mds"] = ""
            continue
        r.raise_for_status()
        return r.text
    raise HTTPException(502, "Session expired and re-login failed")


def to_dicts(data: dict[str, Any]) -> list[dict[str, Any]]:
    key = data.get("key", {})
    out = []
    for row in data.get("records", []):
        d = {RENAME.get(k, k): row[i] for k, i in key.items() if i < len(row) and k not in DROP}
        for f in TIME_FIELDS:
            if isinstance(d.get(f), (int, float)) and d[f] > 0:
                d[f] = datetime.fromtimestamp(d[f] / 1000, timezone.utc).isoformat()
        try:
            d["speed"] = float(d["speed"])
        except (KeyError, ValueError, TypeError):
            pass
        try:
            d["odometer_km"] = float(d["statenumber"].split(",")[0])
        except (KeyError, ValueError, AttributeError):
            pass
        out.append(d)
    return out


def day_ms(d: date) -> int:
    local = datetime(d.year, d.month, d.day, tzinfo=timezone(timedelta(hours=GPS_TZ)))
    return int(local.timestamp() * 1000)


def day_end_ms(d: date) -> int:
    return day_ms(d + timedelta(days=1)) - 1000


def local_today() -> date:
    return datetime.now(timezone(timedelta(hours=GPS_TZ))).date()


def stay_seconds(s: str) -> int:
    m = re.match(r"(?:(\d+)Hour)?(?:(\d+)Minute)?(?:(\d+)Second)?", s or "")
    h, mi, sec = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + sec


async def add_addresses(records: list[dict[str, Any]]) -> None:
    points = [(r["lat"], r["lng"]) for r in records if r.get("lat") and r.get("lng")]
    todo = [p for p in dict.fromkeys(points) if p not in address_cache]
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]
        latlons = {f"row_{j}": {"Lat": str(lat), "Lon": str(lng)} for j, (lat, lng) in enumerate(chunk)}
        r = await http.get(
            "https://poi.18gps.net/poi/list",
            params={"callback": "cb", "latLons": json.dumps(latlons, separators=(",", ":")), "map": "", "key": ""},
        )
        r.raise_for_status()
        result = parse(r.text)
        for j, p in enumerate(chunk):
            address_cache[p] = result.get(f"row_{j}", "")
    for r in records:
        r["address"] = address_cache.get((r.get("lat"), r.get("lng")), "")
