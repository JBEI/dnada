from dnada.crud.base import CRUDBaseWorkflow
from dnada.models.plate import Plate
from dnada.schemas.plate import PlateCreate, PlateUpdate


class CRUDPlate(CRUDBaseWorkflow[Plate, PlateCreate, PlateUpdate]):

    """CRUD Methods for Plates"""


plate = CRUDPlate(Plate)
