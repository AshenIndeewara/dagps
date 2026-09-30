from fastapi import FastAPI

from app.routers import records, reports

app = FastAPI(
    title="DAGPS API",
    version="0.1.0",
    description="FastAPI wrapper for www.dagps.net",
)

app.include_router(records)
app.include_router(reports)

from fastapi import Query
from app.client import add_addresses

@app.get("/address")
async def address(lat: float = Query(...), lng: float = Query(...)):
    """Get address for coordinates."""
    rec = [{"lat": lat, "lng": lng}]
    await add_addresses(rec)
    return {"address": rec[0]["address"]}
