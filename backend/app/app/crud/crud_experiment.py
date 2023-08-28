from app.crud.base import CRUDBaseOwner
from app.models.experiment import Experiment
from app.schemas.experiment import ExperimentCreate, ExperimentUpdate


class CRUDExperiment(CRUDBaseOwner[Experiment, ExperimentCreate, ExperimentUpdate]):

    """CRUD Methods for Experiments"""


experiment = CRUDExperiment(Experiment)
