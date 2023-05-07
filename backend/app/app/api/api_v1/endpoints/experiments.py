from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/experiments", response_model=List[schemas.Experiment])
def read_experiments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve experiments.
    """
    if crud.user.is_superuser(current_user):
        experiments = crud.experiment.get_multi(db, skip=skip, limit=limit)
    else:
        experiments = crud.experiment.get_multi(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return experiments


@router.post("/experiments/find", response_model=List[schemas.Experiment])
def find_experiments(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    search_obj: schemas.ExperimentUpdate,
) -> Any:
    """
    Find experiments.
    """
    experiments = crud.experiment.find(
        db=db, owner_id=current_user.id, obj_in=search_obj
    )
    return experiments


@router.post(
    "/experiments/get_or_create", response_model=schemas.Experiment
)
def get_or_create_experiment(
    *,
    db: Session = Depends(deps.get_db),
    experiment_in: schemas.ExperimentCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get or create experiment
    """
    experiment, created = crud.experiment.get_or_create(
        db=db, owner_id=current_user.id, obj_in=experiment_in
    )
    return experiment


@router.get("/experiments/{id}", response_model=schemas.Experiment)
def read_experiment(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get experiment by ID.
    """
    experiment = crud.experiment.get(db=db, id=id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if not crud.user.is_superuser(current_user) and (
        experiment.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return experiment


@router.post("/experiments", response_model=schemas.Experiment)
def create_experiment(
    *,
    db: Session = Depends(deps.get_db),
    experiment_in: schemas.ExperimentCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new experiment.
    """
    experiment = crud.experiment.create(
        db=db, obj_in=experiment_in, owner_id=current_user.id
    )
    return experiment


@router.put("/experiments/{id}", response_model=schemas.Experiment)
def update_experiment(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    experiment_in: schemas.ExperimentUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an experiment.
    """
    experiment = crud.experiment.get(db=db, id=id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if not crud.user.is_superuser(current_user) and (
        experiment.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    experiment = crud.experiment.update(
        db=db, db_obj=experiment, obj_in=experiment_in
    )
    return experiment


@router.delete("/experiments/{id}", response_model=schemas.Experiment)
def delete_experiment(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an experiment.
    """
    experiment = crud.experiment.get(db=db, id=id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if not crud.user.is_superuser(current_user) and (
        experiment.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail=("Not enough permissions")
        )
    experiment = crud.experiment.remove(db=db, id=id)
    return experiment
