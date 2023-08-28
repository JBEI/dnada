from typing import Optional

from pydantic import BaseModel


# Shared properties
class RawDesignBase(BaseModel):
    name: Optional[str] = None
    data: Optional[dict] = None


# Properties to receive on item creation
class RawDesignCreate(RawDesignBase):
    name: str
    data: dict


# Properties to receive on item update
class RawDesignUpdate(RawDesignBase):
    pass


# Properties shared by models stored in DB
class RawDesignInDBBase(RawDesignCreate):
    id: int
    owner_id: int
    design_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class RawDesign(RawDesignInDBBase):
    pass


# Properties properties stored in DB
class RawDesignInDB(RawDesignInDBBase):
    pass
