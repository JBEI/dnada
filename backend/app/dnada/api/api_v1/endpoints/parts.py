from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dnada import crud, models, schemas
from dnada.api import deps

router = APIRouter()


@router.get("/parts", response_model=List[schemas.Part])
def read_parts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    design_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve parts.
    """
    if crud.user.is_superuser(current_user):
        parts = crud.part.get_multi(
            db,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    else:
        parts = crud.part.get_multi(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    return parts


@router.post("/parts/find", response_model=List[schemas.Part])
def find_parts(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.PartUpdate,
    design_id: int,
) -> Any:
    """
    Find parts.
    """
    parts = crud.part.find(db=db, design_id=design_id, obj_in=search_obj)
    return parts


@router.post("/parts", response_model=schemas.Part)
def create_part(
    *,
    db: Session = Depends(deps.get_db),
    part_in: schemas.PartCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    design_id: int,
) -> Any:
    """
    Create new part.
    """
    part = crud.part.create(
        db=db,
        obj_in=part_in,
        owner_id=current_user.id,
        design_id=design_id,
    )
    return part


@router.put("/parts/{id}", response_model=schemas.Part)
def update_part(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    part_in: schemas.PartUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an part.
    """
    part = crud.part.get(db=db, id=id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    if not crud.user.is_superuser(current_user) and (part.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    part = crud.part.update(db=db, db_obj=part, obj_in=part_in)
    return part


@router.get("/parts/{id}", response_model=schemas.Part)
def read_part(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get part by ID.
    """
    part = crud.part.get(db=db, id=id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    if not crud.user.is_superuser(current_user) and (part.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return part


@router.delete("/parts/{id}", response_model=schemas.Part)
def delete_part(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an part.
    """
    part = crud.part.get(db=db, id=id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    if not crud.user.is_superuser(current_user) and (part.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    part = crud.part.remove(db=db, id=id)
    return part
