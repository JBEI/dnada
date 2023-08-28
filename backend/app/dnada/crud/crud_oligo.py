from pandas import read_json
from sqlalchemy.orm import Session

from dnada.crud.base import CRUDBaseDesign
from dnada.models.oligo import Oligo
from dnada.schemas.oligo import OligoCreate, OligoUpdate


class CRUDOligo(CRUDBaseDesign[Oligo, OligoCreate, OligoUpdate]):

    """CRUD Methods for Oligos"""

    def format_json(
        self, db: Session, *, raw_json: str, owner_id: int, design_id: int
    ) -> str:
        oligos = read_json(raw_json).rename(
            columns={
                "ID Number": "j5_oligo_id",
                "Name": "name",
                "Length": "length",
                "Tm": "tm",
                "Tm (3' only)": "tm_3p",
                "Cost": "cost",
                "Sequence": "sequence",
                "Sequence (3' only)": "sequence_3p",
            }
        )
        oligos["owner_id"] = owner_id
        oligos["design_id"] = design_id
        return oligos.loc[
            :,
            [
                "j5_oligo_id",
                "name",
                "length",
                "tm",
                "tm_3p",
                "cost",
                "sequence",
                "sequence_3p",
                "owner_id",
                "design_id",
            ],
        ].to_json()


oligo = CRUDOligo(Oligo)
