from app.crud.base import CRUDBaseExperiment
from app.models.design import Design
from app.schemas.design import DesignCreate, DesignUpdate


class CRUDDesign(CRUDBaseExperiment[Design, DesignCreate, DesignUpdate]):

    """CRUD Methods for Designs"""


design = CRUDDesign(Design)
