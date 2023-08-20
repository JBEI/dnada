import datetime
import io
import json
from typing import Any, Dict, List, Union

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from app import models, schemas
from app.api import deps
from app.api.utils.post_automation import (
    analyze_qpix,
    analyze_sequencing_results,
    analyze_zag,
    consolidate_pcr_trials_main,
    create_equivolume_assembly,
    create_ngs_submission_form,
    create_pcr_redo,
    prepare_standalone_equimolar_assembly_and_water,
    read_construct_dataframe,
)
from app.api.utils.results_toolbox import condense_plate_reader_data
from app.core.colony_pcr import create_colony_pcr_instructions
from app.core.condense_designs import condense_designs
from app.core.j5_to_echo import create_plating_instructions, j5_to_echo
from app.core.process_design import process_j5_zip_upload
from app.core import j5

router = APIRouter()


async def async_read_csv_file(upload_file: UploadFile) -> str:
    """Read fastAPI UploadFile into StringIO

    Required because pandas unable to read UploadFile
    """
    file_read: Union[str, bytes] = await upload_file.read()
    try:
        return file_read.decode("utf-8") if isinstance(file_read, bytes) else file_read
    except UnicodeDecodeError:  # required in case of windows formatting
        return file_read.decode("utf-16") if isinstance(file_read, bytes) else file_read


@router.post("/parsej5")
def parse_j5_zip(*, upload_file: UploadFile = File(...)) -> str:
    """
    Parse J5 Results File to JSON
    """
    try:
        j5_design: j5.J5Design = process_j5_zip_upload(upload_file)
    finally:
        upload_file.file.close()
    return j5_design.to_json()


@router.post("/condensej5")
def condense_j5_designs(
    *,
    upload_files: List[UploadFile] = File(...),
) -> str:
    """
    Condense j5 design zip files into single design
    """
    try:
        designs: List[j5.J5Design] = [
            process_j5_zip_upload(upload_file) for upload_file in upload_files
        ]
        condensed_j5_design: j5.J5Design = condense_designs(designs)
    finally:
        for upload_file in upload_files:
            upload_file.file.close()
    return condensed_j5_design.to_json()


@router.post("/automatej5")
async def automate_j5(
    *,
    upload_file: UploadFile = File(...),
) -> StreamingResponse:
    """
    Create customized automation instructions for J5 Design JSON
    """
    results_file = io.BytesIO()
    try:
        design_json: str = await async_read_csv_file(upload_file=upload_file)
        j5_design: j5.J5Design = j5.J5Design.parse_raw(design_json)
        _, results_file = j5_to_echo(
            j5_design=j5_design,
        )
    finally:
        upload_file.file.close()
    return StreamingResponse(results_file, media_type="application/zip")


@router.post("/condenseandautomatej5")
async def condense_and_automate_j5(
    *,
    upload_files: List[UploadFile] = File(...),
) -> StreamingResponse:
    """
    Condense j5 design zip files into single design then
    create customized automation instructions for J5 Design
    """
    results_file = io.BytesIO()
    try:
        designs: List[j5.J5Design] = [
            process_j5_zip_upload(upload_file) for upload_file in upload_files
        ]
        condensed_j5_design: j5.J5Design = condense_designs(designs)
        _, results_file = j5_to_echo(
            j5_design=condensed_j5_design,
        )
    finally:
        for upload_file in upload_files:
            upload_file.file.close()
    return StreamingResponse(results_file, media_type="application/zip")


@router.post("/analyzezag")
async def standalone_analyze_zag(
    *,
    peak_files: List[UploadFile] = File(...),
    size_file: UploadFile = File(...),
    settings: str = Form(...),
) -> str:
    """
    Analyze ZAG peak table using expected size table
    """
    results_file: str = ""
    try:
        dict_settings: Dict[str, Any] = json.loads(settings)
        dict_settings["tolerance"] = float(dict_settings["tolerance"])
        size_file_read: str = await async_read_csv_file(upload_file=size_file)
        results_file = analyze_zag(
            peak_files=[peak_file.file for peak_file in peak_files],
            size_file=io.StringIO(size_file_read),
            settings=dict_settings,
        )
    finally:
        for peak_file in peak_files:
            peak_file.file.close()
        size_file.file.close()
    return results_file


