from typing import Optional

from pydantic import BaseModel


# Shared properties
class PartBase(BaseModel):
    j5_part_id: Optional[int] = None
    name: Optional[str] = None
    part_type: Optional[str] = None
    type_id: Optional[int] = None
    relative_overlap: Optional[int] = None
    extra_5p_bps: Optional[int] = None
    extra_3p_bps: Optional[int] = None
    overlap_with_next: Optional[str] = None
    overlap_with_next_rc: Optional[str] = None
    sequence_length: Optional[int] = None
    sequence: Optional[str] = None


# Properties to receive on item creation
class PartCreate(PartBase):
    j5_part_id: int
    name: str
    part_type: str
    type_id: int
    relative_overlap: int
    extra_5p_bps: int
    extra_3p_bps: int
    overlap_with_next: str
    overlap_with_next_rc: str
    sequence_length: int
    sequence: str


# Properties to receive on item update
class PartUpdate(PartBase):
    pass


# Properties shared by models stored in DB
class PartInDBBase(PartCreate):
    id: int
    owner_id: int
    design_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Part(PartInDBBase):
    pass


# Properties properties stored in DB
class PartInDB(PartInDBBase):
    pass
