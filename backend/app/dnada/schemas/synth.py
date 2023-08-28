from pydantic import BaseModel


# Shared properties
class SynthBase(BaseModel):
    j5_synth_id: int = None
    name: str = None
    length: int = None
    cost: float = None
    sequence: str = None


# Properties to receive on item creation
class SynthCreate(SynthBase):
    j5_synth_id: int
    name: str
    length: int
    cost: float
    sequence: str


# Properties to receive on item update
class SynthUpdate(SynthBase):
    pass


# Properties shared by models stored in DB
class SynthInDBBase(SynthBase):
    id: int
    j5_synth_id: int
    name: str
    length: int
    cost: float
    sequence: str
    owner_id: int
    design_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Synth(SynthInDBBase):
    pass


# Properties properties stored in DB
class SynthInDB(SynthInDBBase):
    pass