@router.post("/createpcrredo")
async def standalone_create_pcr_redo(
    *,
    pcr_results_file: UploadFile = File(...),
    settings: str = Form(...),
) -> dict:
    """
    Create PCR Redo instructions using failed PCRs
    """
    pcr_redo_instructions: dict = {}
    try:
        dict_settings: Dict[str, Any] = json.loads(settings)
        dict_settings["pcrRedoPlateColumn"] = "REDO_PLATE"
        dict_settings["pcrRedoWellColumn"] = "REDO_WELL"
        pcr_results_read: str = await async_read_csv_file(upload_file=pcr_results_file)
        pcr_redo_instructions = create_pcr_redo(
            pcr_results_file=io.StringIO(pcr_results_read),
            settings=dict_settings,
        )
    finally:
        pcr_results_file.file.close()
    return pcr_redo_instructions


@router.post("/consolidatepcrtrials")
async def standalone_consolidate_pcr_trials(
    *,
    pcr_trial_files: List[UploadFile] = File(...),
) -> StreamingResponse:
    """
    Consolidate PCR Trials into single worksheet
    """
    results_file = io.BytesIO()
    try:
        pcr_trial_files_dict = {
            f"trial_{i+1}": pcr_trial_file.file
            for i, pcr_trial_file in enumerate(pcr_trial_files)
        }
        results_file = consolidate_pcr_trials_main(pcr_trial_files_dict)
    finally:
        for pcr_trial in pcr_trial_files:
            pcr_trial.file.close()
    return StreamingResponse(results_file, media_type="application/zip")


@router.post("/createequivolumeassembly")
async def standalone_create_equivolume_assembly(
    *,
    pcr_results_file: UploadFile = File(...),
    assembly_file: UploadFile = File(...),
    parts_file: UploadFile = File(...),
) -> StreamingResponse:
    """
    Create equivolume assembly instructions from successful PCRs
    """
    results_file: io.BytesIO = io.BytesIO()
    try:
        pcr_results_content: str = await async_read_csv_file(
            upload_file=pcr_results_file
        )
        assembly_content: str = await async_read_csv_file(upload_file=assembly_file)
        parts_content: str = await async_read_csv_file(upload_file=parts_file)
        results_file = create_equivolume_assembly(
            pcr_results_file=io.StringIO(pcr_results_content),
            assembly_worksheet_file=io.StringIO(assembly_content),
            parts_file=io.StringIO(parts_content),
        )
    finally:
        pcr_results_file.file.close()
        assembly_file.file.close()
        parts_file.file.close()
    return StreamingResponse(results_file, media_type="application/zip")


@router.post("/standalone_equimolar_assembly_and_water_transfer")
async def standalone_equimolar_assembly_and_water_transfer(
    *,
    assembly_worksheet: UploadFile = File(...),
    quant_worksheet: UploadFile = File(...),
    max_fmol: float = Form(...),
    max_vol: float = Form(...),
    max_part_percentage: float = Form(...),
) -> StreamingResponse:
    """
    Take in worksheets and create equimolar assembly instructions.
    Equimolar assembly instructions automatically calculates water
    transfer instructions
    """
    results_file: io.BytesIO = io.BytesIO()
    try:
        assembly_read: str = await async_read_csv_file(upload_file=assembly_worksheet)
        quant_read: str = await async_read_csv_file(upload_file=quant_worksheet)
        results_file = prepare_standalone_equimolar_assembly_and_water(
            skinny_assembly=io.StringIO(assembly_read),
            quant_worksheet=io.StringIO(quant_read),
            max_fmol=max_fmol,
            max_vol=max_vol,
            max_part_percentage=max_part_percentage,
        )
    finally:
        assembly_worksheet.file.close()
        quant_worksheet.file.close()
    return StreamingResponse(results_file, media_type="application/zip")


@router.post("/plating")
async def standalone_create_plating_instructions(
    *,
    construct_file: UploadFile = File(...),
    plating_scheme: str = Form(...),
) -> str:
    """
    Use plating scheme to create Q-Plate layout
    """
    results_file: str = ""
    try:
        construct_read: str = await async_read_csv_file(upload_file=construct_file)
        results_file = create_plating_instructions(
            plating=read_construct_dataframe(
                construct_file=io.StringIO(construct_read)
            ),
            method=plating_scheme,
            assemblyColumns=("src_plate", "src_well"),
        ).to_csv(index=False)
    finally:
        construct_file.file.close()
    return results_file


