#!/usr/bin/env python3

import collections
import io
import itertools
import logging
import os
import warnings
import zipfile
from dataclasses import dataclass  # >python 3.7
from typing import Any, Dict, Generator, List, Optional, Tuple

import numpy as np
import pandas as pd
from Bio import BiopythonWarning, SeqIO
from pandera import check_types
from pandera.typing import DataFrame
from scipy.optimize import OptimizeResult, linprog

import app.api.utils.post_automation as post_automation
import app.core.j5_to_echo_utils as j5_to_echo_utils
from app import schemas
from app.core.config import settings
from app.core.pcr_update import distribute_pcr
from app.core.plating_utils import create_plating_instructions
from app.core.workflow_readme import workflow_readme

warnings.simplefilter("ignore", BiopythonWarning)


# Global Variables
OUTPUT_OLIGOS_PLATE_FILENAME: str = "oligos_plate.csv"
OUTPUT_TEMPLATES_PLATE_FILENAME: str = "templates_plate.csv"
OUTPUT_PCR_MIX_TUBES_FILENAME: str = "pcr_mix_tubes.csv"
MONTE_CARLO_STEPS: int = 100
MAX_WELL_USES: int = 8
DOWNSTREAM_AUTOMATION_PARAMETERS_TEMPLATE: str = os.path.join(
    os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))),
    "downstream_automation_parameters_template.txt",
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def j5_to_echo(j5_design: schemas.J5Design) -> Tuple[dict, io.BytesIO]:
    """Jupyter notebook in function form

    Arguments
    ---------
    master_j5 : str
        String representation of condensed assembly file
    """
    logger.debug("Beginning to automate J5 Design")
    template_plate_df: DataFrame[
        schemas.TemplatesPlateSchema
    ] = create_templates_plates(pcr_df=j5_design.master_j5.pcr_reactions)
    oligos_plate_df: DataFrame[
        schemas.OligosPlateSchema
    ] = create_oligos_plates(oligos=j5_design.master_j5.oligos)
    synths_plate_df: DataFrame[
        schemas.SynthsPlateSchema
    ] = create_synths_plates(
        directSynthesisDF=j5_design.master_j5.direct_synthesis
    )
    oligos_order_form_96: DataFrame[
        schemas.OligosOrderSchema
    ] = create_oligos_order_form(
        oligoPlateDF=oligos_plate_df,
        oligos=j5_design.master_j5.oligos,
        size=96,
    )
    oligos_order_form_384: DataFrame[
        schemas.OligosOrderSchema
    ] = create_oligos_order_form(
        oligoPlateDF=oligos_plate_df,
        oligos=j5_design.master_j5.oligos,
        size=384,
    )
    assembly_volume_df: DataFrame[
        schemas.AssemblyVolumeSchema
    ] = create_assembly_volume_df(
        assemblyPartsDF=j5_design.master_j5.parts,
        skinnyAssemblyInstructionsDF=j5_design.master_j5.skinny_assemblies,
    )
    pcr_instructions: DataFrame[schemas.PCRInstructionsSchema]
    thermocycler: DataFrame[schemas.PCRThermocyclerSchema]
    (pcr_instructions, thermocycler) = distribute_pcr(
        templates=template_plate_df,
        oligos=oligos_plate_df,
        oligosseq=oligos_order_form_96,
        pcrrxns=j5_design.master_j5.pcr_reactions,
        assemblies=assembly_volume_df,
        max_well_uses=MAX_WELL_USES,
    )
    pcr_echo_instructions_df: DataFrame[
        schemas.EchoInstructionsSchema
    ] = create_echo_instructions(worksheet=pcr_instructions, method="pcr")
    pcr_bead_instructions_df = create_bead_instructions(
        clean_pcr_df=pcr_instructions
    )
    clean_pcr_df: DataFrame[schemas.PCRWorksheetSchema] = stamp_pcrs(
        cleanPCRDF=pcr_instructions
    )
    pcr_biomek_instructions_df = create_biomek_pcr_instructions(
        cleanPCRDF=clean_pcr_df
    )
    digest_instructions: DataFrame[
        schemas.DigestsPlateSchema
    ] = create_clean_digest_df(
        digestedPiecesDF=j5_design.master_j5.digests,
        assemblyVolumeDF=assembly_volume_df,
    )
    clean_digest_df: DataFrame[
        schemas.DigestsWorksheetSchema
    ] = stamp_digests(
        cleanDigestDF=digest_instructions, cleanPCRDF=clean_pcr_df
    )
    dpni_biomek_instructions = create_dpni_instructions(
        clean_pcr_df=clean_pcr_df
    )
    zag_echo_instructions_df: DataFrame[
        schemas.EchoInstructionsSchema
    ] = create_echo_instructions(worksheet=clean_pcr_df, method="zag")
    assembly_parts_df: DataFrame[
        schemas.AssemblyPartsSchema
    ] = add_part_locations(
        assemblyPartsDF=j5_design.master_j5.parts,
        cleanPCRDF=clean_pcr_df,
        cleanDigestDF=clean_digest_df,
    )
    clean_part_df: DataFrame[
        schemas.PartsPlateSchema
    ] = create_clean_part_df(
        parts=j5_design.master_j5.parts,
        clean_pcr_df=clean_pcr_df,
        clean_digest_df=clean_digest_df,
    )
    assembly_volume_verified_df: DataFrame[
        schemas.AssemblyVolumeVerifiedSchema
    ] = verify_volume_requirements(
        assemblyVolumeDF=assembly_volume_df,
        assemblyPartsDF=assembly_parts_df,
    )
    skinny_assembly_df: DataFrame[
        schemas.AssemblyWorksheetSchema
    ] = create_skinny_assembly_df(
        skinnyassemblyInstructionsDF=j5_design.master_j5.skinny_assemblies,
        assemblyVolumeDF=assembly_volume_verified_df,
        assemblyPartsDF=assembly_parts_df,
    )
    assembly_echo_instructions_df: DataFrame[
        schemas.EchoInstructionsSchema
    ] = create_echo_instructions(
        worksheet=skinny_assembly_df, method="assembly"
    )
    construct_df: DataFrame[
        schemas.ConstructWorksheetSchema
    ] = gather_construct_worksheet(assembly_worksheet=skinny_assembly_df)
    quant_worksheet: DataFrame[
        schemas.PartsWorksheetSchema
    ] = create_quant_worksheet(parts_plate=clean_part_df)
    quant_echo_instructions: DataFrame[
        schemas.EchoInstructionsSchema
    ] = create_echo_instructions(worksheet=quant_worksheet, method="quant")
    equimolar_assembly_df: DataFrame[
        schemas.EquimolarAssemblyWorksheetSchema
    ] = create_equimolar_assembly_instructions(
        assembly_df=skinny_assembly_df,
        quant_df=quant_worksheet,
        max_fmol=100.0,
        max_vol=5.0,
        max_part_percentage=1.0,
    )
    equimolar_assembly_echo_instructions: DataFrame[
        schemas.EchoInstructionsSchema
    ] = create_echo_instructions(
        worksheet=equimolar_assembly_df, method="equimolar"
    )
    assembly_biomek_instructions = create_assembly_instructions(
        construct_worksheet=construct_df
    )
    plating_instructions_biomek: DataFrame[
        schemas.PlatingInstructionsSchema
    ] = create_plating_instructions(
        plating=construct_df,
        method="biomek",
        assemblyColumns=("src_plate", "src_well"),
    )
    registry_form, registry_sequences = create_registry_submission_form(
        construct_worksheet=construct_df,
    )
    plasmid_sequences: DataFrame[
        schemas.BenchlingPlasmidSequences
    ] = collect_plasmid_sequences(genbanks=j5_design.plasmid_maps)
    aa_sequences: DataFrame[
        schemas.BenchlingAASequences
    ] = collect_aa_sequences(part_sources=j5_design.master_j5.part_sources)
    gene_sequences: DataFrame[
        schemas.BenchlingGeneSequences
    ] = collect_gene_sequences(
        part_sources=j5_design.master_j5.part_sources
    )

    # Preparing ultimate results
    results: Dict[str, Any] = {}
    results["README.md"] = workflow_readme(0)
    results["Input"] = {
        "master_j5.csv": j5_design.master_j5.to_file(),
        "benchling_plasmid_sequences.csv": plasmid_sequences.to_csv(
            index=False
        ),
        "benchling_aa_sequences.csv": aa_sequences.to_csv(index=False),
        "benchling_gene_sequences.csv": gene_sequences.to_csv(index=False),
        "plasmid_maps": {
            plasmid.filename: plasmid.contents
            for plasmid in j5_design.plasmid_maps
        },
    }
    results["Step_1-Order_genes"] = {
        "README.md": workflow_readme(1),
        "synths_plate.csv": synths_plate_df.to_csv(index=False),
    }
    results["Step_2-Order_oligos"] = {
        "README.md": workflow_readme(2),
        "oligos_plate.csv": oligos_plate_df.to_csv(index=False),
        "oligos_order_96.csv": oligos_order_form_96.to_csv(index=False),
        "oligos_order_384.csv": oligos_order_form_384.to_csv(index=False),
        "oligos_order_96.xlsx": to_excel_bytestring(
            oligos_order_form_96, "oligos"
        ),
        "oligos_order_384.xlsx": to_excel_bytestring(
            oligos_order_form_384, "oligos"
        ),
    }
    results["Step_3-Prepare_templates"] = {
        "README.md": workflow_readme(3),
        "templates_plate.csv": template_plate_df.to_csv(index=False),
    }
    results["Step_4-Perform_PCRs"] = {
        "README.md": workflow_readme(4),
        "clean_pcr_worksheet.csv": clean_pcr_df.to_csv(index=False),
        "pcr_echo_instructions.csv": pcr_echo_instructions_df.to_csv(
            index=False
        ),
        "pcr_biomek_instructions.csv": pcr_biomek_instructions_df.to_csv(
            line_terminator="\r\n", index=False
        ),
        "pcr_thermocycler_instructions.csv": (
            thermocycler.to_csv(index=False)
        ),
    }
    results["Step_5-Analyze_PCRs"] = {
        "README.md": workflow_readme(5),
        "zag_echo_instructions.csv": zag_echo_instructions_df.to_csv(
            index=False
        ),
    }
    results["Step_6-Redo_PCRs"] = {
        "README.md": workflow_readme(6),
    }
    results["Step_7-Consolidate_PCRs"] = {
        "README.md": workflow_readme(7),
    }
    results["Step_8-Restriction_Digests"] = {
        "README.md": workflow_readme(8),
        "digests_plate.csv": clean_digest_df.to_csv(index=False),
        "dpni_biomek_instructions.csv": dpni_biomek_instructions.to_csv(
            line_terminator="\r\n", index=False
        ),
    }
    results["Step_9-PCR_Cleanup"] = {
        "README.md": workflow_readme(9),
        "bead_biomek_instructions.csv": pcr_bead_instructions_df.to_csv(
            line_terminator="\r\n", index=False
        ),
    }
    results["Step_10-Quantify_Part_Yield"] = {
        "README.md": workflow_readme(10),
        "parts_plate.csv": clean_part_df.to_csv(index=False),
        "quant_worksheet.csv": quant_worksheet.to_csv(index=False),
        "quant_echo_instructions.csv": quant_echo_instructions.to_csv(
            index=False
        ),
    }
    results["Step_11-Perform_Assembly"] = {
        "README.md": workflow_readme(11),
        "clean_assembly_worksheet.csv": skinny_assembly_df.to_csv(
            index=False
        ),
        "assembly_echo_instructions.csv": (
            assembly_echo_instructions_df.to_csv(index=False)
        ),
        "assembly_biomek_instructions.csv": (
            assembly_biomek_instructions.to_csv(index=False)
        ),
        "construct_worksheet.csv": construct_df.to_csv(index=False),
        "equimolar_assembly_worksheet.csv": (
            equimolar_assembly_df.to_csv(index=False)
        ),
        "equimolar_assembly_echo_instructions.csv": (
            equimolar_assembly_echo_instructions.to_csv(index=False)
        ),
    }
    results["Step_12-Yeast_Plasmid_Prep"] = {
        "README.md": workflow_readme(12),
    }
    results["Step_13-Ecoli_Transformation"] = {
        "README.md": workflow_readme(13),
        "plating_instructions_biomek.csv": (
            plating_instructions_biomek.to_csv(index=False)
        ),
    }
    results["Step_14-Colony_Picking"] = {
        "README.md": workflow_readme(14),
    }
    results["Step_15-Request_NGS"] = {
        "README.md": workflow_readme(15),
        "registry_submission_form.csv": registry_form.to_csv(index=False),
        "registry_submission_sequences.csv": registry_sequences.to_csv(
            index=False
        ),
    }
    results["Step_16-Submit_NGS_Samples"] = {
        "README.md": workflow_readme(16),
    }
    results["Step_17-Analyze_NGS_Results"] = {
        "README.md": workflow_readme(17),
    }
    results["Step_18-Cherrypick_Constructs"] = {
        "README.md": workflow_readme(18),
    }
    results["Step_19-Submit_To_Registry"] = {
        "README.md": workflow_readme(19),
    }
    # Returning results in a zip file
    initial_workflow_zip = create_workflow_zip({"workflow": results})

    # Creating an object that allows easily adding to db
    workflow_db_objects = {
        "plate_csvs": [
            {
                "name": "synths_plate.csv",
                "size": 96,
                "raw_data": synths_plate_df.to_csv(),
                "plate_type": "synth",
                "plate_names": list(synths_plate_df["PLATE ID"].unique()),
            },
            {
                "name": "oligos_plate.csv",
                "size": 384,
                "raw_data": oligos_plate_df.to_csv(),
                "plate_type": "oligo",
                "plate_names": list(oligos_plate_df["PLATE ID"].unique()),
            },
            {
                "name": "templates_plate.csv",
                "size": 384,
                "raw_data": template_plate_df.to_csv(),
                "plate_type": "template",
                "plate_names": list(
                    template_plate_df["PLATE ID"].unique()
                ),
            },
            {
                "name": "digests_plate.csv",
                "size": 96,
                "raw_data": clean_digest_df.to_csv(),
                "plate_type": "digest",
                "plate_names": list(
                    clean_digest_df["DIGEST_SOURCE_PLATE"].unique()
                ),
            },
            {
                "name": "parts_plate.csv",
                "size": 384,
                "raw_data": clean_part_df.to_csv(),
                "plate_type": "part",
                "plate_names": list(clean_part_df["PART_PLATE"].unique()),
            },
            {
                "name": "clean_pcr_worksheet.csv",
                "size": 96,
                "raw_data": clean_pcr_df.to_csv(),
                "plate_type": "pcr",
                "plate_names": list(clean_pcr_df["OUTPUT_PLATE"].unique()),
            },
        ],
        "instructions": [
            {
                "category": "oligo_order_96.csv",
                "trial": 1,
                "data": oligos_order_form_96.to_csv(),
                "assocations": ["oligo"],
            },
            {
                "category": "pcr_worksheet",
                "trial": 1,
                "data": clean_pcr_df.to_csv(),
                "assocations": ["pcr", "template", "oligo", "part"],
            },
            {
                "category": "part_worksheet",
                "trial": 1,
                "data": clean_part_df.to_csv(),
                "assocations": ["part"],
            },
            {
                "category": "clean_assembly_worksheet",
                "trial": 1,
                "data": skinny_assembly_df.to_csv(),
                "assocations": ["assembly"],
            },
            {
                "category": "pcr_echo_instructions.csv",
                "trial": 1,
                "data": pcr_echo_instructions_df.to_csv(),
                "assocations": ["pcr", "template", "oligo"],
            },
            {
                "category": "pcr_biomek_instructions.csv",
                "trial": 1,
                "data": pcr_biomek_instructions_df.to_csv(),
                "assocations": ["pcr", "template", "oligo"],
            },
            {
                "category": "zag_echo_instructions.csv",
                "trial": 1,
                "data": zag_echo_instructions_df.to_csv(),
                "assocations": ["pcr"],
            },
            {
                "category": "bead_biomek_instructions.csv",
                "trial": 1,
                "data": pcr_bead_instructions_df.to_csv(),
                "assocations": ["pcr"],
            },
            {
                "category": "dpni_biomek_instructions.csv",
                "trial": 1,
                "data": dpni_biomek_instructions.to_csv(),
                "assocations": ["pcr"],
            },
            {
                "category": "assembly_biomek_instructions.csv",
                "trial": 1,
                "data": assembly_biomek_instructions.to_csv(),
                "assocations": ["assembly"],
            },
            {
                "category": "construct_worksheet.csv",
                "trial": 1,
                "data": construct_df.to_csv(),
                "associations": ["construct"],
            },
            {
                "category": "quant_worksheet.csv",
                "trial": 1,
                "data": quant_worksheet.to_csv(),
                "associations": ["quant"],
            },
            {
                "category": "registry_submission_form.csv",
                "trial": 1,
                "data": registry_form.to_csv(),
                "associations": ["registry"],
            },
            {
                "category": "registry_submission_sequences.csv",
                "trial": 1,
                "data": registry_sequences.to_csv(),
                "associations": ["registry"],
            },
        ],
        "steps": [
            {
                "name": category,
                "number": int(category.split("-")[0].split("_")[-1]),
                "title": category.split("-")[1],
                "status": "incomplete",
            }
            for category in results
            if category.startswith("Step")
        ],
    }
    logger.debug("Finished automating j5 design")
    return workflow_db_objects, initial_workflow_zip


