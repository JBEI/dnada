from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/instructions", response_model=List[schemas.Instruction])
def read_instructions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    experiment_id: Optional[int] = None,
    design_id: Optional[int] = None,
    workflow_id: Optional[int] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve instructions.
    """
    if crud.user.is_superuser(current_user):
        instructions = crud.instruction.get_multi(
            db,
            skip=skip,
            limit=limit,
            experiment_id=experiment_id,
            design_id=design_id,
            workflow_id=workflow_id,
        )
    else:
        instructions = crud.instruction.get_multi(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=limit,
            experiment_id=experiment_id,
            design_id=design_id,
            workflow_id=workflow_id,
        )
    return instructions


@router.post(
    "/instructions/find", response_model=List[schemas.Instruction]
)
def find_instructions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.InstructionUpdate,
    workflow_id: int,
) -> Any:
    """
    Find instructions.
    """
    instructions = crud.instruction.find(
        db=db, workflow_id=workflow_id, obj_in=search_obj
    )
    return instructions


@router.get("/instructions/pcr", response_model=List[schemas.Instruction])
def read_pcr_instructions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    experiment_id: Optional[int] = None,
    design_id: Optional[int] = None,
    workflow_id: Optional[int] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve pcr instructions.
    """
    if crud.user.is_superuser(current_user):
        instructions = crud.instruction.get_multi(
            db,
            skip=skip,
            limit=limit,
            experiment_id=experiment_id,
            design_id=design_id,
            workflow_id=workflow_id,
        )
    else:
        instructions = crud.instruction.get_multi(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=limit,
            experiment_id=experiment_id,
            design_id=design_id,
            workflow_id=workflow_id,
        )
    return [
        instruction
        for instruction in instructions
        if instruction.category.startswith("pcr_worksheet")
    ]


@router.post("/instructions", response_model=schemas.Instruction)
def create_instruction(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    instruction_in: schemas.InstructionCreate,
    workflow_id: int,
) -> Any:
    """
    Create new instruction.
    """
    instruction = crud.instruction.create(
        db=db,
        obj_in=instruction_in,
        owner_id=current_user.id,
        workflow_id=workflow_id,
    )
    return instruction


@router.put("/instructions/{id}", response_model=schemas.Instruction)
def update_instruction(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    instruction_in: schemas.InstructionUpdate,
    id: int,
) -> Any:
    """
    Update an instruction.
    """
    instruction = crud.instruction.get(db=db, id=id)
    if not instruction:
        raise HTTPException(
            status_code=404, detail="Instruction not found"
        )
    if not crud.user.is_superuser(current_user) and (
        instruction.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    instruction = crud.instruction.update(
        db=db, db_obj=instruction, obj_in=instruction_in
    )
    return instruction


@router.get("/instructions/{id}", response_model=schemas.Instruction)
def read_instruction(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: int,
) -> Any:
    """
    Get instruction by ID.
    """
    instruction = crud.instruction.get(db=db, id=id)
    if not instruction:
        raise HTTPException(
            status_code=404, detail="Instruction not found"
        )
    if not crud.user.is_superuser(current_user) and (
        instruction.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return instruction


@router.get("/instructions/{id}/run", response_model=List[schemas.Run])
def read_instruction_runs(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: int,
) -> Any:
    """
    Get instruction by ID.
    """
    instruction = crud.instruction.get(db=db, id=id)
    if not instruction:
        raise HTTPException(
            status_code=404, detail="Instruction not found"
        )
    if not crud.user.is_superuser(current_user) and (
        instruction.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return instruction.runs


@router.delete("/instructions/{id}", response_model=schemas.Instruction)
def delete_instruction(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: int,
) -> Any:
    """
    Delete an instruction.
    """
    instruction = crud.instruction.get(db=db, id=id)
    if not instruction:
        raise HTTPException(
            status_code=404, detail="Instruction not found"
        )
    if not crud.user.is_superuser(current_user) and (
        instruction.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    instruction = crud.instruction.remove(db=db, id=id)
    return instruction
