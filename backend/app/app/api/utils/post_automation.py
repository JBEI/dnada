#!/usr/bin/env python3

import io
import itertools
import os
import zipfile
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import openpyxl
import pandas as pd

from app.core.j5_to_echo import (create_echo_instructions,
                                 create_equimolar_assembly_instructions,
                                 create_plating_instructions,
                                 gather_construct_worksheet)
from app.core.j5_to_echo_utils import (convert2WellTo3Well, determineSuccessfulBands,
                                       stamp)

NGS_TEMPLATE_FILE: str = os.path.join(
    os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))),
    "ngs_form_empty_template_v2.xlsx",
)


def analyze_zag(peak_files: list, size_file: io.StringIO, settings: dict) -> str:
    expected_size_worksheet = pd.read_csv(size_file, index_col=0)
    plate_names = expected_size_worksheet[settings["zagColumnPlate"]].unique()
    assert len(plate_names) == len(
        peak_files
    ), "Did not provide the correct amount of zag peak files"
    peak_tables = {
        plate_name: peak_file for plate_name, peak_file in zip(plate_names, peak_files)
    }

    pcr_results = determineSuccessfulBands(
        pcrWorksheet=expected_size_worksheet,
        peakTables=peak_tables,
        plateColumns=(
            settings["zagColumnPlate"],
            settings["zagColumnWell"],
            settings["zagColumnSize"],
        ),
        tolerance=settings["tolerance"],
    )
    pcr_results["POLYMERASE"] = settings["polymerase"]
    return pcr_results.to_csv()


def analyze_manual_pcr_results(result_file: io.StringIO, settings: dict) -> str:
    plateColumns: Tuple[str, str, str] = (
        settings["zagColumnPlate"],
        settings["zagColumnWell"],
        settings["zagColumnSize"],
    )
    result_df = pd.read_csv(result_file)
    result_df["OUTPUT_LOCATION"] = result_df.apply(
        lambda row: "#".join(
            [
                row[plateColumns[0]],
                convert2WellTo3Well(row[plateColumns[1]]),
            ]
        ),
        axis=1,
    )
    result_df["POLYMERASE"] = settings["polymerase"]
    return result_df.to_csv()


def create_pcr_redo(pcr_results_file: io.StringIO, settings: dict) -> Dict[str, str]:
    redo_pcr_worksheet = create_pcr_redo_worksheet(pcr_results_file, settings)
    redo_pcr_echo_instructions = create_echo_instructions(
        redo_pcr_worksheet, "redo_pcr"
    )
    return {
        "worksheet": redo_pcr_worksheet.to_csv(),
        "echo_instructions": redo_pcr_echo_instructions.to_csv(),
    }


