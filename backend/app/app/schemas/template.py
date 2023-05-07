from typing import Optional

from pydantic import BaseModel


# Shared properties
class TemplateBase(BaseModel):
    j5_template_id: Optional[int] = None
    name: Optional[str] = None


# Properties to receive on item creation
class TemplateCreate(TemplateBase):
    j5_template_id: int
    name: str


# Properties to receive on item update
class TemplateUpdate(TemplateBase):
    pass


# Properties shared by models stored in DB
class TemplateInDBBase(TemplateCreate):
    id: int
    owner_id: int
    design_id: int
    synth_id: Optional[int] = None

    class Config:
        orm_mode = True


# Properties to return to client
class Template(TemplateInDBBase):
    pass


# Properties properties stored in DB
class TemplateInDB(TemplateInDBBase):
    pass