@router.post("/glycerolstock")
async def standalone_create_glycerol_stock_worksheet(
    *,
    qpix_file: UploadFile = File(...),
    plating_file: UploadFile = File(...),
) -> str:
    """
    Analyze QPix results and make glycerol stock worksheet
    """
    results_file: str = ""
    try:
        qpix_read: str = await async_read_csv_file(upload_file=qpix_file)
        plating_read: str = await async_read_csv_file(upload_file=plating_file)
        results_file = analyze_qpix(
            qpix_file=io.StringIO(qpix_read),
            plating_file=io.StringIO(plating_read),
        )
    finally:
        qpix_file.file.close()
        plating_file.file.close()
    return results_file


@router.post("/createcolonypcrinstructions")
async def standalone_create_colony_pcr_instructions(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
    glycerol_file: UploadFile = File(...),
    plasmid_sequences_file: UploadFile = File(...),
    forward_primer: str = Form(...),
    reverse_primer: str = Form(...),
    reaction_volume: int = Form(...),
) -> StreamingResponse:
    """
    Create colony PCR instructions using 1 set of forward and reverse
    primers
    """
    results_file: io.BytesIO
    try:
        glycerol_worksheet_read: str = await async_read_csv_file(
            upload_file=glycerol_file
        )
        plasmids_sequences_read: str = await async_read_csv_file(
            upload_file=plasmid_sequences_file
        )
        username: str = (
            current_user.email.split("@")[0]
            if current_user.email
            else str(current_user.id)
        )
        results_file = create_colony_pcr_instructions(
            glycerol_file=io.StringIO(glycerol_worksheet_read),
            plasmid_sequences_file=io.StringIO(plasmids_sequences_read),
            forward_primer=forward_primer,
            reverse_primer=reverse_primer,
            username=username,
            reaction_volume=reaction_volume,
        )
    finally:
        glycerol_file.file.close()
        plasmid_sequences_file.file.close()
    return StreamingResponse(results_file, media_type="application/zip")


@router.post("/ngsform")
async def standalone_create_ngs_submission_form(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
    glycerol_stock_file: UploadFile = File(...),
    registry_file: UploadFile = File(...),
) -> StreamingResponse:
    """
    Create ngs submission form
    """
    results_file: io.BytesIO = io.BytesIO()
    try:
        glycerol_stock_read: str = await async_read_csv_file(
            upload_file=glycerol_stock_file
        )
        registry_read: str = await async_read_csv_file(upload_file=registry_file)
        username: str = (
            current_user.email.split("@")[0] if current_user.email else "username"
        )
        results_file = create_ngs_submission_form(
            glycerol_stock_file=io.StringIO(glycerol_stock_read),
            registry_file=io.StringIO(registry_read),
            username=username,
        )
    finally:
        glycerol_stock_file.file.close()
        registry_file.file.close()
    return StreamingResponse(results_file, media_type="application/zip")


@router.post("/cherrypicking")
async def standalone_create_cherry_picking_instructions(
    *,
    sample_file: UploadFile = File(...),
    sequencing_results_file: UploadFile = File(...),
) -> StreamingResponse:
    """
    Analyze Sequencing results and make cherry picking instructions
    """
    results_file: io.BytesIO = io.BytesIO()
    try:
        sample_read: str = await async_read_csv_file(upload_file=sample_file)
        sequencing_results_read: str = await async_read_csv_file(
            upload_file=sequencing_results_file
        )
        results_file = analyze_sequencing_results(
            sample_file=io.StringIO(sample_read),
            sequencing_results_file=io.StringIO(sequencing_results_read),
        )
    finally:
        sample_file.file.close()
        sequencing_results_file.file.close()
    return StreamingResponse(results_file, media_type="application/zip")


@router.post("/condenseplatereaderdata")
async def standalone_condense_plate_reader_data(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
    plate_reader_file: UploadFile = File(...),
    plate_map_file: UploadFile = File(...),
    start_date: datetime.date = Form(...),
) -> str:
    """
    Convert plate reader wide format to tall format
    """
    results_file: str = ""
    try:
        plate_reader_read: str = await async_read_csv_file(
            upload_file=plate_reader_file
        )
        plate_map_read: str = await async_read_csv_file(upload_file=plate_map_file)
        results_file = condense_plate_reader_data(
            plate_reader_file=io.StringIO(plate_reader_read),
            plate_map_file=io.StringIO(plate_map_read),
            start_date=start_date,
        )
    finally:
        plate_reader_file.file.close()
        plate_map_file.file.close()
    return results_file
