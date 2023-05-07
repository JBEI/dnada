from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/synths", response_model=List[schemas.Synth])
def read_synths(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    design_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve synths.
    """
    if crud.user.is_superuser(current_user):
        synths = crud.synth.get_multi(
            db,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    else:
        synths = crud.synth.get_multi(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    return synths


@router.post("/synths/find", response_model=List[schemas.Synth])
def find_synths(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.SynthUpdate,
    design_id: int,
) -> Any:
    """
    Find synths.
    """
    synths = crud.synth.find(db=db, design_id=design_id, obj_in=search_obj)
    return synths


@router.post("/synths", response_model=schemas.Synth)
def create_synth(
    *,
    db: Session = Depends(deps.get_db),
    synth_in: schemas.SynthCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    design_id: int,
) -> Any:
    """
    Create new synth.
    """
    synth = crud.synth.create(
        db=db,
        obj_in=synth_in,
        owner_id=current_user.id,
        design_id=design_id,
    )
    return synth


@router.put("/synths/{id}", response_model=schemas.Synth)
def update_synth(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    synth_in: schemas.SynthUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an synth.
    """
    synth = crud.synth.get(db=db, id=id)
    if not synth:
        raise HTTPException(
            status_code=404, detail="schemas.Synth not found"
        )
    if not crud.user.is_superuser(current_user) and (
        synth.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    synth = crud.synth.update(db=db, db_obj=synth, obj_in=synth_in)
    return synth


@router.get("/synths/{id}", response_model=schemas.Synth)
def read_synth(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get synth by ID.
    """
    synth = crud.synth.get(db=db, id=id)
    if not synth:
        raise HTTPException(
            status_code=404, detail="schemas.Synth not found"
        )
    if not crud.user.is_superuser(current_user) and (
        synth.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return synth


@router.delete("/synths/{id}", response_model=schemas.Synth)
def delete_synth(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an synth.
    """
    synth = crud.synth.get(db=db, id=id)
    if not synth:
        raise HTTPException(
            status_code=404, detail="schemas.Synth not found"
        )
    if not crud.user.is_superuser(current_user) and (
        synth.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    synth = crud.synth.remove(db=db, id=id)
    return synth
