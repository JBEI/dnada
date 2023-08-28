from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dnada import crud, models, schemas
from dnada.api import deps

router = APIRouter()


@router.get("/oligos", response_model=List[schemas.Oligo])
def read_oligos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    design_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve oligos.
    """
    if crud.user.is_superuser(current_user):
        oligos = crud.oligo.get_multi(
            db,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    else:
        oligos = crud.oligo.get_multi(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    return oligos


@router.post("/oligos/find", response_model=List[schemas.Oligo])
def find_oligos(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.OligoUpdate,
    design_id: int,
) -> Any:
    """
    Find oligos.
    """
    oligos = crud.oligo.find(db=db, design_id=design_id, obj_in=search_obj)
    return oligos


@router.post("/oligos", response_model=schemas.Oligo)
def create_oligo(
    *,
    db: Session = Depends(deps.get_db),
    oligo_in: schemas.OligoCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    design_id: int,
) -> Any:
    """
    Create new oligo.
    """
    oligo = crud.oligo.create(
        db=db,
        obj_in=oligo_in,
        owner_id=current_user.id,
        design_id=design_id,
    )
    return oligo


@router.put("/oligos/{id}", response_model=schemas.Oligo)
def update_oligo(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    oligo_in: schemas.OligoUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an oligo.
    """
    oligo = crud.oligo.get(db=db, id=id)
    if not oligo:
        raise HTTPException(status_code=404, detail="Oligo not found")
    if not crud.user.is_superuser(current_user) and (oligo.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    oligo = crud.oligo.update(db=db, db_obj=oligo, obj_in=oligo_in)
    return oligo


@router.get("/oligos/{id}", response_model=schemas.Oligo)
def read_oligo(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get oligo by ID.
    """
    oligo = crud.oligo.get(db=db, id=id)
    if not oligo:
        raise HTTPException(status_code=404, detail="Oligo not found")
    if not crud.user.is_superuser(current_user) and (oligo.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return oligo


@router.delete("/oligos/{id}", response_model=schemas.Oligo)
def delete_oligo(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an oligo.
    """
    oligo = crud.oligo.get(db=db, id=id)
    if not oligo:
        raise HTTPException(status_code=404, detail="Oligo not found")
    if not crud.user.is_superuser(current_user) and (oligo.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    oligo = crud.oligo.remove(db=db, id=id)
    return oligo