def create_workflow_zip(contents: dict) -> io.BytesIO:
    in_mem_zip = io.BytesIO()
    with zipfile.ZipFile(in_mem_zip, "w") as archive:
        for file_path, content in flatten_dict(contents):
            archive.writestr(file_path, content)
    in_mem_zip.seek(0)
    return in_mem_zip


def read_genbank_sequence(genbank: str) -> str:
    """Read sequence from genbank string"""
    return str(
        list(
            SeqIO.to_dict(
                SeqIO.parse(io.StringIO(genbank), "genbank")
            ).values()
        )[0].seq
    ).upper()


@check_types()
def collect_plasmid_sequences(
    genbanks: List[schemas.PlasmidMap],
) -> DataFrame[schemas.BenchlingPlasmidSequences]:
    """Get raw plasmid sequences from design genbanks"""
    if not genbanks:
        return pd.DataFrame(columns=["Name", "Bases", "Type"])
    plasmid_names: List[str] = []
    plasmid_seqs: List[str] = []
    for plasmid_map in genbanks:
        plasmid_names.append(plasmid_map.filename.replace(".gb", ""))
        plasmid_seqs.append(
            read_genbank_sequence(genbank=plasmid_map.contents)
        )
    return (
        pd.DataFrame({"Name": plasmid_names, "Bases": plasmid_seqs})
        .assign(Type="cloning")
        .sort_values(by="Name")
    )


