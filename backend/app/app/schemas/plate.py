from typing import Optional

from pydantic import BaseModel


# Shared properties
class PlateBase(BaseModel):
    name: Optional[str] = None
    size: Optional[int] = None
    plate_type: Optional[str] = None
    raw_data: Optional[str] = None


# Properties to receive on item creation
class PlateCreate(PlateBase):
    name: str
    size: int
    plate_type: str
    raw_data: str


# Properties to receive on item update
class PlateUpdate(PlateBase):
    pass


# Properties shared by models stored in DB
class PlateInDBBase(PlateCreate):
    id: int
    owner_id: int
    workflow_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Plate(PlateInDBBase):
    pass


# Properties properties stored in DB
class PlateInDB(PlateInDBBase):
    pass
