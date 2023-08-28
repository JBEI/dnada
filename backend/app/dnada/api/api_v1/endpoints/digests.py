from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dnada import crud, models, schemas
from dnada.api import deps

router = APIRouter()


@router.get("/digests", response_model=List[schemas.Digest])
def read_digests(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    design_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve digests.
    """
    if crud.user.is_superuser(current_user):
        digests = crud.digest.get_multi(
            db,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    else:
        digests = crud.digest.get_multi(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    return digests


@router.post("/digests/find", response_model=List[schemas.Digest])
def find_digests(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.DigestUpdate,
    part_id: int,
) -> Any:
    """
    Find digests.
    """
    digests = crud.digest.find(db=db, part_id=part_id, obj_in=search_obj)
    return digests


@router.post("/digests", response_model=schemas.Digest)
def create_digest(
    *,
    db: Session = Depends(deps.get_db),
    digest_in: schemas.DigestCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    part_id: int,
) -> Any:
    """
    Create new digest.
    """
    digest = crud.digest.create(
        db=db,
        obj_in=digest_in,
        owner_id=current_user.id,
        part_id=part_id,
    )
    return digest


@router.put("/digests/{id}", response_model=schemas.Digest)
def update_digest(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    digest_in: schemas.DigestUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an digest.
    """
    digest = crud.digest.get(db=db, id=id)
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    if not crud.user.is_superuser(current_user) and (
        digest.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    digest = crud.digest.update(db=db, db_obj=digest, obj_in=digest_in)
    return digest


@router.get("/digests/{id}", response_model=schemas.Digest)
def read_digest(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get digest by ID.
    """
    digest = crud.digest.get(db=db, id=id)
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    if not crud.user.is_superuser(current_user) and (
        digest.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return digest


@router.delete("/digests/{id}", response_model=schemas.Digest)
def delete_digest(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an digest.
    """
    digest = crud.digest.get(db=db, id=id)
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    if not crud.user.is_superuser(current_user) and (
        digest.owner_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    digest = crud.digest.remove(db=db, id=id)
    return digest
