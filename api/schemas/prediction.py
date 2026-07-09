from typing import Optional

from pydantic import BaseModel


class PropertyInput(BaseModel):
    property_type: str
    city: str
    province: str

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    property_state: Optional[str] = None
    build_year: Optional[int] = None

    bedroom_count: Optional[int] = None
    livable_surface: Optional[float] = None
    total_surface: Optional[float] = None

    garage: Optional[int] = 0
    terrace: Optional[int] = 0
    swimming_pool: Optional[int] = 0

    energy_consumption: Optional[float] = None

    preschool_distance: Optional[float] = None
    train_station_distance: Optional[float] = None
    supermarket_distance: Optional[float] = None

    nearest_city: Optional[str] = None
    nearest_city_distance: Optional[float] = None