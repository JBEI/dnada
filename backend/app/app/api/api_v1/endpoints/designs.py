import logging
from typing import Any, List

from fastapi import (APIRouter, Depends, File, Form, HTTPException,
                     UploadFile)
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.utils.db import process_design_to_db
from app.core.process_design import process_j5_zip_upload

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


@router.get("/designs", response_model=List[schemas.Design])
def read_designs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve designs.
    """
    if crud.user.is_superuser(current_user):
        designs = crud.design.get_multi(db, skip=skip, limit=limit)
    else:
        designs = crud.design.get_multi(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return designs


@router.post("/designs/find", response_model=List[schemas.Design])
def find_designs(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.DesignUpdate,
    experiment_id: int,
) -> Any:
    """
    Find designs.
    """
    designs = crud.design.find(
        db=db, experiment_id=experiment_id, obj_in=search_obj
    )
    return designs


@router.put("/designs/{id}", response_model=schemas.Design)
def update_design(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    design_in: schemas.DesignUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an design.
    """
    design = crud.design.get(db=db, id=id)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    if not crud.user.is_superuser(current_user) and (
        design.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    design = crud.design.update(db=db, db_obj=design, obj_in=design_in)
    return design


@router.get("/designs/{id}", response_model=schemas.Design)
def read_design(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get design by ID.
    """
    design = crud.design.get(db=db, id=id)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    if not crud.user.is_superuser(current_user) and (
        design.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return design


@router.delete("/designs/{id}", response_model=schemas.Design)
def delete_design(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an design.
    """
    design = crud.design.get(db=db, id=id)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    if not crud.user.is_superuser(current_user) and (
        design.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    design = crud.design.remove(db=db, id=id)
    return design


@router.post("/designs", response_model=schemas.Design)
def create_design(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    design_file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(...),
    zip_file_name: str = Form(...),
    experiment_id: int = Form(...),
) -> Any:
    """
    Create new design.
    """
    zip_json = {}
    try:
        parent_experiment = crud.experiment.get(db=db, id=experiment_id)
        if not parent_experiment:
            raise HTTPException(
                status_code=422,
                detail=("Experiment not found"),
            )
        if not crud.user.is_superuser(current_user) and (
            parent_experiment.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=400, detail="Not enough permissions"
            )
        logger.debug(f"Beginning to process design: {name}")
        zip_json = process_j5_zip_upload(design_file)
        if "combinatorial" not in zip_json:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Design File invalid. Require combinatorial"
                    " csv to exist in zip"
                ),
            )

        logger.debug("Creating design in database")
        # Creating Design
        design_in = schemas.DesignCreate(
            name=name,
            description=description,
            zip_file_name=zip_file_name,
            condensed=False,
        )
        design = crud.design.create(
            db=db,
            obj_in=design_in,
            owner_id=current_user.id,
            experiment_id=experiment_id,
        )

        # Creating RawDesign
        rawdesign_in = schemas.RawDesignCreate(
            name=zip_json["zip_file_name"], data=zip_json
        )
        crud.rawdesign.create(
            db=db,
            obj_in=rawdesign_in,
            owner_id=current_user.id,
            design_id=design.id,
        )

        logger.debug("Adding design data to database")
        # Process Design to db
        process_design_to_db(
            db=db,
            zip_json=zip_json,
            owner_id=current_user.id,
            design_id=design.id,
        )
    finally:
        design_file.file.close()
    return design
