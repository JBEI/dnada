from typing import Optional

from pydantic import BaseModel


# Shared properties
class WorkflowBase(BaseModel):
    created_time: Optional[str] = None


# Properties to receive on item creation
class WorkflowCreate(WorkflowBase):
    created_time: str


# Properties to receive on item update
class WorkflowUpdate(WorkflowBase):
    pass


# Properties shared by models stored in DB
class WorkflowInDBBase(WorkflowCreate):
    id: int
    owner_id: int
    experiment_id: int
    design_id: int
    resultzip_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Workflow(WorkflowInDBBase):
    pass


# Properties properties stored in DB
class WorkflowInDB(WorkflowInDBBase):
    pass
