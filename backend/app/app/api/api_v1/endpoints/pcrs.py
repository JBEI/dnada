from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/pcrs", response_model=List[schemas.PCR])
def read_pcrs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    design_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve pcrs.
    """
    if crud.user.is_superuser(current_user):
        pcrs = crud.pcr.get_multi(
            db,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    else:
        pcrs = crud.pcr.get_multi(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    return pcrs


@router.post("/pcrs/find", response_model=List[schemas.PCR])
def find_pcrs(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.PCRUpdate,
    part_id: int,
) -> Any:
    """
    Find pcrs.
    """
    pcrs = crud.pcr.find(db=db, part_id=part_id, obj_in=search_obj)
    return pcrs


@router.post("/pcrs", response_model=schemas.PCR)
def create_pcr(
    *,
    db: Session = Depends(deps.get_db),
    pcr_in: schemas.PCRCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    part_id: int,
    template_id: int,
    forward_oligo_id: int,
    reverse_oligo_id: int,
) -> Any:
    """
    Create new pcr.
    """
    pcr = crud.pcr.create(
        db=db,
        obj_in=pcr_in,
        owner_id=current_user.id,
        part_id=part_id,
        template_id=template_id,
        forward_oligo_id=forward_oligo_id,
        reverse_oligo_id=reverse_oligo_id,
    )
    return pcr


@router.put("/pcrs/{id}", response_model=schemas.PCR)
def update_pcr(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    pcr_in: schemas.PCRUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an pcr.
    """
    pcr = crud.pcr.get(db=db, id=id)
    if not pcr:
        raise HTTPException(status_code=404, detail="PCR not found")
    if not crud.user.is_superuser(current_user) and (pcr.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    pcr = crud.pcr.update(db=db, db_obj=pcr, obj_in=pcr_in)
    return pcr


@router.get("/pcrs/{id}", response_model=schemas.PCR)
def read_pcr(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get pcr by ID.
    """
    pcr = crud.pcr.get(db=db, id=id)
    if not pcr:
        raise HTTPException(status_code=404, detail="PCR not found")
    if not crud.user.is_superuser(current_user) and (pcr.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return pcr


@router.delete("/pcrs/{id}", response_model=schemas.PCR)
def delete_pcr(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an pcr.
    """
    pcr = crud.pcr.get(db=db, id=id)
    if not pcr:
        raise HTTPException(status_code=404, detail="PCR not found")
    if not crud.user.is_superuser(current_user) and (pcr.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    pcr = crud.pcr.remove(db=db, id=id)
    return pcr
