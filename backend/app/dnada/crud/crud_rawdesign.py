from dnada.crud.base import CRUDBaseDesign
from dnada.models.rawdesign import RawDesign
from dnada.schemas.rawdesign import RawDesignCreate, RawDesignUpdate


class CRUDRawDesign(CRUDBaseDesign[RawDesign, RawDesignCreate, RawDesignUpdate]):

    """CRUD Methods for RawDesigns"""


rawdesign = CRUDRawDesign(RawDesign)
