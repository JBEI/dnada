from typing import Optional

from pydantic import BaseModel


# Shared properties
class ResultZipBase(BaseModel):
    data: Optional[str] = None


# Properties to receive on item creation
class ResultZipCreate(ResultZipBase):
    data: str


# Properties to receive on item update
class ResultZipUpdate(ResultZipBase):
    pass


# Properties shared by models stored in DB
class ResultZipInDBBase(ResultZipCreate):
    id: int
    owner_id: int
    experiment_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class ResultZip(ResultZipInDBBase):
    pass


# Properties properties stored in DB
class ResultZipInDB(ResultZipInDBBase):
    pass
