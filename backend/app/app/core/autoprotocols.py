import json
import typing as t
from autoprotocol.protocol import Protocol, Container
from autoprotocol.types import protocol
from autoprotocol.liquid_handle import Transfer
from pandera.typing import DataFrame

from app import schemas


# Extending the existing Protocol class.
class CustomProtocol(Protocol):  # type: ignore
    def genesynthesize(self, genes: list[dict[str, t.Any]]) -> "Protocol":
        """
        Add a gene synthesis instruction to the protocol.

        Parameters
        ----------
        genes: List[dict]
            List of dictionaries describing the genes to synthesize.

        Returns
        -------
        self
            The protocol instance.
        """
        instruction = {"op": "genesynthesize", "genes": genes}
        self.instructions.append(instruction)
        return self


def order_genes(synths_order_form_384: DataFrame[schemas.SynthsPlateSchema]) -> str:
    """Create autoprotocol for gene synthesis"""
    p = CustomProtocol()
    synthesis_plate_names: list[str] = (
        synths_order_form_384["PLATE ID"].unique().tolist()
    )
    synthesis_plates: dict[str, Container] = {
        synthesis_plate_name: p.ref(
            synthesis_plate_name, id=None, cont_type="384-echo", storage="cold_20"
        )
        for synthesis_plate_name in synthesis_plate_names
    }
    synthesis_objects: list[dict[str, t.Any]] = [
        {
            "sequence": seq,
            "destination": synthesis_plates[plate].well(well),
            "scale": "1ug",
        }
        for seq, plate, well in zip(
            synths_order_form_384.SEQUENCE,
            synths_order_form_384["PLATE ID"],
            synths_order_form_384["PLATE WELL"],
        )
    ]
    p.genesynthesize(synthesis_objects)
    for plate in synthesis_plates:
        p.seal(synthesis_plates[plate], type="foil", mode="adhesive")

    return json.dumps(p.as_dict(), indent=2)


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


def setup_templates_plate(
    templates_plate: DataFrame[schemas.TemplatesPlateSchema],
    synths_plate: DataFrame[schemas.SynthsPlateSchema],
) -> str:
    """Create autoprotocol for setting up templates plate"""
    p = Protocol()
    synthesis_plate_names: list[str] = synths_plate["PLATE ID"].unique().tolist()
    synthesis_plates: dict[str, Container] = {
        synthesis_plate_name: p.ref(
            synthesis_plate_name,
            id=synthesis_plate_name,
            cont_type="384-echo",
            storage="cold_20",
        )
        for synthesis_plate_name in synthesis_plate_names
    }
    for plate in synthesis_plates:
        p.unseal(synthesis_plates[plate])

    template_plate_names: list[str] = templates_plate["PLATE ID"].unique().tolist()
    template_plates: dict[str, Container] = {
        template_plate_name: p.ref(
            template_plate_name, id=None, cont_type="384-echo", storage="cold_20"
        )
        for template_plate_name in template_plate_names
    }

    for _, template in templates_plate.iterrows():
        synth_template = synths_plate["LIQUID TYPE"].isin([template["LIQUID TYPE"]])
        if synth_template.any():
            synth_sample = synths_plate.loc[synth_template, :].squeeze()
            p.transfer(
                source=synthesis_plates[synth_sample["PLATE ID"]].well(
                    synth_sample["PLATE WELL"]
                ),
                destination=template_plates[template["PLATE ID"]].well(
                    template["PLATE WELL"]
                ),
                volume="50:microliters",
                method=Transfer(
                    blowout=False,
                    prime=False,
                    transit=False,
                    mix_before=False,
                    mix_after=False,
                ),
            )
        else:
            template_tube = p.ref(
                template["LIQUID TYPE"], cont_type="micro-1.5", storage="cold_20"
            )
            p.transfer(
                source=template_tube.well(0),
                destination=template_plates[template["PLATE ID"]].well(
                    template["PLATE WELL"]
                ),
                volume="50:microliter",
                method=Transfer(
                    blowout=False,
                    prime=False,
                    transit=False,
                    mix_before=False,
                    mix_after=False,
                ),
            )

    for plate in synthesis_plates:
        p.seal(synthesis_plates[plate])
    for plate in template_plates:
        p.seal(template_plates[plate])

    return json.dumps(p.as_dict(), indent=2)
