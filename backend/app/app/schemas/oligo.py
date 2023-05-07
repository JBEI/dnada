from typing import Optional

from pydantic import BaseModel


# Shared properties
class OligoBase(BaseModel):
    j5_oligo_id: Optional[int] = None
    name: Optional[str] = None
    length: Optional[int] = None
    tm: Optional[float] = None
    tm_3p: Optional[float] = None
    cost: Optional[float] = None
    sequence: Optional[str] = None
    sequence_3p: Optional[str] = None


# Properties to receive on item creation
class OligoCreate(OligoBase):
    j5_oligo_id: int
    name: str
    length: int
    tm: float
    tm_3p: float
    cost: float
    sequence: str
    sequence_3p: str


# Properties to receive on item update
class OligoUpdate(OligoBase):
    pass


# Properties shared by models stored in DB
class OligoInDBBase(OligoBase):
    id: int
    j5_oligo_id: int
    name: str
    length: int
    tm: float
    tm_3p: float
    cost: float
    sequence: str
    sequence_3p: str
    owner_id: int
    design_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Oligo(OligoInDBBase):
    pass


# Properties properties stored in DB
class OligoInDB(OligoInDBBase):
    pass
