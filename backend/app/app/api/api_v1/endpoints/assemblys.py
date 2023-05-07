from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/assemblys", response_model=List[schemas.Assembly])
def read_assemblys(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    design_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve assemblys.
    """
    if crud.user.is_superuser(current_user):
        assemblys = crud.assembly.get_multi(
            db,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    else:
        assemblys = crud.assembly.get_multi(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=limit,
            design_id=design_id,
            experiment_id=experiment_id,
        )
    return assemblys


@router.post("/assemblys/find", response_model=List[schemas.Assembly])
def find_assemblys(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.AssemblyUpdate,
    design_id: int,
) -> Any:
    """
    Find assemblys.
    """
    assemblys = crud.assembly.find(
        db=db, design_id=design_id, obj_in=search_obj
    )
    return assemblys


@router.post("/assemblys", response_model=schemas.Assembly)
def create_assembly(
    *,
    db: Session = Depends(deps.get_db),
    assembly_in: schemas.AssemblyCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    design_id: int,
    part_id: int,
) -> Any:
    """
    Create new assembly.
    """
    assembly = crud.assembly.create(
        db=db,
        obj_in=assembly_in,
        owner_id=current_user.id,
        design_id=design_id,
        part_id=part_id,
    )
    return assembly


@router.put("/assemblys/{id}", response_model=schemas.Assembly)
def update_assembly(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    assembly_in: schemas.AssemblyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an assembly.
    """
    assembly = crud.assembly.get(db=db, id=id)
    if not assembly:
        raise HTTPException(status_code=404, detail="assembly not found")
    if not crud.user.is_superuser(current_user) and (
        assembly.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    assembly = crud.assembly.update(
        db=db, db_obj=assembly, obj_in=assembly_in
    )
    return assembly


@router.get("/assemblys/{id}", response_model=schemas.Assembly)
def read_assembly(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get assembly by ID.
    """
    assembly = crud.assembly.get(db=db, id=id)
    if not assembly:
        raise HTTPException(status_code=404, detail="assembly not found")
    if not crud.user.is_superuser(current_user) and (
        assembly.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return assembly


@router.delete("/assemblys/{id}", response_model=schemas.Assembly)
def delete_assembly(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an assembly.
    """
    assembly = crud.assembly.get(db=db, id=id)
    if not assembly:
        raise HTTPException(status_code=404, detail="assembly not found")
    if not crud.user.is_superuser(current_user) and (
        assembly.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    assembly = crud.assembly.remove(db=db, id=id)
    return assembly
