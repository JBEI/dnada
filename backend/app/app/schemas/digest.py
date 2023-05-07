from typing import Optional

from pydantic import BaseModel


# Shared properties
class DigestBase(BaseModel):
    j5_digest_id: Optional[int] = None
    source: Optional[str] = None
    length: Optional[int] = None
    sequence: Optional[str] = None


# Properties to receive on item creation
class DigestCreate(DigestBase):
    j5_digest_id: int
    source: str
    length: int
    sequence: str


# Properties to receive on item update
class DigestUpdate(DigestBase):
    pass


# Properties shared by models stored in DB
class DigestInDBBase(DigestBase):
    id: int
    j5_digest_id: int
    source: str
    length: int
    sequence: str
    owner_id: int
    part_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Digest(DigestInDBBase):
    pass


# Properties properties stored in DB
class DigestInDB(DigestInDBBase):
    pass
