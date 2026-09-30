from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from app.client import add_addresses, call, parse, to_dicts

router = APIRouter(prefix="/live", tags=["live"])


@router.get("/all")
async def live_all(address: bool = False):
    """Get all devices, live data."""
    text = await call(
        "GET",
        "/TrackService.aspx",
        params={
            "method": "getUserAndGPSInfoUtc",
            "school_id": "{cust}",
            "custid": "{cust}",
            "mds": "{mds}",
            "mapType": "GOOGLE",
            "callback": "DFRAME.selectCustBack",
            "custTreeCheck": "false",
            "option": "en",
            "Selected": "device",
            "currentid": "{cust}",
        },
    )
    records = to_dicts(parse(text))
    if address:
        await add_addresses(records)
    return {"count": len(records), "records": records}


@router.get("/")
async def live(
    user_ids: Annotated[str, Query(description="comma separated user_ids")],
    address: bool = False,
):
    """Get specific devices, live data."""
    ids = [i for i in user_ids.split(",") if i]
    records = []
    for i in range(0, len(ids), 500):
        text = await call(
            "POST",
            "/TrackService.aspx",
            params={"method": "getUserAndGPSInfoUtcByIds"},
            data={
                "school_id": "{cust}",
                "custid": "{cust}",
                "user_ids": ",".join(ids[i:i + 500]),
                "mds": "{mds}",
                "mapType": "GOOGLE",
                "option": "en",
                "Selected": "device",
                "currentid": "{cust}",
                "update": "1",
            },
        )
        records += to_dicts(parse(text))
    if address:
        await add_addresses(records)
    return {"count": len(records), "records": records}
