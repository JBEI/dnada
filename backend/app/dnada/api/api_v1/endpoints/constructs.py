from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dnada import crud, models, schemas
from dnada.api import deps

router = APIRouter()


@router.get("/constructs", response_model=List[schemas.Construct])
def read_constructs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve constructs.
    """
    if crud.user.is_superuser(current_user):
        constructs = crud.construct.get_multi(db, skip=skip, limit=limit)
    else:
        constructs = crud.construct.get_multi(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return constructs


@router.post("/constructs/find", response_model=List[schemas.Construct])
def find_constructs(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.ConstructUpdate,
    design_id: int,
) -> Any:
    """
    Find constructs.
    """
    constructs = crud.construct.find(db=db, design_id=design_id, obj_in=search_obj)
    return constructs


@router.post("/constructs/get_or_create", response_model=schemas.Construct)
def get_or_create_construct(
    *,
    db: Session = Depends(deps.get_db),
    construct_in: schemas.ConstructCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get or create construct
    """
    construct, created = crud.construct.get_or_create(
        db=db, owner_id=current_user.id, obj_in=construct_in
    )
    return construct


@router.get("/constructs/{id}", response_model=schemas.Construct)
def read_construct(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get construct by ID.
    """
    construct = crud.construct.get(db=db, id=id)
    if not construct:
        raise HTTPException(status_code=404, detail="Construct not found")
    if not crud.user.is_superuser(current_user) and (
        construct.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return construct


@router.post("/constructs", response_model=schemas.Construct)
def create_construct(
    *,
    db: Session = Depends(deps.get_db),
    construct_in: schemas.ConstructCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new construct.
    """
    construct = crud.construct.create(
        db=db, obj_in=construct_in, owner_id=current_user.id
    )
    return construct


@router.put("/constructs/{id}", response_model=schemas.Construct)
def update_construct(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    construct_in: schemas.ConstructUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an construct.
    """
    construct = crud.construct.get(db=db, id=id)
    if not construct:
        raise HTTPException(status_code=404, detail="Construct not found")
    if not crud.user.is_superuser(current_user) and (
        construct.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    construct = crud.construct.update(db=db, db_obj=construct, obj_in=construct_in)
    return construct


@router.delete("/constructs/{id}", response_model=schemas.Construct)
def delete_construct(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an construct.
    """
    construct = crud.construct.get(db=db, id=id)
    if not construct:
        raise HTTPException(status_code=404, detail="Construct not found")
    if not crud.user.is_superuser(current_user) and (
        construct.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail=("Not enough permissions"))
    construct = crud.construct.remove(db=db, id=id)
    return construct
