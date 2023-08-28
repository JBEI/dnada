from typing import Optional

from pydantic import BaseModel


# Shared properties
class BannerBase(BaseModel):
    text: Optional[str] = None


# Properties to receive on item creation
class BannerCreate(BannerBase):
    text: str


# Properties to receive on item update
class BannerUpdate(BannerBase):
    pass


# Properties shared by models stored in DB
class BannerInDBBase(BannerCreate):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Banner(BannerInDBBase):
    pass


# Properties properties stored in DB
class BannerInDB(BannerInDBBase):
    pass
