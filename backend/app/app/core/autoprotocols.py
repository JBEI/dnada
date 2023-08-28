import json
import typing as t
from autoprotocol.protocol import Protocol, Container
from autoprotocol.types import protocol
from autoprotocol.liquid_handle import Transfer
from autoprotocol.builders import DispenseBuilders
from autoprotocol.container_type import ContainerType
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

    def pick(self, colonies: list[dict[str, t.Any]]) -> "Protocol":
        """
        Add a colony picking instruction to the protocol.

        Parameters
        ----------
        colonies: List[dict]
            List of dictionaries describing the colonies to pick.

        Returns
        -------
        self
            The protocol instance.
        """
        instruction = {"op": "pickcolony", "colonies": colonies}
        self.instructions.append(instruction)
        return self


agar_qplate = ContainerType(
    name="48-well Agar Plate",
    well_count=48,
    well_depth_mm=None,
    well_volume_ul="300:microliter",
    well_coating=None,
    sterile=True,
    is_tube=False,
    cover_types=["universal"],
    seal_types=None,
    capabilities=[
        "liquid_handle",
        "incubate",
        "cover",
        "dispense",
        "liquid_handle",
        "provision",
    ],
    shortname="48-agar-plate",
    col_count=6,
    dead_volume_ul="1:microliter",
    safe_min_volume_ul="5:microliter",
    true_max_vol_ul="500:microliter",
)


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


def perform_pcrs(
    echo_instructions: DataFrame[schemas.EchoInstructionsSchema],
    thermocycler_instructions: DataFrame[schemas.PCRThermocyclerSchema],
) -> str:
    """Create autoprotocol for performing PCRs"""
    p = Protocol()
    source_plate_names: list[str] = (
        echo_instructions["Source Plate Name"].unique().tolist()
    )
    source_plates: dict[str, Container] = {
        source_plate_name: p.ref(
            source_plate_name,
            id=source_plate_name,
            cont_type="384-echo",
            storage="cold_20",
        )
        for source_plate_name in source_plate_names
    }
    pcr_plate_names: list[str] = (
        echo_instructions["Destination Plate Name"].unique().tolist()
    )
    pcr_plates: dict[str, Container] = {
        pcr_plate_name: p.ref(
            pcr_plate_name, id=None, cont_type="96-pcr", storage="cold_20"
        )
        for pcr_plate_name in pcr_plate_names
    }

    for plate in source_plates:
        p.unseal(source_plates[plate])

    for _, instruction in echo_instructions.iterrows():
        p.acoustic_transfer(
            source=source_plates[instruction["Source Plate Name"]].well(
                instruction["Source Well"]
            ),
            dest=pcr_plates[instruction["Destination Plate Name"]].well(
                instruction["Destination Well"]
            ),
            volume=f'{instruction["Transfer Volume"]}:nanoliter',
            droplet_size="2.5:nanoliter",
        )

    for plate in source_plates:
        p.seal(source_plates[plate])

    for plate in pcr_plates:
        # Dispense master mix only to columns that have a reaction
        # TODO: use mantis to dispense master mix only to wells that have reaction
        columns = [
            DispenseBuilders.column(
                column=column,
                volume="25:microliter",
            )
            for column in echo_instructions.loc[
                echo_instructions["Destination Plate Name"] == plate,
                "Destination Well",
            ]
            .str[1:]
            .unique()
            .tolist()
        ]
        p.dispense(
            ref=pcr_plates[plate],
            reagent="water",
            columns=columns,
        )
        p.dispense(
            ref=pcr_plates[plate],
            reagent="master_mix",
            columns=columns,
        )

    for plate in pcr_plates:
        p.seal(pcr_plates[plate], type="foil", mode="adhesive")
        p.agitate(
            ref=pcr_plates[plate],
            mode="vortex",
            speed="1000:rpm",
            duration="15:second",
            temperature="20:celsius",
        )

    for plate in pcr_plates:
        extension_time_seconds: int = int(
            thermocycler_instructions.loc[
                thermocycler_instructions["BLOCK_NAME"] == plate,
                "PLATE_LONGEST_PCR",
            ].max()
            / 1000
            * 30
        )
        annealing_temperature: int = int(
            thermocycler_instructions.loc[
                thermocycler_instructions["BLOCK_NAME"] == plate,
                "THERMOCYCLER_ZONE_ANNEALING_TEMP",
            ].mean()
        )
        p.thermocycle(
            ref=pcr_plates[plate],
            groups=[
                {
                    "cycles": 1,
                    "steps": [{"temperature": "98:celsius", "duration": "30:second"}],
                },
                {
                    "cycles": 30,
                    "steps": [
                        {"temperature": "98:celsius", "duration": "10:second"},
                        {
                            "temperature": f"{annealing_temperature}:celsius",
                            "duration": "30:second",
                        },
                        {
                            "temperature": "72:celsius",
                            "duration": f"{extension_time_seconds}:second",
                        },
                    ],
                },
                {
                    "cycles": 1,
                    "steps": [{"temperature": "72:celsius", "duration": "2:minute"}],
                },
                {
                    "cycles": 1,
                    "steps": [{"temperature": "10:celsius", "duration": "30:second"}],
                },
            ],
            volume="50:microliter",
            lid_temperature="105:celsius",
        )

    return json.dumps(p.as_dict(), indent=2)


