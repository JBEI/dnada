import base64
import io
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.utils.db import (add_assembly_instructions_to_db,
                              add_consolidate_pcr_instructions_to_db,
                              add_pcr_redo_instructions_to_db,
                              add_plating_instructions_to_db,
                              process_design_to_db, process_workflow_to_db)
from app.api.utils.post_automation import (consolidate_pcr_trials_main,
                                           create_equivolume_assembly,
                                           create_pcr_redo,
                                           read_construct_dataframe)
from app.api.utils.time import timestamp
from app.core.j5_to_echo import create_plating_instructions, j5_to_echo

router = APIRouter()


@router.post("/workflows", response_model=schemas.Workflow)
def create_workflow(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    settings: schemas.AutomateSettingsCreate,
) -> Any:
    """
    Create workflow for experiment.
    """
    # experiment = crud.experiment.get(db=db, id=settings.experiment_id)
    # j5_key: str = ""
    # if not experiment:
    #     raise HTTPException(status_code=404, detail="Experiment not found")
    # if not crud.user.is_superuser(current_user) and (
    #     experiment.owner_id != current_user.id
    # ):
    #     raise HTTPException(
    #         status_code=400, detail="Not enough permissions"
    #     )
    # designs: List[models.Design] = [
    #     design for design in experiment.designs if not design.condensed
    # ]
    # (
    #     assembly_files,
    #     assembly_zip,
    # ) = create_condense_assembly_files_input(
    #     designs=designs  # type: ignore  # noqa
    # )
    # condensation_response = dispatch_condense_designs(
    #     file_list=assembly_files,
    #     file_zip=assembly_zip,
    #     j5_key=j5_key,
    #     j5_address=settings.j5_address,
    # )
    # if not condensation_response:
    #     raise HTTPException(
    #         status_code=400, detail="Design Files could not be condensed"
    #     )
    # master_j5 = extract_condensation_response(condensation_response)
    # genbanks: Dict[str, str] = gather_genbanks(designs)
    # results_dict, results_file = j5_to_echo(
    #     master_j5=master_j5,
    #     j5_key=j5_key,
    #     j5_address=settings.j5_address,
    #     genbanks=genbanks,
    # )

    # # Add design to database
    # extracted_master_j5: schemas.MasterJ5 = schemas.MasterJ5.parse_csv(
    #     master_j5
    # )

    # zip_json = {
    #     "combinatorial": extracted_master_j5.to_json(),
    #     "zip_file_name": "condensed_design",
    #     **genbanks,
    # }
    # if "combinatorial" not in zip_json:
    #     raise HTTPException(
    #         status_code=422,
    #         detail=(
    #             "Design File invalid. Require "
    #             "combinatorial csv to exist in zip"
    #         ),
    #     )

    # # Create Design
    # design_in = schemas.DesignCreate(
    #     name=f"{experiment.name}_condensed_design",
    #     description="condensed_design",
    #     zip_file_name=zip_json["zip_file_name"],
    #     condensed=True,
    # )
    # design = crud.design.create(
    #     db=db,
    #     obj_in=design_in,
    #     owner_id=current_user.id,
    #     experiment_id=experiment.id,
    # )

    # # Create RawDesign
    # rawdesign_in = schemas.RawDesignCreate(
    #     name=zip_json["zip_file_name"], data=zip_json
    # )
    # crud.rawdesign.create(
    #     db=db,
    #     obj_in=rawdesign_in,
    #     owner_id=current_user.id,
    #     design_id=design.id,
    # )

    # # Create ResultsZip
    # results_file.seek(0)
    # resultzip_in = schemas.ResultZipCreate(
    #     data=base64.b64encode(results_file.read()).decode("utf-8")
    # )
    # resultzip = crud.resultzip.create(
    #     db=db,
    #     obj_in=resultzip_in,
    #     owner_id=current_user.id,
    #     experiment_id=experiment.id,
    # )

    # # Process Design to db
    # process_design_to_db(
    #     db=db,
    #     zip_json=zip_json,
    #     owner_id=current_user.id,
    #     design_id=design.id,
    # )

    # # Create a workflow
    # workflow_in = schemas.WorkflowCreate(created_time=timestamp())
    # workflow = crud.workflow.create(
    #     db=db,
    #     obj_in=workflow_in,
    #     owner_id=current_user.id,
    #     experiment_id=experiment.id,
    #     design_id=design.id,
    #     resultzip_id=resultzip.id,
    # )

    # # Process workflow to db
    # process_workflow_to_db(
    #     db=db,
    #     workflow_objs=results_dict,
    #     owner_id=current_user.id,
    #     workflow_id=workflow.id,
    # )
    # return workflow
    return None


