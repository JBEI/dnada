from pandas import read_json
from sqlalchemy.orm import Session

from dnada.crud.base import CRUDBaseDesign
from dnada.models.synth import Synth
from dnada.schemas.synth import SynthCreate, SynthUpdate


class CRUDSynth(CRUDBaseDesign[Synth, SynthCreate, SynthUpdate]):

    """CRUD Methods for Synths"""

    def format_json(
        self, db: Session, *, raw_json: str, owner_id: int, design_id: int
    ) -> str:
        synths = read_json(raw_json).rename(
            columns={
                "ID Number": "j5_synth_id",
                "Name": "name",
                "Length": "length",
                "Cost": "cost",
                "Sequence": "sequence",
            }
        )
        synths["owner_id"] = owner_id
        synths["design_id"] = design_id
        return synths.loc[
            :,
            [
                "j5_synth_id",
                "name",
                "length",
                "cost",
                "sequence",
                "owner_id",
                "design_id",
            ],
        ].to_json()


synth = CRUDSynth(Synth)
