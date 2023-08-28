#!/usr/bin/env python3

import csv
import io
import json
import logging
import shutil
import tempfile
import zipfile
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from fastapi import UploadFile

from dnada import models

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_condense_assembly_files_input(
    designs: List[models.Design],
) -> Tuple[bytes, bytes]:
    individual_design_csvs = []
    with tempfile.NamedTemporaryFile() as tmp:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as archive:
            for design in designs:
                if hasattr(design, "rawdesign"):
                    design_data = design.rawdesign.data
                else:
                    design_data = design["rawdesign"]["data"]  # type: ignore  # noqa
                for key in design_data.keys():
                    if (
                        key.endswith(".csv")
                        and key.startswith("p")
                        and not key.startswith("partslist")
                    ):
                        individual_design_csvs.append(key)
                        archive.writestr(key, design_data[key])
        tmp.seek(0)
        encoded_assembly_files_zip = tmp.read()
    encoded_assembly_files_list = (
        pd.DataFrame(individual_design_csvs, columns=["Assembly File Name"])
        .sort_values("Assembly File Name")
        .to_csv(index=False)
        .encode("utf-8")
    )
    return encoded_assembly_files_list, encoded_assembly_files_zip


def gather_genbanks(designs: List[models.Design]) -> Dict[str, str]:
    genbanks: Dict[str, str] = dict()
    for design in designs:
        if hasattr(design, "rawdesign"):
            design_data = design.rawdesign.data
        else:
            design_data = design["rawdesign"]["data"]  # type: ignore  # noqa
        for key in design_data.keys():
            if key.endswith(".gb"):
                genbanks[key] = design_data[key]
    return genbanks


def process_zip(zip_handle):
    json_handle = {}
    with tempfile.NamedTemporaryFile(delete=True, suffix=".zip") as tmp:
        shutil.copyfileobj(zip_handle, tmp)
        zip_file = zipfile.ZipFile(tmp, mode="r")
        for subfile in zip_file.namelist():
            json_handle[subfile] = zip_file.read(subfile).decode("utf-8")
    return json_handle


def parse_assembly_instructions(items):
    assemblyInstructionsRawText = [
        item for item in items if item.startswith("Combinations of Assembly Pieces")
    ][0]
    assemblyInstructionsDF = pd.read_csv(
        io.StringIO(assemblyInstructionsRawText),
        sep=",",
        header=0,
        skiprows=2,
    )
    assemblyInstructionsDF = assemblyInstructionsDF.rename(
        columns={
            "Part(s)": "Part(s).0",
            "Assembly Piece ID Number": "Assembly Piece ID Number.0",
        }
    )

    skinnyAssemblyInstructions = pd.DataFrame()
    for i in range(int((assemblyInstructionsDF.shape[1] - 3) / 2)):
        tmp = (
            assemblyInstructionsDF.melt(
                id_vars=["Number", "Name", "Assembly Method"],
                value_vars=[f"Part(s).{i}"],
                value_name="Part Name",
            )
            .drop(columns=["variable"])
            .merge(
                assemblyInstructionsDF.melt(
                    id_vars=["Number", "Name", "Assembly Method"],
                    value_vars=[f"Assembly Piece ID Number.{i}"],
                    value_name="Part ID",
                ).drop(columns=["variable"]),
                on=["Number", "Name", "Assembly Method"],
            )
        )
        tmp["Part Order"] = i
        skinnyAssemblyInstructions = skinnyAssemblyInstructions.append(tmp)
    skinnyAssemblyInstructions = (
        skinnyAssemblyInstructions.dropna()
        .sort_values(["Number", "Part Order"])
        .reset_index(drop=True)
    )
    return skinnyAssemblyInstructions.to_json()


def process_combinatorial_csv(csv_handle):
    json_handle = {}
    # Read condensed J5 File
    rawText = csv.reader(csv_handle, delimiter=",", dialect="excel")
    # Split into chunks
    cleanTxt = "\n".join([",".join(row).rstrip(",").lstrip('"') for row in rawText])
    items = cleanTxt.split("\n\n")
    # Get Oligos, Synths, Digests, PCRs
    for name, header in zip(
        ["oligos", "digests", "synths", "pcrs"],
        [
            "Oligo Synthesis",
            "Digest Linearized Pieces",
            "Direct Synthesis",
            "PCR Reactions",
        ],
    ):
        try:
            rawText = [item for item in items if item.startswith(header)][0]
            jsonText = pd.read_csv(
                io.StringIO(rawText), sep=",", header=0, skiprows=1
            ).to_json()
        except IndexError:
            jsonText = "{}"
        json_handle[name] = jsonText
    # Get Parts
    # Have to account for when multiple assembly methods are being used
    try:
        assemblyPartsRawText = [
            item for item in items if item.startswith("Assembly Pieces")
        ]
        assemblyPartsDFs = [
            pd.read_csv(io.StringIO(methodPieces), sep=",", header=0, skiprows=1)
            for methodPieces in assemblyPartsRawText
        ]
        assemblyPartsDF = (
            assemblyPartsDFs[0]
            if len(assemblyPartsDFs) == 1
            else assemblyPartsDFs[0]
            .append(assemblyPartsDFs[1:], sort=False)
            .sort_values(by="ID Number")
            .reset_index(drop=True)
        )
        partJsonText = assemblyPartsDF.to_json()
    except IndexError:
        partJsonText = "{}"
    json_handle["parts"] = partJsonText
    # Get Assemblys
    # Have to skinnify original table design
    try:
        assemblyJsonText = parse_assembly_instructions(items)
    except IndexError:
        assemblyJsonText = "{}"
    except KeyError:
        assemblyJsonText = "{}"
    json_handle["assemblys"] = assemblyJsonText
    csv_handle.seek(0)
    json_handle["raw_csv"] = csv_handle.read()
    return json_handle


def process_design_upload(
    upload_file: UploadFile, write: Optional[str] = None
) -> Dict[str, Any]:
    with tempfile.NamedTemporaryFile(delete=True, suffix=".zip") as tmp:
        shutil.copyfileobj(upload_file.file, tmp)
        zip_file = zipfile.ZipFile(tmp, mode="r")
        zip_json = {"zip_file_name": upload_file.filename}
        for subfile in zip_file.namelist():
            if subfile.endswith((".gb", ".eug")):
                zip_json[subfile] = zip_file.read(subfile).decode("utf8")
            elif subfile.endswith("combinatorial.csv"):
                csv_file = io.StringIO(zip_file.read(subfile).decode("utf8"))
                zip_json["combinatorial"] = process_combinatorial_csv(csv_file)
                zip_json["combinatorial"]["name"] = subfile
            elif subfile.endswith(".csv"):
                csv_text = zip_file.read(subfile).decode("utf8")
                try:
                    df = pd.read_csv(io.StringIO(csv_text)).to_json()
                except pd.errors.ParserError:
                    df = csv_text
                zip_json[subfile] = df
            elif subfile.endswith(".zip"):
                zip_json[subfile] = process_zip(io.BytesIO(zip_file.read(subfile)))
    if write:
        with open(write, "w") as F:
            json.dump(zip_json, F, indent=2)
    return zip_json