@router.get("/workflows", response_model=List[schemas.Workflow])
def read_workflows(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve workflows.
    """
    if crud.user.is_superuser(current_user):
        workflows = crud.workflow.get_multi(db, skip=skip, limit=limit)
    else:
        workflows = crud.workflow.get_multi(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return workflows


@router.get("/workflows/{id}", response_model=schemas.Workflow)
def read_workflow(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: int,
) -> Any:
    """
    Get workflow by ID.
    """
    workflow = crud.workflow.get(db=db, id=id)
    if not workflow:
        raise HTTPException(
            status_code=404, detail="Automation Result not found"
        )
    if not crud.user.is_superuser(current_user) and (
        workflow.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return workflow


@router.post("/workflows/find", response_model=List[schemas.Workflow])
def find_workflows(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.WorkflowUpdate,
    design_id: int,
) -> Any:
    """
    Find workflows.
    """
    workflows = crud.workflow.find(
        db=db, design_id=design_id, obj_in=search_obj
    )
    return workflows


@router.get(
    "/workflows/{id}/instructions",
    response_model=List[schemas.Instruction],
)
def read_workflow_instructions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: int,
) -> Any:
    """
    Get instructions belonging to workflow by ID.
    """
    workflow = crud.workflow.get(db=db, id=id)
    if not workflow:
        raise HTTPException(
            status_code=404, detail="Instruction not found"
        )
    if not crud.user.is_superuser(current_user) and (
        workflow.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return workflow.instructions


@router.put("/workflow/{id}", response_model=schemas.Workflow)
def update_workflow(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    workflow_in: schemas.WorkflowUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an workflow.
    """
    workflow = crud.workflow.get(db=db, id=id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not crud.user.is_superuser(current_user) and (
        workflow.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    workflow = crud.workflow.update(
        db=db, db_obj=workflow, obj_in=workflow_in
    )
    return workflow


@router.delete("/workflows/{id}", response_model=schemas.Workflow)
def delete_workflow(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an workflow.
    """
    workflow = crud.workflow.get(db=db, id=id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not crud.user.is_superuser(current_user) and (
        workflow.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    workflow = crud.workflow.remove(db=db, id=id)
    return workflow


@router.get("/resultzips/{id}")
def download_workflow_zip(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: int,
) -> StreamingResponse:
    """
    Get result zip by ID.
    """
    result_zip = crud.resultzip.get(db=db, id=id)
    if not result_zip:
        raise HTTPException(status_code=404, detail="Result Zip not found")
    if not crud.user.is_superuser(current_user) and (
        result_zip.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return StreamingResponse(
        io.BytesIO(base64.b64decode(result_zip.data.encode("utf-8"))),
        media_type="application/zip",
    )


class RedoPCRInstructions(BaseModel):
    worksheet: str
    echo_instructions: str


@router.post("/redopcr/{id}", response_model=RedoPCRInstructions)
def create_redopcr_workflow(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: int,  # id = run_id
) -> Any:
    """
    Create redo pcr workflow for experiment.

    pcrrun_id contains pcr results for a previous trial
    """
    pcrrun: Optional[models.Run] = crud.run.get(db=db, id=id)
    if not pcrrun:
        raise HTTPException(status_code=404, detail="PCR Run not found")
    if not crud.user.is_superuser(current_user) and (
        pcrrun.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    workflow_id: int = pcrrun.instruction.workflow_id
    redo_trial: int = pcrrun.instruction.trial + 1
    redo_worksheet: Optional[models.Instruction] = (
        db.query(models.Instruction)
        .join(models.Workflow)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.Instruction.category == "pcr_worksheet")
        .filter(models.Instruction.trial == redo_trial)
        .one_or_none()
    )
    pcr_redo_instructions: Dict[str, Optional[str]] = {}
    if redo_worksheet:
        redo_echo: models.Instruction = (
            db.query(models.Instruction)
            .join(models.Workflow)
            .filter(models.Workflow.id == workflow_id)
            .filter(
                models.Instruction.category == "pcr_echo_instructions.csv"
            )
            .filter(models.Instruction.trial == redo_trial)
            .one()
        )
        pcr_redo_instructions = {
            "worksheet": redo_worksheet.data,
            "echo_instructions": redo_echo.data,
        }
    else:
        settings: Dict[str, Any] = {
            "pcrResultColumn": "GOOD",
            "pcrOutputPlateColumn": "OUTPUT_PLATE",
            "pcrOutputWellColumn": "OUTPUT_WELL",
            "pcrRedoPlateColumn": "REDO_PLATE",
            "pcrRedoWellColumn": "REDO_WELL",
            "pcrRedoTrial": redo_trial,
        }
        pcr_results_file: io.StringIO = io.StringIO(pcrrun.raw_data)
        pcr_redo_instructions = create_pcr_redo(
            pcr_results_file=pcr_results_file, settings=settings
        )
        add_pcr_redo_instructions_to_db(
            db=db,
            owner_id=current_user.id,
            workflow_id=workflow_id,
            pcr_redo_instructions=pcr_redo_instructions,
            trial=redo_trial,
            settings=settings,
        )
    return pcr_redo_instructions


@router.post("/workflow/{id}/consolidatepcrs")
def create_consolidatepcr_workflow(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: int,  # id = workflow_id
    plating_scheme: str,  # plating scheme == biomek
) -> Any:
    """
    Create consolidate pcr workflow for experiment.
    """
    workflow = crud.workflow.get(db=db, id=id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not crud.user.is_superuser(current_user) and (
        workflow.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    pcr_trial_files = (
        db.query(models.Run.raw_data, models.Instruction.trial)
        .join(models.Instruction)
        .join(models.Workflow)
        .filter(models.Workflow.id == id)
        .filter(models.Instruction.category == "pcr_worksheet")
        .filter(models.Run.run_type == "pcr")
        .all()
    )
    if not pcr_trial_files:
        raise HTTPException(status_code=422, detail="No pcr results found")
    pcr_trial_files_dict = {
        f"trial_{i}": io.StringIO(pcr_trial_file)
        for pcr_trial_file, i in pcr_trial_files
    }
    consolidate_pcr_instructions_zip = consolidate_pcr_trials_main(
        pcr_trial_files_dict
    )
    consolidate_pcr_instruction: models.Instruction = (
        add_consolidate_pcr_instructions_to_db(
            db=db,
            owner_id=current_user.id,
            workflow_id=id,
            instruct_zip=consolidate_pcr_instructions_zip,
        )
    )
    pcr_results_worksheet: str = crud.instruction.find(
        db=db,
        workflow_id=id,
        obj_in={"category": "consolidated_pcr_worksheet.csv", "trial": 1},
    )[0].data
    parts_plate: str = crud.instruction.find(
        db=db,
        workflow_id=id,
        obj_in={"category": "part_worksheet", "trial": 1},
    )[0].data
    assembly_worksheet: str = crud.instruction.find(
        db=db,
        workflow_id=id,
        obj_in={"category": "clean_assembly_worksheet", "trial": 1},
    )[0].data
    assembly_instructions: io.BytesIO = create_equivolume_assembly(
        pcr_results_file=io.StringIO(pcr_results_worksheet),
        assembly_worksheet_file=io.StringIO(assembly_worksheet),
        parts_file=io.StringIO(parts_plate),
    )
    add_assembly_instructions_to_db(
        db=db,
        owner_id=current_user.id,
        workflow_id=id,
        assembly_zip=assembly_instructions,
    )
    construct_worksheet: str
    try:
        construct_worksheet = crud.instruction.find(
            db=db,
            workflow_id=id,
            obj_in={
                "category": "possible_constructs_worksheet.csv",
                "trial": 1,
            },
        )[0].data
    except IndexError:
        construct_worksheet = crud.instruction.find(
            db=db,
            workflow_id=id,
            obj_in={"category": "construct_worksheet.csv", "trial": 1},
        )[0].data
    plating_instructions = create_plating_instructions(
        plating=read_construct_dataframe(
            construct_file=io.StringIO(construct_worksheet)
        ),
        method=plating_scheme,
        assemblyColumns=("src_plate", "src_well"),
    ).to_csv(index=False)
    add_plating_instructions_to_db(
        db=db,
        owner_id=current_user.id,
        workflow_id=id,
        plating_instructions=plating_instructions,
    )
    result_zip: io.BytesIO = combine_pcr_and_assembly_zips(
        pcr_zip=consolidate_pcr_instructions_zip,
        assembly_zip=assembly_instructions,
        plating_instructions=plating_instructions,
    )
    if not result_zip:
        raise HTTPException(status_code=422, detail="No result_zip found")
    return StreamingResponse(
        result_zip,
        media_type="application/zip",
    )


def combine_pcr_and_assembly_zips(
    pcr_zip: io.BytesIO,
    assembly_zip: io.BytesIO,
    plating_instructions: str,
) -> io.BytesIO:
    pcr_zip.seek(0)
    assembly_zip.seek(0)
    zip_results: io.BytesIO = io.BytesIO()
    import zipfile

    with zipfile.ZipFile(pcr_zip, mode="r") as F:
        biomek_instructions: str = F.read(
            "biomek_instructions.csv"
        ).decode("utf-8")
        consolidated_pcr_worksheet: str = F.read(
            "consolidated_pcr_worksheet.csv"
        ).decode("utf-8")
        consolidate_pcr_workbook: str = base64.b64encode(
            F.read("consolidate_pcr_workbook.xlsx")
        ).decode("utf-8")
    with zipfile.ZipFile(assembly_zip, mode="r") as F:
        possible_constructs: str = F.read(
            "possible_assembly/possible_constructs.csv"
        ).decode("utf-8")
        possible_constructs_worksheet: str = F.read(
            "possible_assembly/possible_constructs_worksheet.csv"
        ).decode("utf-8")
        possible_assembly_worksheet: str = F.read(
            "possible_assembly/possible_assembly_worksheet.csv"
        ).decode("utf-8")
        possible_assembly_echo_instructions: str = F.read(
            "possible_assembly/possible_assembly_echo_instructions.csv"
        ).decode("utf-8")
        possible_plating_instructions_biomek: str = F.read(
            "possible_assembly/possible_plating_instructions_biomek.csv"
        ).decode("utf-8")
    with zipfile.ZipFile(zip_results, "w") as archive:
        archive.writestr(
            "possible_assembly/possible_constructs.csv",
            possible_constructs,
        )
        archive.writestr(
            "possible_assembly/possible_constructs_worksheet.csv",
            possible_constructs_worksheet,
        )
        archive.writestr(
            "possible_assembly/possible_assembly_worksheet.csv",
            possible_assembly_worksheet,
        )
        archive.writestr(
            "possible_assembly/possible_assembly_echo_instructions.csv",
            possible_assembly_echo_instructions,
        )
        archive.writestr(
            "possible_assembly/possible_plating_instructions_biomek.csv",
            possible_plating_instructions_biomek,
        )
        archive.writestr(
            "consolidate_pcrs/consolidate_pcr_workbook.xlsx",
            consolidate_pcr_workbook,
        )
        archive.writestr(
            "consolidate_pcrs/biomek_instructions.csv",
            biomek_instructions,
        )
        archive.writestr(
            "consolidate_pcrs/consolidated_pcr_worksheet.csv",
            consolidated_pcr_worksheet,
        )
        archive.writestr(
            "plating/plating_instructions.csv", plating_instructions
        )
    zip_results.seek(0)
    return zip_results


@router.get("/workflow/{id}/possibleassembly")
def get_possible_assembly(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: int,  # id = workflow_id
) -> StreamingResponse:
    workflow = crud.workflow.get(db=db, id=id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not crud.user.is_superuser(current_user) and (
        workflow.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    assembly_instructions: List[
        models.Instruction
    ] = crud.instruction.find(
        db=db,
        workflow_id=id,
        obj_in={"category": "assembly_instructions.zip", "trial": 1},
    )
    result_zip: str = ""
    if not assembly_instructions:
        raise HTTPException(
            status_code=422, detail="Possible assembly not found"
        )
    else:
        result_zip = assembly_instructions[0].data
    return StreamingResponse(
        io.BytesIO(base64.b64decode(result_zip.encode("utf-8"))),
        media_type="application/zip",
    )