def create_pcr_redo_worksheet(
    pcr_results_file: io.StringIO, settings: dict
) -> pd.DataFrame:
    pcr_results = pd.read_csv(pcr_results_file, index_col=0)
    failed_pcrs = pcr_results.loc[~pcr_results[settings["pcrResultColumn"]], :]
    pcr_results_plates = pcr_results[settings["pcrOutputPlateColumn"]].unique()
    min_number_of_redo_plates = ((failed_pcrs.shape[0] - 1) // 96) + 1
    new_plate_prefix = f"redo_pcr_plate_T{settings['pcrRedoTrial']}"
    if pcr_results_plates.size == 1:
        # Redo Plate/Well = Output Plate/Well
        plate_prefix = "_".join(
            failed_pcrs.iloc[
                0,
                failed_pcrs.columns.get_loc(settings["pcrOutputPlateColumn"]),
            ].split("_")[:-1]
        )
        failed_pcrs.loc[:, settings["pcrRedoPlateColumn"]] = failed_pcrs.loc[
            :, settings["pcrOutputPlateColumn"]
        ].str.replace(plate_prefix, new_plate_prefix)
        failed_pcrs.loc[:, settings["pcrRedoWellColumn"]] = failed_pcrs[
            settings["pcrOutputWellColumn"]
        ]
    elif pcr_results_plates.size <= min_number_of_redo_plates:
        # Redo Plate/Well = Output Plate/Well
        plate_prefix = "_".join(
            failed_pcrs.iloc[
                0,
                failed_pcrs.columns.get_loc(settings["pcrOutputPlateColumn"]),
            ].split("_")[:-1]
        )
        failed_pcrs.loc[:, settings["pcrRedoPlateColumn"]] = failed_pcrs.loc[
            :, settings["pcrOutputPlateColumn"]
        ].str.replace(plate_prefix, new_plate_prefix)
        failed_pcrs.loc[:, settings["pcrRedoWellColumn"]] = failed_pcrs[
            settings["pcrOutputWellColumn"]
        ]
    elif pcr_results_plates.size > min_number_of_redo_plates:
        # Redo Plate/Well = consolidated
        failed_pcrs[settings["pcrRedoPlateColumn"]] = create_plate_column(
            number=failed_pcrs.shape[0],
            template=new_plate_prefix + "_{}",
            plate_size=96,
        )
        failed_pcrs[settings["pcrRedoWellColumn"]] = create_well_column(
            number=failed_pcrs.shape[0], how="col", plate_size=96
        )
    return failed_pcrs


def create_well_column(
    number: int, how: str = "col", plate_size: int = 96
) -> List[str]:
    assert plate_size == 96 or plate_size == 384
    assert how == "row" or how == "col"
    number_of_plates: int = ((number - 1) // plate_size) + 1
    if plate_size == 96:
        row_labels = "ABCDEFGH"
        col_labels = range(1, 13)
    elif plate_size == 384:
        row_labels = "ABCDEFGHIJKLMNOP"
        col_labels = range(1, 25)
    if how == "row":
        well_column = [
            f"{row}{column}"
            for row, column in itertools.product(row_labels, col_labels)
        ]
    elif how == "col":
        well_column = [
            f"{row}{column}"
            for column, row in itertools.product(col_labels, row_labels)
        ]
    well_column = (well_column * number_of_plates)[:number]
    return well_column


def create_plate_column(
    number: int, template: str = "plate_{}", plate_size: int = 96
) -> List[str]:
    assert plate_size == 96 or plate_size == 384
    assert "{}" in template
    plate_column: List[str] = [
        template.format(index // plate_size + 1) for index in range(number)
    ]
    return plate_column


def consolidate_pcr_trials_main(pcr_trial_files_dict: dict) -> io.BytesIO:
    results_df = consolidate_pcr_trials(pcr_trial_files=pcr_trial_files_dict)
    (
        template_df,
        plate_maps_df,
        biomek_instructions_df,
    ) = generate_consolidation_instructions(results_df)
    results_file = prepare_consolidate_pcr_trials_output(
        pcrTrials=pcr_trial_files_dict,
        consolidatedPCRTrials=results_df,
        humanConsolidateInstructions=template_df,
        humanToBiomekPlateConversion=plate_maps_df,
        biomekConsolidateInstructions=biomek_instructions_df,
    )
    return results_file


def prepare_consolidate_pcr_trials_output(
    pcrTrials: dict,
    consolidatedPCRTrials: pd.DataFrame,
    humanConsolidateInstructions: pd.DataFrame,
    humanToBiomekPlateConversion: pd.DataFrame,
    biomekConsolidateInstructions: pd.DataFrame,
) -> io.BytesIO:
    for pcrTrial in pcrTrials:
        pcrTrials[pcrTrial].seek(0)
    trialSheets = {
        trial: pd.read_csv(pcrTrials[trial], header=0, index_col=0)
        for trial in pcrTrials
    }
    excel_workbook = io.BytesIO()
    with pd.ExcelWriter(excel_workbook, mode="w") as consolidateExcelFile:
        for trial in trialSheets:
            trialSheets[trial].to_excel(
                consolidateExcelFile, sheet_name=trial, index=True
            )
        consolidatedPCRTrials.to_excel(
            consolidateExcelFile,
            sheet_name="consolidatedPCRWorksheet",
            index=False,
        )
        humanConsolidateInstructions.to_excel(
            consolidateExcelFile,
            sheet_name="humanConsolidateInstructions",
            index=False,
        )
        humanToBiomekPlateConversion.to_excel(
            consolidateExcelFile,
            sheet_name="humanToBiomekPlateConversion",
            index=False,
        )
        biomekConsolidateInstructions.to_excel(
            consolidateExcelFile,
            sheet_name="biomekConsolidateInstructions",
            index=False,
        )
    excel_workbook.seek(0)
    zip_results = io.BytesIO()
    with zipfile.ZipFile(zip_results, "w") as archive:
        archive.writestr("consolidate_pcr_workbook.xlsx", excel_workbook.read())
        archive.writestr(
            "biomek_instructions.csv",
            biomekConsolidateInstructions.to_csv(),
        )
        archive.writestr(
            "consolidated_pcr_worksheet.csv",
            consolidatedPCRTrials.to_csv(),
        )
    zip_results.seek(0)
    return zip_results


def consolidate_pcr_trials(pcr_trial_files: dict) -> pd.DataFrame:
    """Consolidate multiple PCR trials into a single sheet

    Arguments
    ---------
    pcr_trial_files : dict
        A dictionary containing paths to pcr result csv
        files. One file per trial.

    Returns
    -------
    consolidatedWorksheet : pd.DataFrame
        Consolidated PCR Worksheet
    """
    for pcrTrial in pcr_trial_files:
        pcr_trial_files[pcrTrial].seek(0)
    trialSheets = {
        trial: pd.read_csv(pcr_trial_files[trial], header=0, index_col=0)
        for trial in pcr_trial_files
    }
    for trial in trialSheets:
        trialSheets[trial] = trialSheets[trial].loc[
            :, ~trialSheets[trial].columns.str.match("Unnamed")
        ]
        trialSheets[trial]["REDO_PLATE"] = trialSheets[trial]["OUTPUT_LOCATION"].apply(
            lambda location: location.split("#")[0]
        )
        trialSheets[trial]["REDO_WELL"] = trialSheets[trial]["OUTPUT_LOCATION"].apply(
            lambda location: location.split("#")[1]
        )
        trialSheets[trial]["trial"] = trial
        trialSheets[trial]["src_plate"] = trialSheets[trial]["REDO_PLATE"]
        trialSheets[trial]["src_well"] = trialSheets[trial]["REDO_WELL"]
        trialSheets[trial]["src_location"] = trialSheets[trial].apply(
            lambda row: "{}#{}#{}".format(
                row["trial"], row["src_plate"], row["src_well"]
            ),
            axis=1,
        )
    consolidatedRxns = trialSheets["trial_1"].copy()
    for trial in trialSheets:
        for entry in trialSheets[trial].loc[trialSheets[trial]["GOOD"]].iterrows():
            # If there isn't a successful reaction in consolidated rxns
            # dataframe Then update the consolidated dataframe with the
            # rxn from the new trial
            if not consolidatedRxns.loc[
                (consolidatedRxns["OUTPUT_PLATE"] == entry[1]["OUTPUT_PLATE"])
                & (consolidatedRxns["OUTPUT_WELL"] == entry[1]["OUTPUT_WELL"]),
                "GOOD",
            ].values[0]:
                consolidatedRxns.loc[
                    (consolidatedRxns["OUTPUT_PLATE"] == entry[1]["OUTPUT_PLATE"])
                    & (consolidatedRxns["OUTPUT_WELL"] == entry[1]["OUTPUT_WELL"])
                ] = entry[1].values
    return consolidatedRxns


def generate_consolidation_instructions(
    consolidatedWorksheet: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Make biomek and human instructions for consolidated PCR rxns

    Arguments
    ---------
    consolidatedWorksheet : pd.DataFrame
        PCR Worksheet that contains consolidated PCR rxns
        from multiple trials. Needs to have the following columns:
        GOOD, trial, src_plate, src_well, OUTPUT_PLATE, and
        OUTPUT_WELL

    Returns
    -------
    humanInstructions : pd.DataFrame
        CSV containing information needed by human to
        consolidate PCR rxns

    plateMap : pd.DataFrame
        CSV containing information needed to convert
        human-readable plate names to Biomek plate names

    robotInstructions : pd.DataFrame
        CSV containing information needed by Biomek to
        consolidate PCR rxns
    """
    # Collecting information about consolidation for instructions
    consolidatedWorksheet = consolidatedWorksheet.loc[
        consolidatedWorksheet["GOOD"]
    ].copy()
    consolidatedWorksheet["trial_src_plate"] = (
        consolidatedWorksheet["trial"] + "#" + consolidatedWorksheet["src_plate"]
    )
    numberOfSrcPlates: int = int(consolidatedWorksheet["trial_src_plate"].unique().size)
    numberOfDestPlates: int = int(consolidatedWorksheet["OUTPUT_PLATE"].unique().size)
    numberOfSamples: int = int(sum(consolidatedWorksheet["GOOD"]))
    volumeToMove: int = 50  # uL

    # Preparing human readable csv instructions
    templateDF = pd.DataFrame(
        {
            "variable_name": [
                "src_plt_num",
                "dest_plt_num",
                "sample_num",
            ],
            "value": [
                numberOfSrcPlates,
                numberOfDestPlates,
                numberOfSamples,
            ],
        }
    )
    templateDF = pd.concat(
        [
            templateDF,
            consolidatedWorksheet.loc[
                :,
                [
                    "trial_src_plate",
                    "src_well",
                    "OUTPUT_PLATE",
                    "OUTPUT_WELL",
                ],
            ].reset_index(drop=True),
        ],
        axis=1,
    )
    templateDF["vol"] = volumeToMove
    templateDF = templateDF.rename(
        columns={
            "trial_src_plate": "src_plt",
            "src_well": "src_well",
            "OUTPUT_PLATE": "dest_plt",
            "OUTPUT_WELL": "dest_well",
        }
    ).reset_index(drop=True)

    # Preparing plate map csv
    srcPlates = np.sort(templateDF["src_plt"].unique())
    destPlates = np.sort(templateDF["dest_plt"].unique())
    srcMap = [(f"src_{i+1}", srcPlate) for i, srcPlate in enumerate(srcPlates)]
    destMap = [(f"dest_{i+1}", destPlate) for i, destPlate in enumerate(destPlates)]
    plateMaps = pd.DataFrame(srcMap + destMap, columns=["biomek_name", "plate_name"])

    # Making biomek readable csv instructions
    biomekInstructions = templateDF.copy()
    for i, plate in enumerate(plateMaps["plate_name"]):
        biomekInstructions = biomekInstructions.replace(
            plate, plateMaps["biomek_name"][i]
        )

    return templateDF, plateMaps, biomekInstructions


def create_equivolume_assembly(
    pcr_results_file: io.StringIO,
    assembly_worksheet_file: io.StringIO,
    parts_file: io.StringIO,
) -> io.BytesIO:
    pcr_results: pd.DataFrame = pd.read_csv(pcr_results_file, index_col=0)
    assembly_worksheet: pd.DataFrame = pd.read_csv(assembly_worksheet_file)
    parts: pd.DataFrame = pd.read_csv(parts_file)
    possible_constructs: pd.DataFrame
    possible_assembly_worksheet: pd.DataFrame
    assembly_worksheet_results: pd.DataFrame
    (
        possible_constructs,
        possible_assembly_worksheet,
        assembly_worksheet_results,
    ) = find_possible_constructs(
        pcr_results=pcr_results,
        assembly_worksheet=assembly_worksheet,
        parts=parts,
    )
    possible_constructs_worksheet: pd.DataFrame = gather_construct_worksheet(
        assembly_worksheet=possible_assembly_worksheet
    )
    methodPrefix = {
        "SLIC/Gibson/CPEC": "possible_gibson_plate_{}",
        "Golden-gate": "possible_golden-gate_plate_{}",
    }
    tmp_gibson_worksheet = possible_constructs_worksheet.loc[
        possible_constructs_worksheet["assembly_method"] == "SLIC/Gibson/CPEC",
        ["j5_construct_id", "src_plate", "src_well"],
    ]
    tmp_gibson_worksheet["src_plate"] = create_plate_column(
        number=tmp_gibson_worksheet.shape[0],
        template=methodPrefix["SLIC/Gibson/CPEC"],
        plate_size=96,
    )
    tmp_gibson_worksheet["src_well"] = create_well_column(
        number=tmp_gibson_worksheet.shape[0],
        how="col",
        plate_size=96,
    )
    tmp_golden_gate_worksheet = possible_constructs_worksheet.loc[
        possible_constructs_worksheet["assembly_method"] == "Golden-gate",
        ["j5_construct_id", "src_plate", "src_well"],
    ]
    tmp_golden_gate_worksheet["src_plate"] = create_plate_column(
        number=tmp_golden_gate_worksheet.shape[0],
        template=methodPrefix["Golden-gate"],
        plate_size=96,
    )
    tmp_golden_gate_worksheet["src_well"] = create_well_column(
        number=tmp_golden_gate_worksheet.shape[0],
        how="col",
        plate_size=96,
    )
    tmp_worksheet = pd.concat([tmp_gibson_worksheet, tmp_golden_gate_worksheet]).rename(
        columns={"src_plate": "tmp_plate", "src_well": "tmp_well"}
    )
    possible_constructs_worksheet = (
        possible_constructs_worksheet.merge(
            tmp_worksheet, how="left", on="j5_construct_id"
        )
        .drop(columns=["src_plate", "src_well"])
        .rename(columns={"tmp_plate": "src_plate", "tmp_well": "src_well"})
    )

    possible_constructs_worksheet["src_plate"] = create_plate_column(
        number=possible_constructs_worksheet.shape[0],
        template="consolidated_gibson_plate_{}",
        plate_size=96,
    )
    possible_constructs_worksheet["src_well"] = create_well_column(
        number=possible_constructs_worksheet.shape[0],
        how="col",
        plate_size=96,
    )
    possible_assembly_worksheet = (
        possible_assembly_worksheet.merge(
            possible_constructs_worksheet.loc[
                :, ["j5_construct_id", "src_plate", "src_well"]
            ],
            how="left",
            left_on="Number",
            right_on="j5_construct_id",
        )
        .drop(
            columns=[
                "Destination Plate",
                "Destination Well",
                "j5_construct_id",
            ]
        )
        .rename(
            columns={
                "src_plate": "Destination Plate",
                "src_well": "Destination Well",
            }
        )
    )
    possible_assembly_echo_instructions = create_echo_instructions(
        worksheet=possible_assembly_worksheet, method="assembly"
    )
    possible_plating_instructions_biomek = create_plating_instructions(
        plating=possible_constructs_worksheet,
        method="biomek",
        assemblyColumns=("src_plate", "src_well"),
    )

    zip_results = io.BytesIO()
    with zipfile.ZipFile(zip_results, "w") as archive:
        archive.writestr(
            "possible_assembly/assembly_worksheet_results.csv",
            assembly_worksheet_results.to_csv(),
        )
        archive.writestr(
            "possible_assembly/possible_constructs.csv",
            possible_constructs.to_csv(),
        )
        archive.writestr(
            "possible_assembly/possible_constructs_worksheet.csv",
            possible_constructs_worksheet.to_csv(),
        )
        archive.writestr(
            "possible_assembly/possible_assembly_worksheet.csv",
            possible_assembly_worksheet.to_csv(),
        )
        archive.writestr(
            "possible_assembly/possible_assembly_echo_instructions.csv",
            possible_assembly_echo_instructions.to_csv(),
        )
        archive.writestr(
            "possible_assembly/possible_plating_instructions_biomek.csv",
            possible_plating_instructions_biomek.to_csv(),
        )
    zip_results.seek(0)
    return zip_results


def find_possible_constructs(
    pcr_results: pd.DataFrame,
    assembly_worksheet: pd.DataFrame,
    parts: pd.DataFrame,
) -> pd.DataFrame:
    # Add pcr results to parts dataframe
    parts["GOOD"] = parts.apply(
        lambda row: True
        if row["PART_TYPE"] == "digest"
        else pcr_results.loc[
            (pcr_results["PARTS_SOURCE_PLATE"] == row["PART_PLATE"])
            & (pcr_results["PARTS_WELL"] == row["PART_WELL"]),
            "GOOD",
        ].values[0],
        axis=1,
    )
    # Add part results to assembly instructions
    assembly_worksheet_results = assembly_worksheet.merge(
        parts.loc[:, ["PART_PLATE", "PART_WELL", "GOOD"]].rename(
            columns={
                "PART_PLATE": "Source Plate",
                "PART_WELL": "Source Well",
            }
        ),
        how="left",
        on=["Source Plate", "Source Well"],
    )
    # Find possible constructs
    possible_constructs_mask = assembly_worksheet_results.groupby("Name").agg(
        {"GOOD": all}
    )
    # Create possible assembly instructions
    assembly_worksheet_possible = assembly_worksheet_results.loc[
        assembly_worksheet_results["Name"].apply(
            lambda name: possible_constructs_mask.loc[name, "GOOD"]
        ),
        :,
    ]
    return (
        possible_constructs_mask,
        assembly_worksheet_possible,
        assembly_worksheet_results,
    )


def prepare_standalone_equimolar_assembly_and_water(
    skinny_assembly: io.StringIO,
    quant_worksheet: io.StringIO,
    max_fmol: float = 100.0,
    max_vol: float = 5.0,
    max_part_percentage: float = 1.0,
) -> io.BytesIO:
    skinny_assembly_df: pd.DataFrame = pd.read_csv(skinny_assembly)
    quant_worksheet_df: pd.DataFrame = pd.read_csv(quant_worksheet)
    equimolar_df: pd.DataFrame = create_equimolar_assembly_instructions(
        assembly_df=skinny_assembly_df,
        quant_df=quant_worksheet_df,
        max_fmol=max_fmol,
        max_vol=max_vol,
        max_part_percentage=max_part_percentage,
    )
    equimolar_echo_instructions: pd.DataFrame = create_echo_instructions(
        worksheet=equimolar_df, method="equimolar"
    )

    zip_results = io.BytesIO()
    with zipfile.ZipFile(zip_results, "w") as archive:
        archive.writestr(
            ("equimolar_assembly_instructions/" "equimolar_assembly_worksheet.csv"),
            equimolar_df.to_csv(),
        )
        archive.writestr(
            (
                "equimolar_assembly_instructions/"
                "equimolar_assembly_echo_instructions.csv"
            ),
            equimolar_echo_instructions.to_csv(),
        )
    zip_results.seek(0)
    return zip_results


def analyze_qpix(qpix_file: io.StringIO, plating_file: io.StringIO) -> str:
    skip_qpix_header: bool = qpix_file.readline().startswith("Run")
    qpix_file.seek(0)
    qpix: pd.DataFrame = pd.read_csv(
        qpix_file,
        skiprows=11 if skip_qpix_header else 0,
        skipinitialspace=True,
    )
    plating: pd.DataFrame = pd.read_csv(plating_file, skipinitialspace=True)
    source_barcode_map: Dict[str, str] = {
        a: b
        for a, b in zip(
            np.sort(qpix["Source Barcode"].unique()),
            np.sort(plating["QPLATE"].unique()),
        )
    }
    dest_barcode_map: Dict[str, str] = {
        barcode: f"glycerol_stock_{i+1}"
        for i, barcode in enumerate(np.sort(qpix["Destination Barcode"].unique()))
    }
    qpix["QPLATE"] = qpix["Source Barcode"].apply(
        lambda barcode: source_barcode_map[barcode]
    )
    qpix["GLYCEROL_PLATE"] = qpix["Destination Barcode"].apply(
        lambda barcode: dest_barcode_map[barcode]
    )
    qpix = qpix.rename(
        columns={
            "Source Region": "QWELL",
            "Destination Well": "GLYCEROL_WELL",
        }
    )
    plating = plating.rename(
        columns={
            "src_plate": "TRANSFORMATION_PLATE",
            "src_well": "TRANSFORMATION_WELL",
        }
    )
    glycerol_worksheet: pd.DataFrame = qpix.merge(
        right=plating, how="left", on=["QPLATE", "QWELL"]
    ).loc[
        :,
        [
            "j5_construct_id",
            "name",
            "parts",
            "assembly_method",
            "TRANSFORMATION_PLATE",
            "TRANSFORMATION_WELL",
            "QPLATE",
            "QWELL",
            "GLYCEROL_PLATE",
            "GLYCEROL_WELL",
        ],
    ]
    return glycerol_worksheet.to_csv(index=False)


def read_construct_dataframe(construct_file: io.StringIO) -> pd.DataFrame:
    return pd.read_csv(construct_file)


def create_ngs_submission_form(
    glycerol_stock_file: io.StringIO,
    registry_file: io.StringIO,
    username: str,
) -> io.BytesIO:
    glycerol: pd.DataFrame = pd.read_csv(glycerol_stock_file)
    registry: pd.DataFrame = (
        pd.read_csv(registry_file)
        .rename(
            columns={
                "name": "Name",
                "Part_ID": "Part ID",
                "part id": "Part ID",
                "part_id": "Part ID",
            }
        )
        .loc[:, ["Name", "Part ID"]]
    )
    ngs_worksheet: pd.DataFrame = glycerol.merge(
        right=registry,
        how="left",
        left_on="name",
        right_on="Name",
    )
    ngs_worksheet["Sample_Name"] = (
        ngs_worksheet["GLYCEROL_PLATE"] + "-" + ngs_worksheet["GLYCEROL_WELL"]
    )
    ngs_worksheet["NGS_PLATE"] = ngs_worksheet["GLYCEROL_PLATE"].apply(
        lambda plate: "{username} {plate_number} {date}".format(
            username=username,
            plate_number=((int(plate.split("_")[-1]) - 1) // 4) + 1,
            date=datetime.today().strftime("%Y%m%d")[2:],
        )
    )
    ngs_worksheet["NGS_WELL"] = ngs_worksheet.apply(
        lambda row: stamp(
            row["GLYCEROL_WELL"],
            (int(row["GLYCEROL_PLATE"].split("_")[-1]) - 1) % 4,
        ),
        axis=1,
    )

    submission_excels: Dict[str, io.BytesIO] = {}
    submission_excel: io.BytesIO
    for plate in ngs_worksheet["NGS_PLATE"].unique():
        submission_excel = io.BytesIO()
        workbook = openpyxl.load_workbook(filename=NGS_TEMPLATE_FILE)
        worksheet = workbook.active
        worksheet["AI33"] = "Rows, Quads"
        for i, value in enumerate(
            ngs_worksheet.loc[ngs_worksheet["NGS_PLATE"] == plate, "Sample_Name"].values
        ):
            worksheet[f"AK{34 + i}"] = value
            worksheet[f"AM{34 + i}"] = "Plasmid__purified"
        for i, value in enumerate(
            ngs_worksheet.loc[ngs_worksheet["NGS_PLATE"] == plate, "Part ID"].values
        ):
            worksheet[f"AL{34 + i}"] = value
        workbook.save(submission_excel)
        submission_excel.seek(0)
        submission_excels[plate] = submission_excel

    zip_results = io.BytesIO()
    with zipfile.ZipFile(zip_results, "w") as archive:
        archive.writestr(
            "ngs_submission_instructions/ngs_worksheet.csv",
            ngs_worksheet.to_csv(),
        )
        for plate in submission_excels:
            archive.writestr(
                f"ngs_submission_instructions/{plate}.xlsx",
                submission_excels[plate].read(),
            )
    zip_results.seek(0)
    return zip_results


def analyze_sequencing_results(
    sample_file: io.StringIO, sequencing_results_file: io.StringIO
) -> io.BytesIO:
    samples: pd.DataFrame = pd.read_csv(sample_file)
    sequencing_results: pd.DataFrame = pd.read_csv(sequencing_results_file).rename(
        columns={"Sample_Name": "NGS_NAME", "Sample Name": "NGS_NAME"}
    )
    tmpSeries: pd.Series = samples["NGS_PLATE"].str.split(" ").str[:2]
    samples["NGS_NAME"] = (
        tmpSeries.str[0] + "-" + tmpSeries.str[1] + "-" + samples["Sample_Name"]
    )
    samples["NGS_ID"] = samples["NGS_NAME"].str.replace("_", "-").str.replace(" ", "-")
    sequencing_results["NGS_ID"] = (
        sequencing_results["NGS_NAME"].str.replace("_", "-").str.replace(" ", "-")
    )
    samples = samples.merge(right=sequencing_results, how="left", on="NGS_ID")
    first_successful_constructs: pd.DataFrame = (
        samples.loc[samples["IS_CLEAN"], :]
        .groupby(["j5_construct_id"])
        .aggregate("first")
        .loc[:, ["NGS_ID", "IS_CLEAN"]]
        .rename(columns={"IS_CLEAN": "CHERRY_PICK"})
    )
    first_successful_constructs["FINAL_PLATE"] = create_plate_column(
        number=first_successful_constructs.shape[0],
        template="final_plate_{}",
        plate_size=96,
    )
    first_successful_constructs["FINAL_WELL"] = create_well_column(
        number=first_successful_constructs.shape[0],
        how="col",
        plate_size=96,
    )
    samples = samples.merge(
        right=first_successful_constructs, how="left", on="NGS_ID"
    ).fillna(value=False)

    instructions: pd.DataFrame = samples.loc[
        samples["CHERRY_PICK"],
        [
            "NGS_PLATE",
            "NGS_WELL",
            "GLYCEROL_PLATE",
            "GLYCEROL_WELL",
            "FINAL_PLATE",
            "FINAL_WELL",
        ],
    ]
    instructions["row"] = instructions["FINAL_WELL"].str[0]
    instructions["col"] = instructions["FINAL_WELL"].str[1:]
    instructions = instructions.sort_values(by=["FINAL_PLATE", "col", "row"])
    instructions = instructions.drop(columns=["col", "row"]).reset_index(drop=True)
    instructions["VOLUME"] = 10

    biomek: pd.DataFrame = instructions.rename(
        columns={
            "GLYCEROL_PLATE": "src_plate",
            "GLYCEROL_WELL": "src_well",
            "FINAL_PLATE": "dest_plate",
            "FINAL_WELL": "dest_well",
            "VOLUME": "volume",
        }
    )
    biomek["src_plate"] = "src_plate_" + biomek["src_plate"].str.split("_").str[-1]
    biomek["dest_plate"] = "dest_plate_" + biomek["dest_plate"].str.split("_").str[-1]
    zip_results = io.BytesIO()
    with zipfile.ZipFile(zip_results, "w") as archive:
        archive.writestr(
            "cherry_picking_instructions/cherry_picking_worksheet.csv",
            samples.to_csv(index=False),
        )
        archive.writestr(
            (
                "cherry_picking_instructions/"
                "human_readable_cherry_picking_instructions.csv"
            ),
            instructions.to_csv(index=False),
        )
        archive.writestr(
            ("cherry_picking_instructions/" "biomek_cherry_picking_instructions.csv"),
            biomek.to_csv(index=False),
        )
    zip_results.seek(0)
    return zip_results