@check_types()
def collect_aa_sequences(
    part_sources: Optional[DataFrame[schemas.MasterJ5PartSources]],
) -> DataFrame[schemas.BenchlingAASequences]:
    """Get aa sequences from design parts"""
    if part_sources is None:
        return pd.DataFrame(columns=["Name", "Bases", "Type"])
    return (
        part_sources.loc[:, ["Name", "AA_Sequence"]]
        .rename(columns={"AA_Sequence": "Bases"})
        .assign(Type="AA")
    )


@check_types()
def collect_gene_sequences(
    part_sources: Optional[DataFrame[schemas.MasterJ5PartSources]],
) -> DataFrame[schemas.BenchlingGeneSequences]:
    """Get dna sequences from design parts"""
    if part_sources is None:
        return pd.DataFrame(columns=["Name", "Bases"])
    return part_sources.loc[:, ["Name", "Sequence"]].rename(
        columns={"Sequence": "Bases"}
    )


def flatten_dict(
    pyobj: dict, keystring: str = ""
) -> Generator[Any, None, None]:
    """Flatten a dictionary of dictionaries

    Notes
    -----
    Code taken from:
    https://www.geeksforgeeks.org/
    python-convert-nested-dictionary-into-flattened-dictionary/
    """
    if type(pyobj) is dict:
        keystring = keystring + "/" if keystring else keystring
        for k in pyobj:
            yield from flatten_dict(pyobj[k], keystring + k)
    else:
        yield keystring, pyobj


def distribute_high_use_parts(
    tmpSkinnyAssembly: pd.DataFrame,
    assemblyVolumeDF: DataFrame[schemas.AssemblyVolumeVerifiedSchema],
    assemblyPartsDF: DataFrame[schemas.AssemblyPartsSchema],
) -> DataFrame[schemas.AssemblyWorksheetSchema]:
    """Distributes parts that are used a lot

    Each well can only be used so many (8) times. If a part is being
    used more than that, it has to be split up into multiple wells.

    Arguments
    ---------
    tmpSkinnyAssembly: pd.DataFrame
        Main assembly worksheet. This will be mutated and returned at
        the end of the function.

    assemblyVolumeDF: pd.DataFrame
        Table of transfer volumes

    assemblyPartsDF: pd.DataFrame
        Table of parts used in the assembly and their IDs

    Returns
    -------
    tmpSkinnyAssembly: pd.DataFrame
        Same main assembly worksheet, but with high-use parts in
        multiple wells instead of just one.

    """
    for partID in assemblyVolumeDF.loc[
        assemblyVolumeDF["NUMBER_OF_USES"] > MAX_WELL_USES, "PART_ID"
    ]:
        distributedWells = j5_to_echo_utils.distributeWells(
            assemblyVolumeDF.loc[
                assemblyVolumeDF["PART_ID"] == partID, "NUMBER_OF_USES"
            ].values[0],
            eval(
                assemblyPartsDF.loc[
                    assemblyPartsDF["ID Number"] == partID,
                    "SOURCE_LOCATIONS",
                ].values[0]
            ),
            maxWellUses=MAX_WELL_USES,
        )
        tmpSkinnyAssembly.loc[
            tmpSkinnyAssembly["Part ID"] == partID,
            ["Source Plate", "Source Well"],
        ] = distributedWells
    return tmpSkinnyAssembly


@check_types()
def verify_volume_requirements(
    assemblyVolumeDF: DataFrame[schemas.AssemblyVolumeSchema],
    assemblyPartsDF: DataFrame[schemas.AssemblyPartsSchema],
) -> DataFrame[schemas.AssemblyVolumeVerifiedSchema]:
    """Volume Verification

    Calculates the volume obtained from the source locations,
    then says whether that volume is enough to do all the reactions

    Arguments
    ---------
    assemblyVolumeDF: pd.DataFrame
        worksheet containing reaction volumes

    assemblyPartsDF: pd.DataFrame
        worksheet listing all the parts in the assembly

    Returns
    -------
    assemblyVolumeDF: pd.DataFrame
        same dataframe as above, modified to also say
        whether there's enough volume for the rxns

    """

    assemblyVolumeDF["NUMBER_OF_RXNS_PERFORMED"] = assemblyPartsDF.apply(
        lambda row: len(row["SOURCE_LOCATIONS"]), axis=1
    )
    assemblyVolumeDF["VOLUME_OBTAINED_(uL)"] = (
        assemblyVolumeDF["NUMBER_OF_RXNS_PERFORMED"] * 40
    )  # 40 uL elution volume
    assemblyVolumeDF["ENOUGH_VOLUME"] = (
        assemblyVolumeDF["VOLUME_OBTAINED_(uL)"]
        > assemblyVolumeDF["VOLUME_REQUIRED_(uL)"]
    )
    assemblyVolumeDF["SOURCE_WELLS"] = assemblyPartsDF["SOURCE_LOCATIONS"]
    return assemblyVolumeDF


@check_types()
def create_skinny_assembly_df(
    skinnyassemblyInstructionsDF: Optional[
        DataFrame[schemas.MasterJ5SkinnyAssemblies]
    ],
    assemblyVolumeDF: DataFrame[schemas.AssemblyVolumeVerifiedSchema],
    assemblyPartsDF: DataFrame[schemas.AssemblyPartsSchema],
) -> DataFrame[schemas.AssemblyWorksheetSchema]:
    """Creates skinny assembly worksheet

    Combines the two arguments into a new Dataframe called
    tmpSkinnyAssembly and returns it.
    This assembly sheet is easier to manipulate than FatAssembly.

    Arguments
    ---------
    skinnyassemblyInstructionsDF: pd.DataFrame
        Assembly Instructions - basically saying which part goes where

    assemblyPartsDF: pd.DataFrame
        Table of parts used in the assembly, their IDs, and their locations

    Returns
    -------
    tmpSkinnyAssembly: pd.DataFrame
        Main assembly worksheet that combines the list of parts with
        assembly instructions
    """
    tmpSkinnyAssembly = pd.merge(
        skinnyassemblyInstructionsDF,
        assemblyPartsDF.loc[
            :,
            [
                "ID Number",
                "FIRST_PART_SOURCE_PLATE",
                "FIRST_PART_WELL",
                "SOURCE_LOCATIONS",
            ],
        ],
        left_on="Part ID",
        right_on="ID Number",
        how="left",
    )

    summary = (
        tmpSkinnyAssembly.groupby("Number")
        .agg({"Part Name": "sum"})
        .replace(regex={r"\)\(": " + "})
        .replace(regex={r"\(": "", r"\)": ""})
    )
    summary = summary.rename(columns={"Part Name": "Parts Summary"})

    methodPrefix = {
        "SLIC/Gibson/CPEC": "gibson_plate_",
        "Golden-gate": "golden-gate_plate_",
    }
    tmpFatAssembly = (
        tmpSkinnyAssembly.groupby("Number")["Assembly Method"]
        .agg(set)
        .to_frame()
    )
    for method in methodPrefix.keys():
        numberOfMethodRxns = tmpFatAssembly.loc[
            tmpFatAssembly["Assembly Method"] == set([method])
        ].shape[0]
        tmpFatAssembly.loc[
            tmpFatAssembly["Assembly Method"] == set([method]),
            "Destination Plate",
        ] = [
            f"{methodPrefix[method]}{index//96 + 1}"
            for index in range(numberOfMethodRxns)
        ]
        tmpFatAssembly.loc[
            tmpFatAssembly["Assembly Method"] == set([method]),
            "Destination Well",
        ] = (
            [
                f"{row}{column}"
                for column, row in itertools.product(
                    range(1, 13), "ABCDEFGH"
                )
            ]
            * 20
        )[
            :numberOfMethodRxns
        ]
    tmpFatAssembly = tmpFatAssembly[
        ["Destination Plate", "Destination Well"]
    ]

    tmpSkinnyAssembly = tmpSkinnyAssembly.merge(
        tmpFatAssembly, left_on="Number", right_index=True, how="left"
    )
    tmpSkinnyAssembly = tmpSkinnyAssembly.merge(
        summary, left_on="Number", right_index=True, how="left"
    )
    tmpSkinnyAssembly = tmpSkinnyAssembly.rename(
        columns={
            "FIRST_PART_SOURCE_PLATE": "Source Plate",
            "FIRST_PART_WELL": "Source Well",
        }
    )
    skinny_assembly_df = distribute_high_use_parts(
        tmpSkinnyAssembly=tmpSkinnyAssembly,
        assemblyVolumeDF=assemblyVolumeDF,
        assemblyPartsDF=assemblyPartsDF,
    )
    return skinny_assembly_df


