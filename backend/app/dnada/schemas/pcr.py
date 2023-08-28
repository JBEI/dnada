from typing import Optional

from pydantic import BaseModel


# Shared properties
class PCRBase(BaseModel):
    j5_pcr_id: Optional[int] = None
    note: Optional[str] = None
    mean_oligo_temp: Optional[float] = None
    delta_oligo_temp: Optional[float] = None
    mean_oligo_temp_3p: Optional[float] = None
    delta_oligo_temp_3p: Optional[float] = None
    length: Optional[int] = None
    sequence: Optional[str] = None


# Properties to receive on item creation
class PCRCreate(PCRBase):
    j5_pcr_id: int
    note: str
    mean_oligo_temp: float
    delta_oligo_temp: float
    mean_oligo_temp_3p: float
    delta_oligo_temp_3p: float
    length: int
    sequence: str


# Properties to receive on item update
class PCRUpdate(PCRBase):
    pass


# Properties shared by models stored in DB
class PCRInDBBase(PCRCreate):
    id: int
    owner_id: int
    part_id: int
    template_id: int
    forward_oligo_id: int
    reverse_oligo_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class PCR(PCRInDBBase):
    pass


# Properties properties stored in DB
class PCRInDB(PCRInDBBase):
    pass
