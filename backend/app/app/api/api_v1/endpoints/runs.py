from typing import Any, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import Json
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.utils.assemblyrun_helper import add_assembly_results_to_db
from app.api.utils.pcrrun_helper import add_pcr_results_to_db, gather_size_file
from app.api.utils.post_automation import analyze_manual_pcr_results, analyze_zag
from app.api.utils.sequencingrun_helper import add_sequencing_results_to_db

router = APIRouter()


@router.post("/runs/pcr", response_model=schemas.Run)
def create_pcr_run(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    peak_files: List[UploadFile] = File(...),
    settings: Json = Form(...),
) -> Any:
    """
    Create new PCR results

    settings = {
        isRawZagData: True,
        tolerance: '0.50',
        zagColumnPlate: 'OUTPUT_PLATE',
        zagColumnWell: 'OUTPUT_WELL',
        polymerase: 'Q5',
        instructionID: 0
    }
    """
    try:
        peak_files_noasync: list = [peak_file.file for peak_file in peak_files]
        settings["zagColumnSize"] = "EXPECTED_SIZE"
        if settings["isRawZagData"]:
            settings["tolerance"] = float(settings["tolerance"])
            size_file = gather_size_file(
                db=db, instruction_id=settings["instructionID"]
            )
            results_file = analyze_zag(
                peak_files=peak_files_noasync,
                size_file=size_file,
                settings=settings,
            )
        else:
            assert len(peak_files) == 1
            # results_file = peak_files_noasync[0].read().decode("utf-8")
            results_file = analyze_manual_pcr_results(
                result_file=peak_files_noasync[0], settings=settings
            )
        pcrrun = add_pcr_results_to_db(
            db=db,
            results_file=results_file,
            current_user=current_user,
            settings=settings,
        )
    finally:
        for peak_file in peak_files:
            peak_file.file.close()
    return pcrrun


@router.post("/runs/assembly", response_model=schemas.Run)
async def create_assembly_run(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    assembly_files: List[UploadFile] = File(...),
    settings: schemas.AssemblyRunSettings = Depends(
        schemas.AssemblyRunSettings.as_form
    ),
) -> Any:
    """
    Create new Assembly results

    assembly_file should at least have 2 columns: j5_construct_id (int) and
    colonies (bool)

    settings = {
        manual: True,
        workflowID: 0
    }
    """
    try:
        assert len(assembly_files) == 1
        assembly_file = assembly_files[0]
        assembly_results = await assembly_file.read()
        if isinstance(assembly_results, bytes):
            assembly_results = assembly_results.decode("utf-8")
        assembly_run = add_assembly_results_to_db(
            db=db,
            results_file=assembly_results,
            current_user=current_user,
            settings=settings,
        )
    finally:
        assembly_file.file.close()
    return assembly_run


@router.post("/runs/sequencing", response_model=schemas.Run)
async def create_sequencing_run(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    sequencing_file: UploadFile = File(...),
    settings: schemas.SequencingRunSettings = Depends(
        schemas.SequencingRunSettings.as_form
    ),
) -> Any:
    """
    Create new Sequencing results

    sequencing_file should at least have 2 columns: j5_construct_id (int)
    and sequencing (bool)

    settings = {
        manual: False,
        workflowID: 0
    }
    """
    try:
        sequencing_results = await sequencing_file.read()
        if isinstance(sequencing_results, bytes):
            sequencing_results = sequencing_results.decode("utf-8")
        sequencing_run = add_sequencing_results_to_db(
            db=db,
            results_file=sequencing_results,
            current_user=current_user,
            settings=settings,
        )
    finally:
        sequencing_file.file.close()
    return sequencing_run


@router.get("/runs", response_model=List[schemas.Run])
def read_runs(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve runs.
    """
    if crud.user.is_superuser(current_user):
        runs = crud.run.get_multi(db, skip=skip, limit=limit)
    else:
        runs = crud.run.get_multi(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return runs


@router.post("/runs/find", response_model=List[schemas.Run])
def find_runs(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.RunUpdate,
    instruction_id: int,
) -> Any:
    """
    Find runs.
    """
    runs = crud.run.find(db=db, instruction_id=instruction_id, obj_in=search_obj)
    return runs


@router.get("/runs/{id}", response_model=schemas.Run)
def read_run(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: int,
) -> Any:
    """
    Get run by ID.
    """
    run = crud.run.get(db=db, id=id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if not crud.user.is_superuser(current_user) and (run.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return run


@router.put("/runs/{id}", response_model=schemas.Run)
def update_run(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    run_in: schemas.RunUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a run.
    """
    run = crud.run.get(db=db, id=id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if not crud.user.is_superuser(current_user) and (run.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    run = crud.run.update(db=db, db_obj=run, obj_in=run_in)
    return run


@router.delete("/runs/{id}", response_model=schemas.Run)
def delete_run(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: int,
) -> Any:
    """
    Delete a run.
    """
    run = crud.run.get(db=db, id=id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if not crud.user.is_superuser(current_user) and (run.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    run = crud.run.remove(db=db, id=id)
    return run
