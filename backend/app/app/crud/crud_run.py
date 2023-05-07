from app.crud.base import CRUDBaseInstruction
from app.models.run import Run
from app.schemas.run import RunCreate, RunUpdate


class CRUDRun(CRUDBaseInstruction[Run, RunCreate, RunUpdate]):

    """CRUD Methods for Runs"""


run = CRUDRun(Run)