def analyze_pcrs(
    pcr_worksheet: DataFrame[schemas.PCRWorksheetSchema],
) -> str:
    """Create autoprotocol for analyzing PCRs"""
    p = Protocol()
    pcr_plate_names: list[str] = pcr_worksheet["OUTPUT_PLATE"].unique().tolist()
    pcr_plates: dict[str, Container] = {
        pcr_plate_name: p.ref(
            pcr_plate_name, id=pcr_plate_name, cont_type="96-pcr", storage="cold_20"
        )
        for pcr_plate_name in pcr_plate_names
    }

    zag_plates: dict[str, Container] = {
        f"zag_{pcr_plate_name}": p.ref(
            f"zag_{pcr_plate_name}",
            id=None,
            cont_type="96-pcr",
            storage=None,
            discard=True,
        )
        for pcr_plate_name in pcr_plate_names
    }

    for plate in zag_plates:
        p.dispense_full_plate(
            ref=zag_plates[plate],
            reagent="TE buffer",
            volume="25:microliter",
        )

    for plate in pcr_plates:
        p.unseal(pcr_plates[plate])
        p.transfer(
            source=pcr_plates[plate].all_wells(),
            destination=zag_plates[f"zag_{plate}"].all_wells(),
            volume="1:microliter",
            method=Transfer(
                blowout=False,
                prime=False,
                transit=False,
                mix_before=False,
                mix_after=False,
            ),
        )
        p.seal(pcr_plates[plate], type="foil", mode="adhesive")

    for plate in zag_plates:
        p.seal(zag_plates[plate], type="foil", mode="adhesive")
        p.agitate(
            ref=zag_plates[plate],
            mode="vortex",
            speed="1000:rpm",
            duration="15:second",
            temperature="20:celsius",
        )
        p.spin(
            ref=zag_plates[plate],
            acceleration="3000:g",
            duration="1:minute",
        )
        p.unseal(zag_plates[plate])
        p.gel_separate(
            zag_plates[plate].all_wells(),
            matrix="ZAG 130 dsDNA Separation Gel(96, 1.0%)",
            ladder="1 kb Plus DNA Ladder",
            dataref=f"{plate}_raw_data",
            volume="1:microliter",
            duration="45:minute",
        )

    return json.dumps(p.as_dict(), indent=2)


