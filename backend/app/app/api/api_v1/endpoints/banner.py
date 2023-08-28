from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.put("/banner", response_model=schemas.Banner)
async def update_banner(
    *,
    db: Session = Depends(deps.get_db),
    banner_in: schemas.BannerUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update app banner.
    """
    banner = crud.banner.get(db=db)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    banner = crud.banner.update(db=db, db_obj=banner, obj_in=banner_in)
    return banner


@router.get("/banner", response_model=schemas.Banner)
async def read_banner(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get app banner
    """
    banner = crud.banner.get(db=db)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return banner
