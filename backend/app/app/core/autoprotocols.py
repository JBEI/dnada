import json
from autoprotocol.protocol import Protocol, Container
from autoprotocol.types import protocol
from pandera.typing import DataFrame

from app import schemas


def order_oligos(oligos_order_form_384: DataFrame[schemas.OligosOrderSchema]) -> str:
    """Create autoprotocol for oligo synthesis"""
    p = Protocol()
    oligo_plate_names: list[str] = oligos_order_form_384.Plate.unique().tolist()
    oligo_plates: dict[str, Container] = {
        oligo_plate_name: p.ref(
            oligo_plate_name, id=None, cont_type="384-echo", storage="cold_20"
        )
        for oligo_plate_name in oligo_plate_names
    }
    oligo_objects: list[protocol.OligosynthesizeOligo] = [
        {
            "sequence": seq,
            "destination": oligo_plates[plate].well(well),
            "scale": "25nm",
            "purification": "standard",
        }
        for seq, plate, well in zip(
            oligos_order_form_384.Sequence,
            oligos_order_form_384.Plate,
            oligos_order_form_384["Well Position"],
        )
    ]
    p.oligosynthesize(oligo_objects)
    for plate in oligo_plates:
        p.seal(oligo_plates[plate], type="foil", mode="adhesive")

    return json.dumps(p.as_dict(), indent=2)
