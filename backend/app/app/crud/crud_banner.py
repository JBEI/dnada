from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.banner import Banner
from app.schemas.banner import BannerCreate, BannerUpdate


class CRUDBanner(CRUDBase[Banner, BannerCreate, BannerUpdate]):

    """CRUD Methods for Banner"""

    def get(self, db: Session) -> Banner:
        banner: Optional[Banner] = db.query(self.model).first()
        if not banner:
            return self.create(db=db, obj_in=BannerCreate(text=""))
        else:
            return banner


banner = CRUDBanner(Banner)
