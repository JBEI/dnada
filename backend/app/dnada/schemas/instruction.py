from typing import Optional

from pydantic import BaseModel


# Shared properties
class InstructionBase(BaseModel):
    category: Optional[str] = None
    trial: Optional[int] = None
    data: Optional[str] = None


# Properties to receive on item creation
class InstructionCreate(InstructionBase):
    category: str
    trial: int
    data: str


# Properties to receive on item update
class InstructionUpdate(InstructionBase):
    pass


# Properties shared by models stored in DB
class InstructionInDBBase(InstructionCreate):
    id: int
    owner_id: int
    workflow_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Instruction(InstructionInDBBase):
    pass


# Properties properties stored in DB
class InstructionInDB(InstructionInDBBase):
    pass
