from pydantic import BaseModel

class LocationRequest(BaseModel):
    location: str

class CoordinatesRequest(BaseModel):
    latitude: float
    longitude: float

class BlynkRequest(BaseModel):
    pin: str
    value: str