@check_types()
def stamp_digests(
    cleanDigestDF: DataFrame[schemas.DigestsPlateSchema],
    cleanPCRDF: DataFrame[schemas.PCRWorksheetSchema],
) -> DataFrame[schemas.DigestsWorksheetSchema]:
    """Adds part locations for each digest reaction"""
    if cleanDigestDF.empty:
        return pd.DataFrame(
            columns=list(cleanDigestDF.columns)
            + ["PARTS_SOURCE_PLATE", "PARTS_WELL", "PART_TYPE"]
        )
    cleanDigestDF["PARTS_SOURCE_PLATE"] = [
        f'parts_plate_{((index + 96 * cleanPCRDF["OUTPUT_PLATE"].unique().shape[0])//384 + 1)}'  # noqa
        for index in range(cleanDigestDF.shape[0])
    ]
    cleanDigestDF["PARTS_WELL"] = cleanDigestDF.loc[
        :, "DIGEST_SOURCE_PLATE":"DIGEST_SOURCE_WELL"  # type: ignore
    ].apply(
        lambda row: j5_to_echo_utils.stamp(
            j5_to_echo_utils.convert3WellTo2Well(
                row["DIGEST_SOURCE_WELL"]
            ),
            (
                int(row["DIGEST_SOURCE_PLATE"].split("_")[-1])
                - 1
                + cleanPCRDF["OUTPUT_PLATE"].unique().shape[0]
            )
            % 4,
        ),
        axis=1,
    )
    cleanDigestDF["PART_TYPE"] = "digest"
    return cleanDigestDF


@check_types()
def stamp_pcrs(
    cleanPCRDF: DataFrame[schemas.PCRInstructionsSchema],
) -> DataFrame[schemas.PCRWorksheetSchema]:
    """Adds part locations for each PCR reaction"""
    if cleanPCRDF.empty:
        return pd.DataFrame(
            columns=list(cleanPCRDF.columns)
            + ["PARTS_SOURCE_PLATE", "PARTS_WELL", "ZAG_PLATE", "ZAG_WELL"]
        )
    cleanPCRDF["PARTS_SOURCE_PLATE"] = cleanPCRDF["OUTPUT_PLATE"].apply(
        lambda pcrPlate: f'parts_plate_{( (int(pcrPlate.split("_")[-1])-1)//4 + 1 )}'  # noqa
    )
    cleanPCRDF["PARTS_WELL"] = cleanPCRDF.loc[
        :, "OUTPUT_PLATE":"OUTPUT_WELL"  # type: ignore
    ].apply(
        lambda row: j5_to_echo_utils.stamp(
            j5_to_echo_utils.convert3WellTo2Well(row["OUTPUT_WELL"]),
            (int(row["OUTPUT_PLATE"].split("_")[-1]) - 1) % 4,
        ),
        axis=1,
    )
    cleanPCRDF["ZAG_PLATE"] = [
        f"zag_plate_{index//95 + 1}"
        for index in range(cleanPCRDF.shape[0])
    ]
    cleanPCRDF["ZAG_WELL"] = (
        [
            f"{row}{column}"
            for row, column in list(
                itertools.product("ABCDEFGH", range(1, 13))
            )[:-1]
        ]
        * 20
    )[: cleanPCRDF.shape[0]]
    return cleanPCRDF


@check_types()
def create_clean_digest_df(
    digestedPiecesDF: Optional[DataFrame[schemas.MasterJ5Digests]],
    assemblyVolumeDF: DataFrame[schemas.AssemblyVolumeSchema],
) -> DataFrame[schemas.DigestsPlateSchema]:
    """Creates restriction digest instructions"""
    if digestedPiecesDF is None:
        return pd.DataFrame(
            columns=[
                "REACTION_NUMBER",
                "SEQUENCE_SOURCE",
                "SEQUENCE_LENGTH",
                "DIGEST_SOURCE_PLATE",
                "DIGEST_SOURCE_WELL",
            ]
        )
    cleanDigestDF = pd.DataFrame()
    cleanDigestDF["REACTION_NUMBER"] = np.concatenate(
        assemblyVolumeDF.loc[
            assemblyVolumeDF["TYPE"] == "Digest Linearized",
            ["TYPE_ID", "NUMBER_OF_USES"],
        ]
        .apply(
            lambda row: [row["TYPE_ID"]]
            * j5_to_echo_utils.necessaryRxnsFromUses(
                row["NUMBER_OF_USES"], MAX_WELL_USES
            ),
            axis=1,
        )
        .values
    )
    cleanDigestDF["SEQUENCE_SOURCE"] = cleanDigestDF[
        "REACTION_NUMBER"
    ].apply(
        lambda idNumber: digestedPiecesDF.loc[
            digestedPiecesDF["ID Number"] == idNumber, "Sequence Source"
        ].values[0]
    )
    cleanDigestDF["SEQUENCE_LENGTH"] = cleanDigestDF[
        "REACTION_NUMBER"
    ].apply(
        lambda idNumber: digestedPiecesDF.loc[
            digestedPiecesDF["ID Number"] == idNumber, "Length"
        ].values[0]
    )
    cleanDigestDF["DIGEST_SOURCE_PLATE"] = [
        f"digest_plate_{index//96 + 1}"
        for index in range(cleanDigestDF.shape[0])
    ]
    cleanDigestDF["DIGEST_SOURCE_WELL"] = (
        [
            f"{row}{column}"
            for row, column in itertools.product("ABCDEFGH", range(1, 13))
        ]
        * 20
    )[: cleanDigestDF.shape[0]]
    return cleanDigestDF


@check_types()
def create_assembly_volume_df(
    assemblyPartsDF: Optional[DataFrame[schemas.MasterJ5Parts]],
    skinnyAssemblyInstructionsDF: Optional[
        DataFrame[schemas.MasterJ5SkinnyAssemblies]
    ],
) -> DataFrame[schemas.AssemblyVolumeSchema]:
    """Creates a worksheet that calculates how much volume required for
    each part"""
    if assemblyPartsDF is None or skinnyAssemblyInstructionsDF is None:
        return pd.DataFrame(
            columns=[
                "PART_ID",
                "PART_NAME",
                "TYPE",
                "TYPE_ID",
                "NUMBER_OF_USES",
                "VOLUME_REQUIRED_(uL)",
            ]
        )
    tmpCounts = skinnyAssemblyInstructionsDF["Part ID"].value_counts()
    assemblyVolumeDF = pd.DataFrame()
    assemblyVolumeDF["PART_ID"] = assemblyPartsDF["ID Number"]
    assemblyVolumeDF["PART_NAME"] = assemblyPartsDF["Part(s)"]
    assemblyVolumeDF["TYPE"] = assemblyPartsDF["Type"]
    assemblyVolumeDF["TYPE_ID"] = assemblyPartsDF["Type ID Number"]
    assemblyVolumeDF["NUMBER_OF_USES"] = assemblyPartsDF[
        "ID Number"
    ].apply(lambda idNumber: tmpCounts[idNumber])
    assemblyVolumeDF["VOLUME_REQUIRED_(uL)"] = (
        assemblyVolumeDF["NUMBER_OF_USES"] * 2.0
    )  # 2 uL of each part per rxn
    return assemblyVolumeDF


@check_types()
def create_synths_plates(
    directSynthesisDF: Optional[DataFrame[schemas.MasterJ5Synthesis]],
) -> DataFrame[schemas.SynthsPlateSchema]:
    """Creates synthesis plate

    Sets up a direct synthesis plate using the instructions given in
    directSynthesisDF
    Note that directSynthesisDF and directSynthesisPlateDF are 2 different
    tables with different info in them!

    Arguments
    ---------
    directSynthesisDF: pd.DataFrame
        Table with information about the direct synthesis

    Returns
    -------
    directSynthesisPlateDF: pd.DataFrame
        A new dataframe with liquid type, well location, and volume
    """
    directSynthesisPlateLabels = [
        "PLATE ID",
        "PLATE WELL",
        "LIQUID TYPE",
        "VOLUME (uL)",
        "SEQUENCE",
    ]
    if directSynthesisDF is None:
        return pd.DataFrame(columns=directSynthesisPlateLabels)

    directSynthesisPlateLiquidType = directSynthesisDF["Name"]
    directSynthesisPlateWells = post_automation.create_well_column(
        number=directSynthesisPlateLiquidType.shape[0],
        how="row",
        plate_size=96,
    )
    directSynthesisPlateID = post_automation.create_plate_column(
        number=directSynthesisPlateLiquidType.shape[0],
        template="directSynthesiss_plate_{}",
        plate_size=96,
    )
    directSynthesisPlateVolume = [
        65
    ] * directSynthesisPlateLiquidType.shape[0]
    directSynthesisPlateSequence = directSynthesisDF["Sequence"]
    directSynthesisPlateDF = pd.DataFrame(
        list(
            zip(
                directSynthesisPlateID,
                directSynthesisPlateWells,
                directSynthesisPlateLiquidType,
                directSynthesisPlateVolume,
                directSynthesisPlateSequence,
            )
        ),
        columns=directSynthesisPlateLabels,
    )
    return directSynthesisPlateDF


