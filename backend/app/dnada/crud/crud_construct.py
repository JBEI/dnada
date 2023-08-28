from pandas import read_json
from sqlalchemy.orm import Session

from dnada.crud.base import CRUDBaseDesign
from dnada.models.construct import Construct
from dnada.schemas.construct import ConstructCreate, ConstructUpdate


class CRUDConstruct(CRUDBaseDesign[Construct, ConstructCreate, ConstructUpdate]):

    """CRUD Methods for Constructs"""

    def format_json(
        self, db: Session, *, raw_json: str, owner_id: int, design_id: int
    ) -> str:
        constructs = read_json(raw_json).rename(
            columns={
                "name": "name",
                "filename": "filename",
                "genbank": "genbank",
                "j5_construct_id": "j5_construct_id",
                "assembly_method": "assembly_method",
            }
        )
        constructs["owner_id"] = owner_id
        constructs["design_id"] = design_id
        return constructs.loc[
            :,
            [
                "name",
                "genbank",
                "j5_construct_id",
                "assembly_method",
                "owner_id",
                "design_id",
            ],
        ].to_json()


construct = CRUDConstruct(Construct)
