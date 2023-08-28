from typing import Optional

from pydantic import BaseModel


# Shared properties
class WorkflowStepBase(BaseModel):
    name: Optional[str] = None
    number: Optional[int] = None
    title: Optional[str] = None
    status: Optional[str] = None


# Properties to receive on item creation
class WorkflowStepCreate(WorkflowStepBase):
    name: str
    number: int
    title: str
    status: str


# Properties to receive on item update
class WorkflowStepUpdate(WorkflowStepBase):
    pass


# Properties shared by models stored in DB
class WorkflowStepInDBBase(WorkflowStepCreate):
    id: int
    owner_id: int
    workflow_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class WorkflowStep(WorkflowStepInDBBase):
    pass


# Properties properties stored in DB
class WorkflowStepInDB(WorkflowStepInDBBase):
    pass
