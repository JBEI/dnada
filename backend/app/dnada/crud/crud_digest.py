from pandas import read_json
from sqlalchemy.orm import Session

from dnada.crud.base import CRUDBasePart
from dnada.models.digest import Digest
from dnada.models.part import Part
from dnada.schemas.digest import DigestCreate, DigestUpdate


class CRUDDigest(CRUDBasePart[Digest, DigestCreate, DigestUpdate]):

    """CRUD Methods for Digests"""

    def format_json(
        self, db: Session, *, raw_json: str, owner_id: int, design_id: int
    ) -> str:
        digests = read_json(raw_json).rename(
            columns={
                "ID Number": "j5_digest_id",
                "Sequence Source": "source",
                "Length": "length",
                "Sequence": "sequence",
            }
        )
        digests["owner_id"] = owner_id
        digests["design_id"] = design_id
        digests["part_id"] = digests.apply(
            lambda row: db.query(Part)
            .filter(
                Part.owner_id == row["owner_id"],
                Part.design_id == row["design_id"],
                Part.part_type == "Digest Linearized",
                Part.type_id == row["j5_digest_id"],
            )
            .one()
            .id,
            axis=1,
        )
        return digests.loc[
            :,
            [
                "j5_digest_id",
                "source",
                "length",
                "sequence",
                "owner_id",
                "part_id",
            ],
        ].to_json()


digest = CRUDDigest(Digest)
