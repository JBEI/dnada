from typing import Optional

from pydantic import BaseModel


# Shared properties
class RunBase(BaseModel):
    date: Optional[str] = None
    instrument: Optional[str] = None
    raw_data: Optional[str] = None
    run_type: Optional[str] = None


# Properties to receive on item creation
class RunCreate(RunBase):
    date: str
    instrument: str
    raw_data: str
    run_type: str


# Properties to receive on item update
class RunUpdate(RunBase):
    pass


# Properties shared by models stored in DB
class RunInDBBase(RunCreate):
    id: int
    owner_id: int
    # workflow_id: int
    instruction_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Run(RunInDBBase):
    pass


# Properties properties stored in DB
class RunInDB(RunInDBBase):
    pass
