from pandas import read_json
from sqlalchemy.orm import Session

from app.crud.base import CRUDBaseDesign
from app.models.part import Part
from app.schemas.part import PartCreate, PartUpdate


class CRUDPart(CRUDBaseDesign[Part, PartCreate, PartUpdate]):

    """CRUD Methods for Parts"""

    def format_json(
        self, db: Session, *, raw_json: str, owner_id: int, design_id: int
    ) -> str:
        parts = read_json(raw_json).rename(
            columns={
                "ID Number": "j5_part_id",
                "Part(s)": "name",
                "Type": "part_type",
                "Type ID Number": "type_id",
                "Relative Overlap Position": "relative_overlap",
                "Extra 5' CPEC bps": "extra_5p_bps",
                "Extra 3' CPEC bps": "extra_3p_bps",
                "Overlap with Next": "overlap_with_next",
                "Overlap with Next Reverse Complemenet": "overlap_with_next_rc",
                "Sequence Length": "sequence_length",
                "Sequence": "sequence",
            }
        )
        parts["owner_id"] = owner_id
        parts["design_id"] = design_id
        return parts.loc[
            :,
            [
                "j5_part_id",
                "name",
                "part_type",
                "type_id",
                "relative_overlap",
                "extra_5p_bps",
                "extra_3p_bps",
                "overlap_with_next",
                "overlap_with_next_rc",
                "sequence_length",
                "sequence",
                "owner_id",
                "design_id",
            ],
        ].to_json()


part = CRUDPart(Part)
