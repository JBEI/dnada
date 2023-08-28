from dnada.crud.base import CRUDBaseExperiment
from dnada.models.design import Design
from dnada.schemas.design import DesignCreate, DesignUpdate


class CRUDDesign(CRUDBaseExperiment[Design, DesignCreate, DesignUpdate]):

    """CRUD Methods for Designs"""


design = CRUDDesign(Design)