@check_types()
def add_part_locations(
    assemblyPartsDF: Optional[DataFrame[schemas.MasterJ5Parts]],
    cleanPCRDF: DataFrame[schemas.PCRWorksheetSchema],
    cleanDigestDF: DataFrame[schemas.DigestsWorksheetSchema],
) -> DataFrame[schemas.AssemblyPartsSchema]:
    """Identifying source locations of parts"""
    if assemblyPartsDF is None:
        raise ValueError("No parts available?")
    assemblySourceDataFrames = {
        "PCR": cleanPCRDF,
        "Direct Synthesis/PCR": cleanPCRDF,
        "SOE": cleanPCRDF,
        "Digest Linearized": cleanDigestDF,
    }
    assemblyTypeMap = {
        "PCR": "pcr",
        "Direct Synthesis/PCR": "pcr",
        "SOE": "pcr",
        "Digest Linearized": "digest",
    }
    assemblyPartsDF["SOURCE_LOCATIONS"] = assemblyPartsDF.apply(
        lambda row: list(
            zip(
                list(
                    assemblySourceDataFrames[row["Type"]].loc[
                        assemblySourceDataFrames[row["Type"]].loc[
                            :, "REACTION_NUMBER"
                        ]
                        == row["Type ID Number"],
                        "PARTS_SOURCE_PLATE",
                    ]
                ),
                list(
                    assemblySourceDataFrames[row["Type"]].loc[
                        assemblySourceDataFrames[row["Type"]].loc[
                            :, "REACTION_NUMBER"
                        ]
                        == row["Type ID Number"],
                        "PARTS_WELL",
                    ]
                ),
            )
        ),
        axis=1,
    )
    assemblyPartsDF["PART_TYPE"] = assemblyPartsDF["Type"].apply(
        lambda j5_type: assemblyTypeMap[j5_type]
    )
    assemblyPartsDF["FIRST_PART_SOURCE_PLATE"] = assemblyPartsDF[
        "SOURCE_LOCATIONS"
    ].apply(lambda locations: locations[0][0])
    assemblyPartsDF["FIRST_PART_WELL"] = assemblyPartsDF[
        "SOURCE_LOCATIONS"
    ].apply(lambda locations: locations[0][1])
    return assemblyPartsDF


def well_to_index(well: str) -> int:
    well_clean: str = j5_to_echo_utils.convert3WellTo2Well(well)
    possible_wells: List[str] = [
        f"{row}{column}"
        for row, column in itertools.product("ABCDEFGH", range(1, 13))
    ]
    assert well_clean in possible_wells
    well_index_map = {
        letter_number: biomek_index
        for letter_number, biomek_index in zip(
            possible_wells, range(1, 97)
        )
    }
    return well_index_map[well_clean]


