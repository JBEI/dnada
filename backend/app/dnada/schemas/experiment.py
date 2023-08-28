from typing import Optional

from pydantic import BaseModel


# Shared properties
class ExperimentBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Properties to receive on item creation
class ExperimentCreate(ExperimentBase):
    name: str


# Properties to receive on item update
class ExperimentUpdate(ExperimentBase):
    pass


# Properties shared by models stored in DB
class ExperimentInDBBase(ExperimentCreate):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Experiment(ExperimentInDBBase):
    pass


# Properties properties stored in DB
class ExperimentInDB(ExperimentInDBBase):
    pass
