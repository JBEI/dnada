from typing import Optional

from pydantic import BaseModel


# Shared properties
class WellBase(BaseModel):
    location: Optional[str] = None
    volume: Optional[float] = None
    well_type: Optional[str] = None


# Properties to receive on item creation
class WellCreate(WellBase):
    location: str
    volume: float
    well_type: str


# Properties to receive on item update
class WellUpdate(WellBase):
    pass


# Properties shared by models stored in DB
class WellInDBBase(WellCreate):
    id: int
    owner_id: int
    plate_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Well(WellInDBBase):
    pass


# Properties stored in DB
class WellInDB(WellInDBBase):
    pass


# WellWithLiquid
class WellWithLiquidInDBBase(WellCreate):
    id: int
    owner_id: int
    plate_id: int
    content_id: int

    class Config:
        orm_mode = True


# OligoWell
# Properties to return to client
class OligoWell(WellWithLiquidInDBBase):
    pass


# Properties stored in DB
class OligoWellInDB(WellWithLiquidInDBBase):
    pass


# OligoOrder96Well
# Properties to return to client
class OligoOrder96Well(WellWithLiquidInDBBase):
    pass


# Properties stored in DB
class OligoOrder96WellInDB(WellWithLiquidInDBBase):
    pass


# DigestWell
# Properties to return to client
class DigestWell(WellWithLiquidInDBBase):
    pass


# Properties stored in DB
class DigestWellInDB(WellWithLiquidInDBBase):
    pass


# SynthWell
# Properties to return to client
class SynthWell(WellWithLiquidInDBBase):
    pass


# Properties stored in DB
class SynthWellInDB(WellWithLiquidInDBBase):
    pass


# PCRWell
# Properties to return to client
class PCRWell(WellWithLiquidInDBBase):
    pass


# Properties stored in DB
class PCRWellInDB(WellWithLiquidInDBBase):
    pass


# TemplateWell
# Properties to return to client
class TemplateWell(WellWithLiquidInDBBase):
    pass


# Properties stored in DB
class TemplateWellInDB(WellWithLiquidInDBBase):
    pass


# PartWell
# Properties to return to client
class PartWell(WellWithLiquidInDBBase):
    pass


# Properties stored in DB
class PartWellInDB(WellWithLiquidInDBBase):
    pass
