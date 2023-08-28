from app.crud.base import CRUDBaseDesign
from app.models.rawdesign import RawDesign
from app.schemas.rawdesign import RawDesignCreate, RawDesignUpdate


class CRUDRawDesign(CRUDBaseDesign[RawDesign, RawDesignCreate, RawDesignUpdate]):

    """CRUD Methods for RawDesigns"""


rawdesign = CRUDRawDesign(RawDesign)
