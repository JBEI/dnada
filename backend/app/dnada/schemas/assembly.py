from typing import Optional

from pydantic import BaseModel


# Shared properties
class AssemblyBase(BaseModel):
    j5_assembly_id: Optional[int] = None
    name: Optional[str] = None
    assembly_method: Optional[str] = None
    bin: Optional[int] = None


# Properties to receive on item creation
class AssemblyCreate(AssemblyBase):
    j5_assembly_id: int
    name: str
    assembly_method: str
    bin: int


# Properties to receive on item update
class AssemblyUpdate(AssemblyBase):
    pass


# Properties shared by models stored in DB
class AssemblyInDBBase(AssemblyCreate):
    id: int
    owner_id: int
    design_id: int
    construct_id: int
    part_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Assembly(AssemblyInDBBase):
    pass


# Properties properties stored in DB
class AssemblyInDB(AssemblyInDBBase):
    pass
