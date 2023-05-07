from app.crud.base import CRUDBaseWorkflow
from app.models.plate import Plate
from app.schemas.plate import PlateCreate, PlateUpdate


class CRUDPlate(CRUDBaseWorkflow[Plate, PlateCreate, PlateUpdate]):

    """CRUD Methods for Plates"""


plate = CRUDPlate(Plate)
