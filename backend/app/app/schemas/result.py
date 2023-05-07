from typing import Optional

from pydantic import BaseModel


# Shared properties
class ResultBase(BaseModel):
    result_type: Optional[str] = None


# Properties to receive on item creation
class ResultCreate(ResultBase):
    result_type: str


# Properties to receive on item update
class ResultUpdate(ResultBase):
    pass


# Properties shared by models stored in DB
class ResultInDBBase(ResultCreate):
    id: int
    owner_id: int
    run_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Result(ResultInDBBase):
    pass


# Properties stored in DB
class ResultInDB(ResultInDBBase):
    pass


# ResultWithSample
class ResultWithSampleInDBBase(ResultCreate):
    id: int
    owner_id: int
    run_id: int
    sample_id: int

    class Config:
        orm_mode = True


# PCR Result
# Shared properties
class PCRResultBase(BaseModel):
    result_type: Optional[str] = None
    polymerase: Optional[str] = None
    good: Optional[bool] = None


# Properties to receive on item creation
class PCRResultCreate(PCRResultBase):
    result_type: str
    polymerase: str
    good: bool


# Properties to receive on item update
class PCRResultUpdate(PCRResultBase):
    pass


# Properties shared by models stored in DB
class PCRResultInDBBase(PCRResultCreate):
    id: int
    owner_id: int
    run_id: int
    sample_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class PCRResult(PCRResultInDBBase):
    pass


# Properties stored in DB
class PCRResultInDB(PCRResultInDBBase):
    pass


# Assembly Result
# Shared properties
class AssemblyResultBase(BaseModel):
    result_type: Optional[str] = None
    colonies: Optional[bool] = None


# Properties to receive on item creation
class AssemblyResultCreate(AssemblyResultBase):
    result_type: str
    colonies: bool


# Properties to receive on item update
class AssemblyResultUpdate(AssemblyResultBase):
    pass


# Properties shared by models stored in DB
class AssemblyResultInDBBase(AssemblyResultCreate):
    id: int
    owner_id: int
    run_id: int
    sample_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class AssemblyResult(AssemblyResultInDBBase):
    pass


# Properties stored in DB
class AssemblyResultInDB(AssemblyResultInDBBase):
    pass


# Sequencing Result
# Shared properties
class SequencingResultBase(BaseModel):
    result_type: Optional[str] = None
    sequencing: Optional[bool] = None


# Properties to receive on item creation
class SequencingResultCreate(SequencingResultBase):
    result_type: str
    sequencing: bool


# Properties to receive on item update
class SequencingResultUpdate(SequencingResultBase):
    pass


# Properties shared by models stored in DB
class SequencingResultInDBBase(SequencingResultCreate):
    id: int
    owner_id: int
    run_id: int
    sample_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class SequencingResult(SequencingResultInDBBase):
    pass


# Properties stored in DB
class SequencingResultInDB(SequencingResultInDBBase):
    pass
