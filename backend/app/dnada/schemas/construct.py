from typing import Optional

from pydantic import BaseModel


# Shared properties
class ConstructBase(BaseModel):
    name: Optional[str] = None
    genbank: Optional[str] = None
    j5_construct_id: Optional[int] = None
    assembly_method: Optional[str] = None
    jbx: Optional[str] = None


# Properties to receive on item creation
class ConstructCreate(ConstructBase):
    name: str
    genbank: str
    j5_construct_id: int
    assembly_method: str


# Properties to receive on item update
class ConstructUpdate(ConstructBase):
    pass


# Properties shared by models stored in DB
class ConstructInDBBase(ConstructCreate):
    id: int
    owner_id: int
    design_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Construct(ConstructInDBBase):
    pass


# Properties properties stored in DB
class ConstructInDB(ConstructInDBBase):
    pass
