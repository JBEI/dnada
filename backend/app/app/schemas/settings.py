from pydantic import BaseModel

from app.api.utils.pydantic_form_decorator import as_form

# @as_form is decorator used to enable pydantic validation of
# multipart form data


@as_form
class AssemblyRunSettings(BaseModel):
    manual: bool
    workflowID: int


@as_form
class SequencingRunSettings(BaseModel):
    manual: bool
    workflowID: int
