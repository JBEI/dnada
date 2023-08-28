from dnada.crud.base import CRUDBaseInstruction
from dnada.models.run import Run
from dnada.schemas.run import RunCreate, RunUpdate


class CRUDRun(CRUDBaseInstruction[Run, RunCreate, RunUpdate]):

    """CRUD Methods for Runs"""


run = CRUDRun(Run)
