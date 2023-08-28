from dnada.crud.base import CRUDBaseOwner
from dnada.models.experiment import Experiment
from dnada.schemas.experiment import ExperimentCreate, ExperimentUpdate


class CRUDExperiment(CRUDBaseOwner[Experiment, ExperimentCreate, ExperimentUpdate]):

    """CRUD Methods for Experiments"""


experiment = CRUDExperiment(Experiment)
