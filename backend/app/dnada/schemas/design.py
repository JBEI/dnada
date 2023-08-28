from typing import Optional

from pydantic import BaseModel


# Shared properties
class DesignBase(BaseModel):
    name: Optional[str] = None
    zip_file_name: Optional[str] = None
    description: Optional[str] = None
    condensed: Optional[bool] = None


# Properties to receive on item creation
class DesignCreate(DesignBase):
    name: str
    zip_file_name: str
    condensed: bool


# Properties to receive on item update
class DesignUpdate(DesignBase):
    pass


# Properties shared by models stored in DB
class DesignInDBBase(DesignCreate):
    id: int
    owner_id: int
    experiment_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Design(DesignInDBBase):
    pass


# Properties properties stored in DB
class DesignInDB(DesignInDBBase):
    pass