def perform_digestions(
    pcr_worksheet: DataFrame[schemas.PCRWorksheetSchema],
    digest_worksheet: DataFrame[schemas.DigestsWorksheetSchema],
) -> str:
    """Create autoprotocol for performing digestions"""
    p = Protocol()
    pcr_plate_names: list[str] = pcr_worksheet["OUTPUT_PLATE"].unique().tolist()
    pcr_plates: dict[str, Container] = {
        pcr_plate_name: p.ref(
            pcr_plate_name, id=pcr_plate_name, cont_type="96-pcr", storage="cold_20"
        )
        for pcr_plate_name in pcr_plate_names
    }

    digest_plate_names: list[str] = (
        digest_worksheet["DIGEST_SOURCE_PLATE"].unique().tolist()
    )
    digest_plates: dict[str, Container] = {
        digest_plate_name: p.ref(
            digest_plate_name, id=None, cont_type="96-pcr", storage="cold_20"
        )
        for digest_plate_name in digest_plate_names
    }

    for plate in pcr_plates:
        p.unseal(pcr_plates[plate])
        # Dispense restriction enzymes only to columns that have a reaction
        # TODO: use mantis to dispense only to wells that have reaction
        buffer_columns = [
            DispenseBuilders.column(
                column=column,
                volume="5:microliter",
            )
            for column in pcr_worksheet.loc[
                pcr_worksheet["OUTPUT_PLATE"] == plate,
                "OUTPUT_WELL",
            ]
            .str[1:]
            .unique()
            .tolist()
        ]
        enzyme_columns = [
            DispenseBuilders.column(
                column=column,
                volume="1:microliter",
            )
            for column in pcr_worksheet.loc[
                pcr_worksheet["OUTPUT_PLATE"] == plate,
                "OUTPUT_WELL",
            ]
            .str[1:]
            .unique()
            .tolist()
        ]
        p.dispense(
            ref=pcr_plates[plate],
            reagent="10X FastDigest Buffer",
            columns=buffer_columns,
        )
        p.dispense(
            ref=pcr_plates[plate],
            reagent="DpnI",
            columns=enzyme_columns,
            step_size="0.5:microliter",
        )
        p.seal(pcr_plates[plate], type="foil", mode="adhesive")
        p.thermocycle(
            ref=pcr_plates[plate],
            groups=[
                {
                    "cycles": 1,
                    "steps": [{"temperature": "37:celsius", "duration": "60:minute"}],
                },
                {
                    "cycles": 1,
                    "steps": [{"temperature": "98:celsius", "duration": "5:minute"}],
                },
                {
                    "cycles": 1,
                    "steps": [{"temperature": "10:celsius", "duration": "30:second"}],
                },
            ],
            volume="56:microliter",
            lid_temperature="105:celsius",
        )

    for _, digest in digest_worksheet.iterrows():
        template_tube = p.ref(
            digest["SEQUENCE_SOURCE"], cont_type="micro-1.5", storage="cold_20"
        )
        p.transfer(
            source=template_tube.well(0),
            destination=digest_plates[digest["DIGEST_SOURCE_PLATE"]].well(
                digest["DIGEST_SOURCE_WELL"]
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

    for plate in digest_plates:
        # Dispense restriction enzymes only to columns that have a reaction
        # TODO: use mantis to dispense only to wells that have reaction
        buffer_columns = [
            DispenseBuilders.column(
                column=column,
                volume="5:microliter",
            )
            for column in digest_worksheet.loc[
                digest_worksheet["DIGEST_SOURCE_PLATE"] == plate,
                "DIGEST_SOURCE_WELL",
            ]
            .str[1:]
            .unique()
            .tolist()
        ]
        enzyme_columns = [
            DispenseBuilders.column(column=column, volume="2:microliter")
            for column in digest_worksheet.loc[
                digest_worksheet["DIGEST_SOURCE_PLATE"] == plate,
                "DIGEST_SOURCE_WELL",
            ]
            .str[1:]
            .unique()
            .tolist()
        ]
        p.dispense(
            ref=digest_plates[plate],
            reagent="10X FastDigest Buffer",
            columns=buffer_columns,
        )
        p.dispense(
            ref=digest_plates[plate],
            reagent="Restriction Enzyme",
            columns=enzyme_columns,
            step_size="0.5:microliter",
        )
        p.seal(digest_plates[plate], type="foil", mode="adhesive")
        p.thermocycle(
            ref=digest_plates[plate],
            groups=[
                {
                    "cycles": 1,
                    "steps": [{"temperature": "37:celsius", "duration": "60:minute"}],
                },
                {
                    "cycles": 1,
                    "steps": [{"temperature": "98:celsius", "duration": "5:minute"}],
                },
                {
                    "cycles": 1,
                    "steps": [{"temperature": "10:celsius", "duration": "30:second"}],
                },
            ],
            volume="56:microliter",
            lid_temperature="105:celsius",
        )

    return json.dumps(p.as_dict(), indent=2)


def perform_cleanups(
    pcr_worksheet: DataFrame[schemas.PCRWorksheetSchema],
    digest_worksheet: DataFrame[schemas.DigestsWorksheetSchema],
) -> str:
    """Create autoprotocol for performing DNA cleanups"""
    p = Protocol()
    pcr_plate_names: list[str] = pcr_worksheet["OUTPUT_PLATE"].unique().tolist()
    digest_plate_names: list[str] = (
        digest_worksheet["DIGEST_SOURCE_PLATE"].unique().tolist()
    )
    cleanup_source_plates: dict[str, Container] = {
        cleanup_plate_name: p.ref(
            cleanup_plate_name,
            id=cleanup_plate_name,
            cont_type="96-pcr",
            storage="cold_20",
        )
        for cleanup_plate_name in pcr_plate_names + digest_plate_names
    }
    cleanup_plates: dict[str, Container] = {
        "kf-"
        + cleanup_plate_name: p.ref(
            "kf-" + cleanup_plate_name,
            id=None,
            cont_type="96-v-kf",
            storage=None,
            discard=True,
        )
        for cleanup_plate_name in pcr_plate_names + digest_plate_names
    }
    waste_container: Container = p.ref(
        "waste_container", cont_type="res-sw96-hp", discard=True
    )

    for plate in cleanup_plates:
        # TODO: cleanup only wells with samples
        p.unseal(ref=cleanup_source_plates[plate.replace("kf-", "")])
        p.transfer(
            source=cleanup_source_plates[plate.replace("kf-", "")].all_wells(),
            destination=cleanup_plates[plate].all_wells(),
            volume="60:microliter",
            method=Transfer(
                blowout=False,
                prime=False,
                transit=False,
                mix_before=False,
                mix_after=False,
            ),
        )
        # Magbead binding
        p.dispense_full_plate(
            ref=cleanup_plates[plate],
            reagent="magnetic_beads",
            volume="90:microliter",
        )
        p.mag_mix(
            head="96-pcr",
            container=cleanup_plates[plate],
            duration="5:minute",
            frequency="60:hertz",
            magnetize=False,
        )
        p.mag_collect(
            head="96-pcr",
            container=cleanup_plates[plate],
            cycles=5,
            pause_duration="5:second",
        )
        # Magbead wash 1
        p.transfer(
            source=cleanup_plates[plate].all_wells(),
            destination=waste_container.well(0),
            volume="150:microliter",
            method=Transfer(
                blowout=False,
                prime=False,
                transit=False,
                mix_before=False,
                mix_after=False,
            ),
        )
        p.dispense_full_plate(
            ref=cleanup_plates[plate],
            reagent=r"70% ethanol",
            volume="200:microliter",
        )
        p.mag_release(
            head="96-pcr",
            container=cleanup_plates[plate],
            duration="30:second",
            frequency="60:hertz",
        )
        p.mag_collect(
            head="96-pcr",
            container=cleanup_plates[plate],
            cycles=5,
            pause_duration="5:second",
        )
        # Magbead wash 2
        p.transfer(
            source=cleanup_plates[plate].all_wells(),
            destination=waste_container.well(0),
            volume="200:microliter",
            method=Transfer(
                blowout=False,
                prime=False,
                transit=False,
                mix_before=False,
                mix_after=False,
            ),
        )
        p.dispense_full_plate(
            ref=cleanup_plates[plate],
            reagent=r"70% ethanol",
            volume="200:microliter",
        )
        p.mag_release(
            head="96-pcr",
            container=cleanup_plates[plate],
            duration="30:second",
            frequency="60:hertz",
        )
        p.mag_collect(
            head="96-pcr",
            container=cleanup_plates[plate],
            cycles=5,
            pause_duration="5:second",
        )
        # Magbead elution
        p.mag_dry(
            head="96-pcr",
            container=cleanup_plates[plate],
            duration="10:minute",
        )
        p.transfer(
            source=cleanup_plates[plate].all_wells(),
            destination=waste_container.well(0),
            volume="200:microliter",
            method=Transfer(
                blowout=False,
                prime=False,
                transit=False,
                mix_before=False,
                mix_after=False,
            ),
        )
        p.dispense_full_plate(
            ref=cleanup_plates[plate],
            reagent="Nuclease Free Water",
            volume="50:microliter",
        )
        p.mag_release(
            head="96-pcr",
            container=cleanup_plates[plate],
            duration="30:second",
            frequency="60:hertz",
        )
        p.mag_incubate(
            head="96-pcr",
            container=cleanup_plates[plate],
            duration="2:minute",
        )
        p.mag_collect(
            head="96-pcr",
            container=cleanup_plates[plate],
            cycles=5,
            pause_duration="5:second",
        )
        p.transfer(
            source=cleanup_plates[plate].all_wells(),
            destination=cleanup_source_plates[plate.replace("kf-", "")].all_wells(),
            volume="60:microliter",
            method=Transfer(
                blowout=False,
                prime=False,
                transit=False,
                mix_before=False,
                mix_after=False,
            ),
        )
        p.seal(
            cleanup_source_plates[plate.replace("kf-", "")],
            type="foil",
            mode="adhesive",
        )
    return json.dumps(p.as_dict(), indent=2)


def organize_and_quantify_fragments(
    quant_worksheet: DataFrame[schemas.PartsWorksheetSchema],
) -> str:
    """Create autoprotocol for organizing and quantifying fragments"""
    p = Protocol()
    part_plate_names: list[str] = quant_worksheet["PART_PLATE"].unique().tolist()
    part_plates: dict[str, Container] = {
        part_plate_name: p.ref(
            part_plate_name, id=None, cont_type="384-echo", storage="cold_20"
        )
        for part_plate_name in part_plate_names
    }

    quant_plate_names: list[str] = quant_worksheet["QUANT_PLATE"].unique().tolist()
    quant_plates: dict[str, Container] = {
        quant_plate_name: p.ref(
            quant_plate_name,
            id=None,
            cont_type="384-flat",
            storage=None,
            discard=True,
        )
        for quant_plate_name in quant_plate_names
    }

    source_plate_names: list[str] = quant_worksheet["SOURCE_PLATE"].unique().tolist()
    source_plates: dict[str, Container] = {
        source_plate_name: p.ref(
            source_plate_name,
            id=source_plate_name,
            cont_type="96-pcr",
            storage=None,
            discard=True,
        )
        for source_plate_name in source_plate_names
    }

    for plate in source_plates:
        p.unseal(source_plates[plate])

    for _, part in quant_worksheet.iterrows():
        p.transfer(
            source=source_plates[part["SOURCE_PLATE"]].well(part["SOURCE_WELL"]),
            destination=part_plates[part["PART_PLATE"]].well(part["PART_WELL"]),
            volume="50:microliter",
            method=Transfer(
                blowout=False,
                prime=False,
                transit=False,
                mix_before=False,
                mix_after=False,
            ),
        )

    for _, part in quant_worksheet.iterrows():
        p.acoustic_transfer(
            source=part_plates[part["PART_PLATE"]].well(part["PART_WELL"]),
            dest=quant_plates[part["QUANT_PLATE"]].well(part["QUANT_WELL"]),
            volume=f'{part["QUANT_VOLUME"]}:nanoliter',
            droplet_size="2.5:nanoliter",
        )

    for plate in quant_plates:
        p.dispense_full_plate(
            ref=quant_plates[plate],
            reagent="1X dsDNA BR Assay Buffer",
            volume="100:microliter",
        )
        p.agitate(
            ref=quant_plates[plate],
            mode="vortex",
            speed="200:rpm",
            duration="30:second",
        )

    for plate in quant_plates:
        p.fluorescence(
            ref=quant_plates[plate],
            wells=quant_plates[plate].all_wells(),
            excitation="485:nanometer",
            emission="530:nanometer",
            dataref=f"{plate}_raw_qubit_data",
        )

    for plate in part_plates:
        p.seal(part_plates[plate], type="foil", mode="adhesive")

    return json.dumps(p.as_dict(), indent=2)


def perform_assembly(
    assembly_echo_instructions: DataFrame[schemas.EchoInstructionsSchema],
) -> str:
    """Create autoprotocol for performing equivolume DNA assembly"""
    # TODO: add yeast and golden gate assembly to autoprotocol

    p = Protocol()
    part_plate_names: list[str] = (
        assembly_echo_instructions["Source Plate Name"].unique().tolist()
    )
    part_plates: dict[str, Container] = {
        part_plate_name: p.ref(
            part_plate_name, id=part_plate_name, cont_type="384-echo", storage="cold_20"
        )
        for part_plate_name in part_plate_names
    }

    assembly_plate_names: list[str] = (
        assembly_echo_instructions["Destination Plate Name"].unique().tolist()
    )
    assembly_plates: dict[str, Container] = {
        assembly_plate_name: p.ref(
            assembly_plate_name, id=None, cont_type="96-pcr", storage="cold_20"
        )
        for assembly_plate_name in assembly_plate_names
    }

    for plate in part_plates:
        p.unseal(part_plates[plate])

    for _, instruction in assembly_echo_instructions.iterrows():
        p.acoustic_transfer(
            source=part_plates[instruction["Source Plate Name"]].well(
                instruction["Source Well"]
            ),
            dest=assembly_plates[instruction["Destination Plate Name"]].well(
                instruction["Destination Well"]
            ),
            volume=f'{instruction["Transfer Volume"]}:nanoliter',
            droplet_size="2.5:nanoliter",
        )

    for plate in part_plates:
        p.seal(part_plates[plate])

    for plate in assembly_plates:
        p.dispense_full_plate(
            ref=assembly_plates[plate],
            reagent="Gibson Assembly Master Mix",
            volume="5:microliter",
        )

    for plate in assembly_plates:
        p.seal(assembly_plates[plate], type="foil", mode="adhesive")
        p.thermocycle(
            ref=assembly_plates[plate],
            groups=[
                {
                    "cycles": 1,
                    "steps": [{"temperature": "50:celsius", "duration": "60:minute"}],
                }
            ],
        )

    return json.dumps(p.as_dict(), indent=2)


def perform_transformation(
    plating_instructions: DataFrame[schemas.PlatingInstructionsSchema],
) -> str:
    """Create autoprotocol for performing E. coli transformations"""
    p = Protocol()
    assembly_plate_names: list[str] = (
        plating_instructions["src_plate"].unique().tolist()
    )
    assembly_plates: dict[str, Container] = {
        assembly_plate_name: p.ref(
            assembly_plate_name,
            id=assembly_plate_name,
            cont_type="96-pcr",
            storage="cold_20",
        )
        for assembly_plate_name in assembly_plate_names
    }

    transformation_plate_names: list[str] = [
        "transformation_" + plate for plate in assembly_plate_names
    ]
    transformation_plates: dict[str, Container] = {
        transformation_plate_name: p.ref(
            transformation_plate_name,
            id=None,
            cont_type="96-pcr",
            storage=None,
            discard=True,
        )
        for transformation_plate_name in transformation_plate_names
    }

    agar_plate_names: list[str] = plating_instructions["QPLATE"].unique().tolist()
    agar_plates: dict[str, Container] = {
        agar_plate_name: p.ref(
            agar_plate_name,
            id=None,
            cont_type=agar_qplate,
            storage="cold_4",
        )
        for agar_plate_name in agar_plate_names
    }

    for plate in assembly_plates:
        p.unseal(assembly_plates[plate])

    for plate in transformation_plates:
        p.dispense_full_plate(
            ref=transformation_plates[plate],
            reagent="Chemically Competent E. coli",
            volume="10:microliter",
        )

    for _, transformation in plating_instructions.iterrows():
        p.transfer(
            source=assembly_plates[transformation["src_plate"]].well(
                transformation["src_well"]
            ),
            destination=transformation_plates[
                "transformation_" + transformation["src_plate"]
            ].well(transformation["src_well"]),
            volume="5:microliter",
            method=Transfer(
                blowout=False,
                prime=False,
                transit=False,
                mix_before=False,
                mix_after=False,
            ),
        )

    for plate in transformation_plates:
        p.seal(transformation_plates[plate], type="foil", mode="adhesive")
        p.incubate(
            ref=transformation_plates[plate],
            where="cold_4",
            duration="10:minute",
        )
        p.thermocycle(
            ref=transformation_plates[plate],
            groups=[
                {
                    "cycles": 1,
                    "steps": [{"temperature": "42:celsius", "duration": "30:second"}],
                }
            ],
        )
        p.incubate(
            ref=transformation_plates[plate],
            where="cold_4",
            duration="5:minute",
        )
        p.unseal(transformation_plates[plate])
        p.dispense_full_plate(
            ref=transformation_plates[plate],
            reagent="SOC Media",
            volume="180:microliter",
        )
        p.seal(transformation_plates[plate], type="breathable", mode="adhesive")
        p.incubate(
            ref=transformation_plates[plate],
            where="warm_37",
            duration="1:hour",
            shaking=True,
        )
        p.unseal(transformation_plates[plate])

    for _, transformation in plating_instructions.iterrows():
        p.spread(
            source=transformation_plates[
                "transformation_" + transformation["src_plate"]
            ].well(transformation["src_well"]),
            dest=agar_plates[transformation["QPLATE"]].well(transformation["QWELL"]),
            volume="150:microliter",
        )

    for agar_plate in agar_plates:
        p.incubate(
            ref=agar_plates[agar_plate],
            where="ambient",
            duration="1:hour",
        )
        p.incubate(
            ref=agar_plates[agar_plate],
            where="warm_37",
            duration="16:hour",
        )

    return json.dumps(p.as_dict(), indent=2)


def perform_colony_picking(
    picking_instructions: DataFrame[schemas.PickingResultsSchema],
) -> str:
    """Create autoprotocol for picking E. coli colonies."""
    p = CustomProtocol()
    agar_plate_names: list[str] = (
        picking_instructions["Source Barcode"].unique().tolist()
    )
    agar_plates: dict[str, Container] = {
        agar_plate_name: p.ref(
            agar_plate_name,
            id=agar_plate_name,
            cont_type=agar_qplate,
            storage="cold_4",
        )
        for agar_plate_name in agar_plate_names
    }

    picking_plate_names: list[str] = [
        "picking_" + name
        for name in picking_instructions["Destination Barcode"].unique().tolist()
    ]
    picking_plates: dict[str, Container] = {
        picking_plate_name: p.ref(
            picking_plate_name,
            id=None,
            cont_type="96-deep",
            storage=None,
            discard=True,
        )
        for picking_plate_name in picking_plate_names
    }

    glycerol_plate_names: list[str] = (
        picking_instructions["Destination Barcode"].unique().tolist()
    )
    glycerol_plates: dict[str, Container] = {
        glycerol_plate_name: p.ref(
            glycerol_plate_name,
            id=None,
            cont_type="96-pcr",
            storage="cold_80",
        )
        for glycerol_plate_name in glycerol_plate_names
    }

    ngs_plate_names: list[str] = [
        "ngs_" + name
        for name in picking_instructions["Destination Barcode"].unique().tolist()
    ]
    ngs_plates: dict[str, Container] = {
        ngs_plate_name: p.ref(
            ngs_plate_name,
            id=None,
            cont_type="96-pcr",
            storage="cold_20",
        )
        for ngs_plate_name in ngs_plate_names
    }

    for plate in picking_plates:
        p.dispense_full_plate(
            ref=picking_plates[plate],
            reagent="LB Miller Broth",
            volume="800:microliter",
        )

    picking_objects: list[dict[str, t.Any]] = [
        {
            "source": agar_plates[source_plate].well(source_well),
            "destination": picking_plates["picking_" + destination_plate].well(
                destination_well
            ),
        }
        for source_plate, source_well, destination_plate, destination_well in zip(
            picking_instructions["Source Barcode"],
            picking_instructions["Source Region"],
            picking_instructions["Destination Barcode"],
            picking_instructions["Destination Well"],
        )
    ]
    p.pick(colonies=picking_objects)

    for plate in picking_plates:
        p.incubate(
            ref=picking_plates[plate],
            where="warm_37",
            duration="16:hour",
        )

    for plate in glycerol_plates:
        p.dispense_full_plate(
            ref=glycerol_plates[plate], reagent=r"60% glycerol", volume="50:microliter"
        )

    for _, colony in picking_instructions.iterrows():
        p.transfer(
            source=picking_plates["picking_" + colony["Destination Barcode"]].well(
                colony["Destination Well"]
            ),
            destination=glycerol_plates[colony["Destination Barcode"]].well(
                colony["Destination Well"]
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

    for plate in glycerol_plates:
        p.seal(glycerol_plates[plate], type="foil", mode="adhesive")

    for plate in ngs_plates:
        p.dispense_full_plate(
            ref=ngs_plates[plate], reagent="water", volume="20:microliter"
        )

    for _, colony in picking_instructions.iterrows():
        p.transfer(
            source=picking_plates["picking_" + colony["Destination Barcode"]].well(
                colony["Destination Well"]
            ),
            destination=ngs_plates["ngs_" + colony["Destination Barcode"]].well(
                colony["Destination Well"]
            ),
            volume="20:microliter",
            method=Transfer(
                blowout=False,
                prime=False,
                transit=False,
                mix_before=False,
                mix_after=False,
            ),
        )

    for plate in ngs_plates:
        p.seal(ref=ngs_plates[plate], type="foil", mode="adhesive")
        p.thermocycle(
            ref=ngs_plates[plate],
            groups=[
                {
                    "cycles": 1,
                    "steps": [{"temperature": "98:celsius", "duration": "10:minute"}],
                },
                {
                    "cycles": 1,
                    "steps": [{"temperature": "10:celsius", "duration": "30:second"}],
                },
            ],
            volume="40:microliter",
            lid_temperature="105:celsius",
        )

    return json.dumps(p.as_dict(), indent=2)