@check_types()
def create_echo_instructions(
    worksheet: pd.DataFrame, method: str
) -> DataFrame[schemas.EchoInstructionsSchema]:
    """Given a worksheet, create echo instructions

    Arguments
    ---------
    worksheet : pd.DataFrame
        A pandas dataframe that contains information
        about how to set up PCR or assembly rxns

    method : str
        The type of worksheet given. Can be either
        'pcr', 'assembly', or 'zag'

    Returns
    -------
    echoPlate : pd.DataFrame
        A pandas dataframe that contains echo
        instructions
    """
    if worksheet.empty:
        return pd.DataFrame(
            columns=[
                "Source Plate Name",
                "Source Well",
                "Destination Plate Name",
                "Destination Well",
                "Transfer Volume",
            ]
        )
    echoPlate = pd.DataFrame()
    if method == "pcr":
        echoPlate["Source Plate Name"] = pd.concat(
            [
                worksheet["PRIMER1_PLATE"],
                worksheet["PRIMER2_PLATE"],
                worksheet["TEMPLATE_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Source Well"] = pd.concat(
            [
                worksheet["PRIMER1_WELL"],
                worksheet["PRIMER2_WELL"],
                worksheet["TEMPLATE_WELL"],
            ],
            axis=0,
        )
        echoPlate["Destination Plate Name"] = pd.concat(
            [
                worksheet["OUTPUT_PLATE"],
                worksheet["OUTPUT_PLATE"],
                worksheet["OUTPUT_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Destination Well"] = pd.concat(
            [
                worksheet["OUTPUT_WELL"],
                worksheet["OUTPUT_WELL"],
                worksheet["OUTPUT_WELL"],
            ],
            axis=0,
        )
        echoPlate["Transfer Volume"] = pd.concat(
            [
                worksheet["PRIMER1_VOLUME"],
                worksheet["PRIMER2_VOLUME"],
                worksheet["TEMPLATE_VOLUME"],
            ],
            axis=0,
        )
    elif method == "assembly":
        echoPlate = worksheet.loc[
            :,
            [
                "Source Plate",
                "Source Well",
                "Destination Plate",
                "Destination Well",
            ],
        ]
        echoPlate["Transfer Volume"] = 2000  # nL
        echoPlate = echoPlate.rename(
            columns={
                "Source Plate": "Source Plate Name",
                "Destination Plate": "Destination Plate Name",
            }
        )
    elif method == "equimolar":
        echoPlate = worksheet.loc[
            :,
            [
                "Source Plate",
                "Source Well",
                "Destination Plate",
                "Destination Well",
                "Transfer Volume",
            ],
        ]
        echoPlate = echoPlate.rename(
            columns={
                "Source Plate": "Source Plate Name",
                "Destination Plate": "Destination Plate Name",
            }
        )
    elif method == "zag":
        echoPlate = worksheet.loc[
            :,
            ["PARTS_SOURCE_PLATE", "PARTS_WELL", "ZAG_PLATE", "ZAG_WELL"],
        ].copy()
        echoPlate["Transfer Volume"] = 500
        echoPlate.columns = [
            "Source Plate Name",
            "Source Well",
            "Destination Plate Name",
            "Destination Well",
            "Transfer Volume",
        ]
    elif method == "custom":
        partColumnHeaders = [
            column
            for column in worksheet.columns
            if (column.startswith("Part(s)"))
            and (not column.endswith(("ID", "Source Plate", "Well")))
        ]
        echoPlate["Source Plate Name"] = pd.concat(
            [
                worksheet[f"{part} Source Plate"]
                for part in partColumnHeaders
            ],
            axis=0,
        )
        echoPlate["Source Well"] = pd.concat(
            [worksheet[f"{part} Well"] for part in partColumnHeaders],
            axis=0,
        )
        echoPlate["Destination Plate Name"] = pd.concat(
            [worksheet["Assembly Plate"] for part in partColumnHeaders],
            axis=0,
        )
        echoPlate["Destination Well"] = pd.concat(
            [worksheet["Assembly Well"] for part in partColumnHeaders],
            axis=0,
        )
        echoPlate["Transfer Volume"] = 2000  # nL
    elif method == "quant":
        echoPlate = worksheet.loc[
            :,
            [
                "PART_PLATE",
                "PART_WELL",
                "QUANT_PLATE",
                "QUANT_WELL",
                "QUANT_VOLUME",
            ],
        ].copy()
        echoPlate.columns = [
            "Source Plate Name",
            "Source Well",
            "Destination Plate Name",
            "Destination Well",
            "Transfer Volume",
        ]
    elif method == "redo_pcr":
        echoPlate["Source Plate Name"] = pd.concat(
            [
                worksheet["PRIMER1_PLATE"],
                worksheet["PRIMER2_PLATE"],
                worksheet["TEMPLATE_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Source Well"] = pd.concat(
            [
                worksheet["PRIMER1_WELL"],
                worksheet["PRIMER2_WELL"],
                worksheet["TEMPLATE_WELL"],
            ],
            axis=0,
        )
        echoPlate["Destination Plate Name"] = pd.concat(
            [
                worksheet["REDO_PLATE"],
                worksheet["REDO_PLATE"],
                worksheet["REDO_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Destination Well"] = pd.concat(
            [
                worksheet["REDO_WELL"],
                worksheet["REDO_WELL"],
                worksheet["REDO_WELL"],
            ],
            axis=0,
        )
        echoPlate["Transfer Volume"] = pd.concat(
            [
                worksheet["PRIMER1_VOLUME"],
                worksheet["PRIMER2_VOLUME"],
                worksheet["TEMPLATE_VOLUME"],
            ],
            axis=0,
        )
    elif method == "colony_pcr":
        echoPlate["Source Plate Name"] = pd.concat(
            [
                worksheet["PRIMER1_PLATE"],
                worksheet["PRIMER2_PLATE"],
                worksheet["NGS_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Source Well"] = pd.concat(
            [
                worksheet["PRIMER1_WELL"],
                worksheet["PRIMER2_WELL"],
                worksheet["NGS_WELL"],
            ],
            axis=0,
        )
        echoPlate["Destination Plate Name"] = pd.concat(
            [
                worksheet["COLONY_PCR_PLATE"],
                worksheet["COLONY_PCR_PLATE"],
                worksheet["COLONY_PCR_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Destination Well"] = pd.concat(
            [
                worksheet["COLONY_PCR_WELL"],
                worksheet["COLONY_PCR_WELL"],
                worksheet["COLONY_PCR_WELL"],
            ],
            axis=0,
        )
        echoPlate["Transfer Volume"] = pd.concat(
            [
                worksheet["PRIMER1_VOLUME"],
                worksheet["PRIMER2_VOLUME"],
                worksheet["NGS_VOLUME"],
            ],
            axis=0,
        )
    echoPlate = (
        echoPlate.dropna()
        .sort_values(
            [
                "Source Plate Name",
                "Destination Plate Name",
                "Source Well",
                "Destination Well",
            ],
            ascending=[True, True, True, True],
        )
        .reset_index(drop=True)
    )
    return echoPlate


@check_types()
def create_templates_plates(
    pcr_df: Optional[DataFrame[schemas.MasterJ5PCRs]],
) -> DataFrame[schemas.TemplatesPlateSchema]:
    """Parse the required templates from the pcr section and make a
    template plate

    Creates a template plate worksheet using the template list in
    pcr_df.

    Arguments
    ---------
    pcr_df: pd.DataFrame
        This contains a list of templates which we use to create
        our plate.

    Returns
    -------
    templatePlateDF: pd.DataFrame
        Information about one particular template plate. Describes
        what's in each
        well and how much volume of it there is.
    """
    templatePlateLabels = [
        "PLATE ID",
        "PLATE WELL",
        "LIQUID TYPE",
        "VOLUME (uL)",
    ]
    if pcr_df is None:
        return pd.DataFrame(columns=templatePlateLabels)
    templatePlateLiquidType = np.sort(pcr_df["Primary Template"].unique())
    templatePlateWells = post_automation.create_well_column(
        number=templatePlateLiquidType.shape[0], how="row", plate_size=384
    )
    templatePlateID = post_automation.create_plate_column(
        number=templatePlateLiquidType.shape[0],
        template="templates_plate_{}",
        plate_size=384,
    )
    templatePlateVolume = [65] * templatePlateLiquidType.shape[0]
    templatePlateDF = pd.DataFrame(
        list(
            zip(
                templatePlateID,
                templatePlateWells,
                templatePlateLiquidType,
                templatePlateVolume,
            )
        ),
        columns=templatePlateLabels,
    )
    return templatePlateDF


@check_types()
def create_oligos_plates(
    oligos: Optional[DataFrame[schemas.MasterJ5Oligos]],
) -> DataFrame[schemas.OligosPlateSchema]:
    """Parse the oligo from the oligo section and make an oligo plate

    Creates an oligo plate worksheet using the given list of oligos

    Arguments
    ---------
    oligos: pd.DataFrame
        Basically just a list of oligos

    Returns
    -------
    oligoPlateDF: pd.DataFrame
        Information about one particular oligo plate. Describes what's in
        each well and how much volume of it there is.
    """
    oligoPlateLabels = [
        "PLATE ID",
        "PLATE WELL",
        "LIQUID TYPE",
        "VOLUME (uL)",
    ]
    if oligos is None:
        return pd.DataFrame(columns=oligoPlateLabels)
    oligoPlateLiquidType = np.sort(oligos["Name"].unique())
    oligoPlateWells = post_automation.create_well_column(
        number=oligoPlateLiquidType.shape[0], how="row", plate_size=384
    )
    oligoPlateID = post_automation.create_plate_column(
        number=oligoPlateLiquidType.shape[0],
        template="oligos_plate_{}",
        plate_size=384,
    )
    oligoPlateVolume = [65] * oligoPlateLiquidType.shape[0]
    oligoPlateDF = pd.DataFrame(
        list(
            zip(
                oligoPlateID,
                oligoPlateWells,
                oligoPlateLiquidType,
                oligoPlateVolume,
            )
        ),
        columns=oligoPlateLabels,
    )
    return oligoPlateDF


@check_types()
def create_oligos_order_form(
    oligoPlateDF: DataFrame[schemas.OligosPlateSchema],
    oligos: Optional[DataFrame[schemas.MasterJ5Oligos]],
    size: int = 96,
) -> DataFrame[schemas.OligosOrderSchema]:
    """Makes a list of oligo sequences to order

    The DataFrame that's returned is essentially a shopping list
    for oligos.

    Arguments
    ---------
    oligoPlateDF: pd.DataFrame
        Information about one particular oligo plate. Describes what's
        in each
        well and how much volume of it there is.

    oligos: pd.DataFrame
        A list of oligo names

    size: int
        How many wells are in the plate. Default 96 but can also be 384.

    Returns
    -------
    oligoOrderDF: pd.DataFrame
        Table listing oligo names and their locations in the well
        in addition to the sequence of each oligo.
    """
    if size not in [96, 384]:
        raise ValueError(f"Not possible size of oligo order plate: {size}")
    if oligos is None:
        return pd.DataFrame(
            columns=[
                "Plate",
                "Well Position",
                "Name",
                "Sequence",
                "Length",
            ]
        )
    oligoOrderDF = pd.DataFrame()
    if size == 96:
        oligoOrderDF["Well Position"] = oligoPlateDF["PLATE WELL"].apply(
            j5_to_echo_utils.unstampOligos
        )
    else:
        oligoOrderDF["Well Position"] = oligoPlateDF["PLATE WELL"]
    oligoOrderDF["Name"] = oligoPlateDF["LIQUID TYPE"]
    oligoOrderDF["Sequence"] = oligoPlateDF["LIQUID TYPE"].apply(
        lambda oligo: oligos.loc[
            oligos["Name"] == oligo, "Sequence"
        ].values[0]
    )
    oligoOrderDF["Plate"] = [
        f"oligo_order_plate_{i//size + 1}"
        for i in range(oligoOrderDF.shape[0])
    ]
    oligoOrderDF["Length"] = oligoOrderDF["Sequence"].apply(len)
    return oligoOrderDF.loc[
        :, ["Plate", "Well Position", "Name", "Sequence", "Length"]
    ]


def to_excel_bytestring(df: pd.DataFrame, sheet_name: str = None) -> bytes:
    output = io.BytesIO()
    writer = pd.ExcelWriter(output)
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()
    return output.getvalue()


@check_types()
def create_clean_part_df(
    parts: Optional[DataFrame[schemas.MasterJ5Parts]],
    clean_pcr_df: DataFrame[schemas.PCRWorksheetSchema],
    clean_digest_df: DataFrame[schemas.DigestsWorksheetSchema],
) -> DataFrame[schemas.PartsPlateSchema]:
    if parts is None:
        raise ValueError("No parts available")
    clean_pcr_df["PART_TYPE"] = "pcr"
    clean_digest_df["PART_TYPE"] = "digest"
    clean_part_df = pd.concat(
        (
            clean_digest_df.rename(
                columns={
                    "DIGEST_SOURCE_PLATE": "SOURCE_PLATE",
                    "DIGEST_SOURCE_WELL": "SOURCE_WELL",
                    "PARTS_SOURCE_PLATE": "PART_PLATE",
                    "PARTS_WELL": "PART_WELL",
                    "SEQUENCE_LENGTH": "PART_LENGTH",
                    "REACTION_NUMBER": "SOURCE_ID",
                }
            ).loc[
                :,
                [
                    "PART_PLATE",
                    "PART_WELL",
                    "PART_LENGTH",
                    "PART_TYPE",
                    "SOURCE_ID",
                    "SOURCE_PLATE",
                    "SOURCE_WELL",
                ],
            ],
            clean_pcr_df.rename(
                columns={
                    "OUTPUT_PLATE": "SOURCE_PLATE",
                    "OUTPUT_WELL": "SOURCE_WELL",
                    "PARTS_SOURCE_PLATE": "PART_PLATE",
                    "PARTS_WELL": "PART_WELL",
                    "EXPECTED_SIZE": "PART_LENGTH",
                    "REACTION_NUMBER": "SOURCE_ID",
                }
            ).loc[
                :,
                [
                    "PART_PLATE",
                    "PART_WELL",
                    "PART_LENGTH",
                    "PART_TYPE",
                    "SOURCE_ID",
                    "SOURCE_PLATE",
                    "SOURCE_WELL",
                ],
            ],
        )
    )
    clean_part_df["PART_ID"] = clean_part_df.apply(
        lambda row: parts.loc[
            (parts["PART_TYPE"] == row["PART_TYPE"])
            & (parts["Type ID Number"] == row["SOURCE_ID"]),
            "ID Number",
        ].values[0],
        axis=1,
    )
    clean_part_df["PART_NAME"] = clean_part_df.apply(
        lambda row: parts.loc[
            (parts["PART_TYPE"] == row["PART_TYPE"])
            & (parts["Type ID Number"] == row["SOURCE_ID"]),
            "Part(s)",
        ].values[0],
        axis=1,
    )
    return clean_part_df.loc[
        :,
        [
            "PART_PLATE",
            "PART_WELL",
            "PART_ID",
            "PART_NAME",
            "PART_LENGTH",
            "PART_TYPE",
            "SOURCE_ID",
            "SOURCE_PLATE",
            "SOURCE_WELL",
        ],
    ]


def create_dpni_instructions(
    clean_pcr_df: pd.DataFrame,
    names: Tuple[str, str] = ("OUTPUT_PLATE", "OUTPUT_WELL"),
) -> pd.DataFrame:
    dest_df: pd.DataFrame = clean_pcr_df.loc[:, names].rename(
        columns={names[0]: "dest_pos", names[1]: "dest_well"}
    )
    dest_df["dest_well"] = (
        dest_df["dest_well"].apply(well_to_index).astype(str) + ", "
    )
    dest_df = (
        dest_df.groupby("dest_pos")
        .agg("sum")
        .reset_index()
        .sort_values("dest_pos")
    )
    dest_df["dest_pos"] = [f"dest_{i+1}" for i in range(dest_df.shape[0])]
    dest_plt_num: int = dest_df["dest_pos"].size
    sample_num: int = clean_pcr_df.shape[0]
    final_df: pd.DataFrame = pd.DataFrame(
        {
            "variable_name_1": ["dest_plt_num", "sample_num"],
            "value_1": [dest_plt_num, sample_num],
        }
    )
    final_df = final_df.join(dest_df)
    return final_df


def create_assembly_instructions(
    construct_worksheet: DataFrame[schemas.ConstructWorksheetSchema],
    names: Tuple[str, str] = ("src_plate", "src_well"),
) -> pd.DataFrame:
    dest_df: pd.DataFrame = construct_worksheet.loc[:, names].rename(
        columns={names[0]: "dest_pos", names[1]: "dest_well"}
    )
    dest_df["dest_well"] = (
        dest_df["dest_well"].apply(well_to_index).astype(str) + ", "
    )
    dest_df = dest_df.groupby("dest_pos").agg("sum").reset_index()
    dest_plt_num: int = dest_df["dest_pos"].size
    sample_num: int = construct_worksheet.shape[0]
    final_df: pd.DataFrame = pd.DataFrame(
        {
            "variable_name": ["dest_plt_num", "sample_num"],
            "value": [dest_plt_num, sample_num],
        }
    )
    final_df = final_df.join(dest_df)
    biomek_plate_mapping: dict = {
        plate: f"dest_{i+1}"
        for i, plate in enumerate(final_df["dest_pos"].values)
        if not pd.isnull(plate)
    }
    final_df["dest_pos"] = final_df["dest_pos"].apply(
        lambda old_plate_name: biomek_plate_mapping[old_plate_name]
        if not pd.isnull(old_plate_name)
        else np.nan
    )
    return final_df


def create_bead_instructions(clean_pcr_df: pd.DataFrame) -> pd.DataFrame:
    bead_df = pd.DataFrame(
        columns=(
            "Bead_Reservoir",
            "Bead_Res_Section",
            "Biorad_Dest_Plate",
            "Biorad_Dest_Well",
            "Bead_Transfer_Vol",
            "PCR_Source_plate",
            "PCR_Source_Well",
            "PCR_Transfer_Vol",
            "Waste",
            "Section2 ",
            "Supernatant removal volume",
        )
    )
    default_row_dict = {
        "Bead_Reservoir": "Bead_Res_40",
        "Bead_Res_Section": 1,
        "Biorad_Dest_Plate": "Samples",
        "Biorad_Dest_Well": "",
        "Bead_Transfer_Vol": 39,
        "PCR_Source_plate": "Sample_PCR",
        "PCR_Source_Well": "",
        "PCR_Transfer_Vol": 30,
        "Waste": "Waste_container",
        "Section2 ": 1,
        "Supernatant removal volume": 69,
    }
    default_row_series = pd.Series(default_row_dict)
    for i in range(len(clean_pcr_df)):
        bead_df.loc[i] = default_row_series
    bead_df["PCR_Source_Well"] = clean_pcr_df["OUTPUT_WELL"].apply(
        j5_to_echo_utils.convert3WellTo2Well
    )
    bead_df["Biorad_Dest_Well"] = clean_pcr_df["OUTPUT_WELL"].apply(
        j5_to_echo_utils.convert3WellTo2Well
    )
    return bead_df


def create_biomek_pcr_instructions(
    cleanPCRDF: pd.DataFrame,
) -> pd.DataFrame:
    totalVolume = 30  # uL
    dnaVolume = 0.6  # 0.25 + 0.25 + 0.1 uL DNA
    mmVolume = totalVolume / 2  # uL of 2X MM
    waterVolume = totalVolume - dnaVolume - mmVolume
    mmTubeVolume = 2  # mL

    for pcrPlate in cleanPCRDF["OUTPUT_PLATE"].unique():
        # tmpPlateDF = cleanPCRDF.loc[
        #     cleanPCRDF["OUTPUT_PLATE"] == pcrPlate, :
        # ]
        tmpBiomekWells = cleanPCRDF["OUTPUT_WELL"].apply(
            j5_to_echo_utils.convertWellToBiomekNumber
        )
        templateDF = pd.DataFrame(
            {
                "Variable_name": [
                    "Email_to",
                    "ExpID",
                    "Samples",
                    "DNA_vol",
                    "Water_vol",
                    "Water_reqVol",
                    "MasterMix_Vol",
                    "MasterMix_reqVol",
                ],
                "Value": [
                    settings.FIRST_SUPERUSER,
                    "PCR",
                    tmpBiomekWells.shape[0],
                    dnaVolume,  # uL DNA
                    waterVolume,  # uL watts
                    tmpBiomekWells.shape[0]
                    * waterVolume
                    / 1000
                    / 0.9,  # mL watts
                    mmVolume,  # uL 2X MM
                    tmpBiomekWells.shape[0]
                    * mmVolume
                    / 1000
                    / 0.9,  # mL watts
                ],
            }
        )
        templateDF = pd.concat(
            [templateDF, tmpBiomekWells], axis=1
        ).rename(columns={"OUTPUT_WELL": "Well_user"})
        templateDF["Well"] = templateDF["Well_user"]
        templateDF["Src_vol"] = templateDF["Well"].apply(
            lambda well: dnaVolume if not pd.isna(well) else np.nan
        )
        templateDF["MasterMix_well"] = templateDF.apply(
            lambda row: (row.name + 1)
            * mmVolume
            // (mmTubeVolume * 0.9 * 1000)
            + 1
            if not pd.isna(row["Well_user"])
            else np.nan,
            axis=1,
        )
        templateDF["MasterMix_TFFvol"] = templateDF["Well"].apply(
            lambda well: mmVolume if not pd.isna(well) else np.nan
        )
    return templateDF


@check_types()
def gather_construct_worksheet(
    assembly_worksheet: DataFrame[schemas.AssemblyWorksheetSchema],
) -> DataFrame[schemas.ConstructWorksheetSchema]:
    construct_worksheet = (
        assembly_worksheet.loc[
            :,
            [
                "Number",
                "Name",
                "Parts Summary",
                "Assembly Method",
                "Destination Plate",
                "Destination Well",
            ],
        ]
        .groupby("Number")
        .first()
        .reset_index()
        .rename(
            columns={
                "Number": "j5_construct_id",
                "Name": "name",
                "Parts Summary": "parts",
                "Assembly Method": "assembly_method",
                "Destination Plate": "src_plate",
                "Destination Well": "src_well",
            }
        )
    )
    return construct_worksheet


def create_quant_worksheet(
    parts_plate: DataFrame[schemas.PartsPlateSchema],
) -> DataFrame[schemas.PartsWorksheetSchema]:
    parts_plate["QUANT_PLATE"] = [
        f"quant_plate_{index//88 + 1}"
        for index in range(parts_plate.shape[0])
    ]
    parts_plate["QUANT_WELL"] = (
        [
            f"{row}{column}"
            for row, column in list(
                itertools.product("ABCDEFGH", range(1, 12))
            )
        ]
        * 20
    )[: parts_plate.shape[0]]
    parts_plate["QUANT_VOLUME"] = 1000
    parts_plate[
        "Conc (ng/uL)"
    ] = 50  # Assume each PCR Rxn is 50 ng/uL initially
    return parts_plate


def index_to_384_well(index: int) -> str:
    index = int(index % 384)
    possible_wells: List[str] = [
        f"{row}{column}"
        for row, column in itertools.product(
            "ABCDEFGHIJKLMNOP", range(1, 25)
        )
    ]
    index_well_map = {
        biomek_index: letter_number
        for letter_number, biomek_index in zip(
            possible_wells, range(1, 385)
        )
    }
    return index_well_map[index]


def optimize_equimolar_assembly_rxn(
    conc: np.ndarray, max_vol: float, max_fmol: float
) -> np.ndarray:
    """
    Arguments
    ---------
    conc: np.array
        Concentrations of each part in a reaction

    max_vol: float
        Max total volume allowed for reaction (in uL)

    max_fmol: float
        Max amount of part used for reaction (in fmols)
    """
    # Objective: maximize mols used subject to following constraints
    c: np.ndarray = conc * -1

    # Each part has maximum mol
    A_ub: np.ndarray = np.diag(c * -1)
    b_ub: np.ndarray = np.full(c.size, fill_value=max_fmol)

    # Total volume of all parts should be less than max_vol
    A_ub = np.vstack([A_ub, np.ones(c.size)])
    b_ub = np.hstack([b_ub, np.array([max_vol])])

    # Each part should use equal mol
    A_eq: np.ndarray = np.eye(N=c.size - 1, M=c.size, k=1)
    np.fill_diagonal(A_eq, -1.0)
    A_eq = A_eq * c

    b_eq: np.ndarray = np.zeros(c.size - 1)

    # Each part volume should be non-negative and under the max volume
    bounds: Tuple[float, Optional[float]] = (0, max_vol)

    # Perform optimization
    result: OptimizeResult = linprog(
        c=c,
        A_ub=A_ub,
        b_ub=b_ub,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        options={"cholesky": False, "sym_pos": False},
    )
    volumes: np.ndarray = np.zeros(c.size)
    if not result.status:
        volumes = result.x
    return volumes


def add_water_to_assembly(
    assembly_worksheet: pd.DataFrame,
    max_vol: float = 5.0,  # uL
    volume_column: str = "EQUIMOLAR_VOLUME",
) -> pd.DataFrame:
    water_required = (
        max_vol
        - assembly_worksheet.groupby("Number").agg({volume_column: "sum"})
    ).reset_index()
    water_required["Part Name"] = "water"
    water_required["Destination Plate"] = water_required["Number"].apply(
        lambda number: assembly_worksheet.loc[
            assembly_worksheet["Number"] == number, "Destination Plate"
        ].values[0]
    )
    water_required["Destination Well"] = water_required["Number"].apply(
        lambda number: assembly_worksheet.loc[
            assembly_worksheet["Number"] == number, "Destination Well"
        ].values[0]
    )
    water_required = water_required.loc[
        ~np.isclose(water_required[volume_column], 0.0, atol=1e-3), :
    ]
    water_required["Source Plate"] = "water_plate"
    water_required["Source Well"] = (
        water_required[volume_column].cumsum() // 45
    ) + 1
    water_required["Source Plate"] = water_required["Source Well"].apply(
        lambda well: f"water_plate_{int(well//384)+1}"
    )
    water_required["Source Well"] = water_required["Source Well"].apply(
        index_to_384_well
    )
    return assembly_worksheet.append(water_required)


def create_equimolar_assembly_instructions(
    assembly_df: DataFrame[schemas.AssemblyWorksheetSchema],
    quant_df: DataFrame[schemas.PartsWorksheetSchema],
    max_fmol: float = 100.0,
    max_vol: float = 5.0,
    max_part_percentage: float = 1.0,
) -> DataFrame[schemas.EquimolarAssemblyWorksheetSchema]:
    equimolar_worksheet = assembly_df.merge(
        quant_df,
        left_on=["Source Plate", "Source Well"],
        right_on=["PART_PLATE", "PART_WELL"],
    ).sort_values(["Number", "Part Order"])
    # Formula from: https://nebiocalculator.neb.com/#!/dsdnaamt
    equimolar_worksheet["Conc (fmol/uL)"] = (
        (equimolar_worksheet["Conc (ng/uL)"] * 1e-6)
        / ((equimolar_worksheet["PART_LENGTH"] * 617.96) + 36.04)
    ) * 1e12
    equimolar_worksheet["EQUIMOLAR_VOLUME"] = 0

    for rxn in equimolar_worksheet["Number"].unique():
        conc: np.ndarray = equimolar_worksheet.loc[
            equimolar_worksheet["Number"] == rxn, "Conc (fmol/uL)"
        ].values
        vol: np.ndarray = optimize_equimolar_assembly_rxn(
            conc=conc,
            max_vol=max_vol * max_part_percentage,
            max_fmol=max_fmol,
        )
        equimolar_worksheet.loc[
            equimolar_worksheet["Number"] == rxn, "EQUIMOLAR_VOLUME"
        ] = vol
    equimolar_worksheet["fmol_used"] = (
        equimolar_worksheet["Conc (fmol/uL)"]
        * equimolar_worksheet["EQUIMOLAR_VOLUME"]
    )
    equimolar_worksheet = add_water_to_assembly(
        assembly_worksheet=equimolar_worksheet,
        max_vol=max_vol,
        volume_column="EQUIMOLAR_VOLUME",
    )
    equimolar_worksheet["Transfer Volume"] = (
        equimolar_worksheet["EQUIMOLAR_VOLUME"] * 1000
    ).map(int)
    return equimolar_worksheet


@dataclass
class RegistryOptions:
    principal_investigator: str
    principal_investigator_email: str
    intellectual_property: str
    biosafety_level: int
    keywords: str
    notes: str
    status: str 
    strain_name_prefix: str 
    creator: str
    creator_email: str
    host: str  
    genotype: str 
    circular: bool
    selection_marker: str
    strain_selection_marker: str
    backbone: str
    replicates_in: str
    ori: str
    promoters: str
    plasmid_use: str


DEFAULT_REGISTRY_OPTIONS: RegistryOptions = RegistryOptions(
    principal_investigator="Principal Investigator Name",
    principal_investigator_email="Principal Investigator Email",
    intellectual_property="N/A",
    biosafety_level=1,
    keywords="",
    notes="",
    status="In Progress",
    strain_name_prefix="strain_",
    creator="Creator Name",
    creator_email="Creator Email",
    host="E. coli",
    genotype="DH5-alpha",
    circular=True,
    selection_marker="kan",
    strain_selection_marker="kan",
    backbone="pET28",
    replicates_in="E. coli",
    ori="colE1",
    promoters="T7",
    plasmid_use="expression",
)


def create_registry_submission_form(
    construct_worksheet: DataFrame[schemas.ConstructWorksheetSchema],
    options: RegistryOptions = DEFAULT_REGISTRY_OPTIONS,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    plasmid_name = construct_worksheet["name"]
    strain_name = [
        f"{options.strain_name_prefix}{i}"
        for i in range(plasmid_name.shape[0])
    ]
    summary = "Plasmid consisting of parts: " + construct_worksheet[
        "parts"
    ].astype(str)
    strain_summary = f"{options.host} carrying " + summary
    sequence_file = plasmid_name + ".gb"
    registry_form = pd.DataFrame(
        collections.OrderedDict(
            [
                ("Principal Investigator", options.principal_investigator),
                (
                    "Principal Investigator Email",
                    options.principal_investigator_email,
                ),
                ("Intellectual Property", options.intellectual_property),
                ("BioSafety Level", options.biosafety_level),
                ("Name", strain_name),
                ("Keywords", options.keywords),
                ("Summary", strain_summary),
                ("Notes", options.notes),
                ("Status", options.status),
                ("Creator", options.creator),
                ("Creator Email", options.creator_email),
                ("Genus and Species", options.host),
                ("Genotype or Phenotype", options.genotype),
                ("Selection Markers", options.strain_selection_marker),
                (
                    "Plasmid Principal Investigator",
                    options.principal_investigator,
                ),
                (
                    "Plasmid Principal Investigator Email",
                    options.principal_investigator_email,
                ),
                (
                    "Plasmid Intellectual Property",
                    options.intellectual_property,
                ),
                ("Plasmid BioSafety Level", options.biosafety_level),
                ("Plasmid Name", plasmid_name),
                ("Plasmid Keywords", options.keywords),
                ("Plasmid Summary", summary),
                ("Plasmid Notes", options.notes),
                ("Plasmid Status", options.status),
                ("Plasmid Creator", options.creator),
                ("Plasmid Creator Email", options.creator_email),
                ("Plasmid Circular", options.circular),
                ("Plasmid Backbone", options.backbone),
                ("Plasmid Promoters", options.promoters),
                ("Plasmid Replicates In", options.replicates_in),
                ("Plasmid Origin of Replication", options.ori),
                ("Plasmid Selection Marker", options.selection_marker),
                ("Plasmid Plasmid Use", options.plasmid_use),
                # ("Plasmid Sequence File", sequence_file)
            ]
        )
    )
    registry_sequence = pd.DataFrame(
        {"Plasmid Sequence File": sequence_file}
    )
    return registry_form, registry_sequence


def create_oligos_96(
    oligos_plate: pd.DataFrame, oligos_order_96: pd.DataFrame
) -> pd.DataFrame:
    biomek_oligos_plate: pd.DataFrame = oligos_plate.merge(
        oligos_order_96,
        how="left",
        left_on="LIQUID TYPE",
        right_on="Name",
    )
    biomek_oligos_plate["PLATE ID"] = biomek_oligos_plate["Plate"].apply(
        lambda name: f'backup_oligos_plate_{name.split("_")[-1]}'
    )
    biomek_oligos_plate["PLATE WELL"] = biomek_oligos_plate[
        "Well Position"
    ]
    biomek_oligos_plate["VOLUME (uL)"] = 1500
    return biomek_oligos_plate.loc[
        :, ["PLATE ID", "PLATE WELL", "LIQUID TYPE", "VOLUME (uL)"]
    ]


def create_templates_96(templates_plate: pd.DataFrame) -> pd.DataFrame:
    biomek_templates_plate: pd.DataFrame = templates_plate.copy()
    biomek_templates_plate["PLATE WELL"] = templates_plate[
        "PLATE WELL"
    ].apply(j5_to_echo_utils.unstamp)
    biomek_templates_plate["PLATE ID"] = [
        f"backup_templates_plate_{i//96 + 1}"
        for i in range(biomek_templates_plate.shape[0])
    ]
    biomek_templates_plate["VOLUME (uL)"] = 1500
    return biomek_templates_plate
