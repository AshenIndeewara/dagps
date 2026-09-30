from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.client import (
    add_addresses,
    call,
    day_end_ms,
    day_ms,
    local_today,
    parse,
    stay_seconds,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/mileage")
async def mileage(start: date | None = None, end: date | None = None):
    """Mileage report (defaults to today)."""
    today = local_today()
    start = start or today
    end = end or start
    text = await call(
        "POST",
        "/GetDataService.aspx",
        params={"method": "report", "mds": "{mds}", "showZeroMil": "true"},
        data={
            "beginTime": day_ms(start),
            "endTime": day_ms(end),
            "enterprise_id": "{cust}",
            "channel": "ENTERPRISE",
            "radiobutton": "0",
        },
    )
    return parse(text)


@router.get("/daily-mileage")
async def daily_mileage(user_id: str, start: date | None = None, end: date | None = None):
    """Per-day mileage and stop count for one device."""
    start = start or local_today()
    end = end or start
    text = await call(
        "POST",
        "/GetDataService.aspx",
        params={"method": "RunIndex", "mds": "{mds}", "showZeroMil": "true"},
        data={
            "beginTime": day_ms(start),
            "endTime": day_end_ms(end),
            "userid": user_id.replace("-", ""),
        },
    )
    records = parse(text)
    return {"count": len(records), "records": records}


@router.get("/stops")
async def stops(
    user_id: str,
    start: date | None = None,
    end: date | None = None,
    min_stay_seconds: int = 300,
):
    """Stops/parking for one device."""
    try:
        uid = str(UUID(user_id))
    except ValueError:
        raise HTTPException(422, "user_id is not a valid id")
    start = start or local_today()
    end = end or start
    text = await call(
        "POST",
        "/GetDataService.aspx",
        params={"method": "StayDetail", "mds": "{mds}"},
        data={
            "beginTime": day_ms(start),
            "endTime": day_end_ms(end),
            "userid": uid,
            "mapType": "GOOGLE",
            "filter": min_stay_seconds,
        },
    )
    records = []
    for r in parse(text):
        r.pop("olon", None)
        r.pop("olat", None)
        if "lon" in r:
            r["lng"] = r.pop("lon")
        r["duration_s"] = stay_seconds(r.get("stopCar"))
        records.append(r)
    await add_addresses(records)
    return {"count": len(records), "records": records}
