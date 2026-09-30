from datetime import date
from typing import Any

from pydantic import BaseModel, Field

class Record(BaseModel):
    """Base record model - actual fields depend on endpoint."""
    lat: float | None = None
    lng: float | None = None
    speed: float | None = None
    heading: float | None = None
    odometer_km: float | None = None
    address: str = ""
    sys_time: str | None = None
    datetime: str | None = None
    heart_time: str | None = None
    server_time: str | None = None

    class Config:
        extra = "allow"


class Response(BaseModel):
    """Standard response wrapper."""
    count: int
    records: list[dict[str, Any]]


class LiveAllResponse(Response):
    """Response for /live/all."""
    pass


class LiveResponse(Response):
    """Response for /live."""
    pass


class StopsResponse(Response):
    """Response for /reports/stops."""
    pass


class MileageRequest(BaseModel):
    """Request model for mileage reports."""
    start: date | None = None
    end: date | None = None


class DailyMileageRequest(MileageRequest):
    """Request model for daily mileage."""
    user_id: str


class StopsRequest(BaseModel):
    """Request model for stops report."""
    user_id: str
    start: int | None = None
    end: int | None = None
    min_stay_seconds: int = 300


class AddressRequest(BaseModel):
    """Request model for address lookup."""
    lat: float
    lng: float


class AddressResponse(BaseModel):
    """Response for /address."""
    address: str
