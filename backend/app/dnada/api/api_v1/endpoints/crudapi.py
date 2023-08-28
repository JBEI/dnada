from typing import Any, Generic, TypeVar

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from dnada import crud, models
from dnada.api import deps
from dnada.crud.base import CRUDBaseOwner

# Example basic api setup
# from .crudapi import CRUDAPI
# api_experiment = CRUDAPI[
#     schemas.Experiment, schemas.ExperimentCreate,schemas.ExperimentUpdate
# ](crud.experiment)
# # router.add_api_route(
# #     path="/experiments",
# #     endpoint=api_experiment.create_item,
# #     response_model=schemas.Experiment,
# #     methods=["POST"],
# #     name="create_experiment",
# #     summary="Create Experiment",
# #     description="Create new experiment",
# # )
# create_experiment = (
#     router.post("/experiments", response_model=schemas.Experiment)
# )(api_experiment.create_item)
# read_experiment = (
#     router.get("/experiments/{id}", response_model=schemas.Experiment)
# )(api_experiment.read_item)
# read_experiments = (
#     router.get("/experiments", response_model=List[schemas.Experiment])
# )(api_experiment.read_items)
# update_experiment = (
#     router.put("/experiments/{id}", response_model=schemas.Experiment)
# )(api_experiment.update_item)
# delete_experiment = (
#     router.delete("/experiments/{id}", response_model=schemas.Experiment)
# )(api_experiment.delete_item)

SchemaType = TypeVar("SchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
CRUDType = TypeVar("CRUDType", bound=CRUDBaseOwner)


class CRUDAPI(Generic[SchemaType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, crud_model: CRUDType):
        self.crud_model = crud_model

    def create_item(
        self,
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        item_in: CreateSchemaType,
    ) -> Any:
        """
        Create new item
        """
        item = self.crud_model.create(
            db=db,
            obj_in=item_in,
            owner_id=current_user.id,
        )
        return item

    def read_items(
        self,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        skip: int = 0,
        limit: int = 100,
    ) -> Any:
        """
        Retrieve items.
        """
        if crud.user.is_superuser(current_user):
            items = self.crud_model.get_multi(db, skip=skip, limit=limit)
        else:
            items = self.crud_model.get_multi(
                db=db, skip=skip, limit=limit, owner_id=current_user.id
            )
        return items

    def read_item(
        self,
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        id: int,
    ) -> Any:
        """
        Get item by ID.
        """
        item = self.crud_model.get(db=db, id=id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if not crud.user.is_superuser(current_user) and (
            item.owner_id != current_user.id
        ):
            raise HTTPException(status_code=400, detail="Not enough permissions")
        return item

    def update_item(
        self,
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        id: int,
        item_in: UpdateSchemaType,
    ) -> Any:
        """
        Update an item.
        """
        item = self.crud_model.get(db=db, id=id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if not crud.user.is_superuser(current_user) and (
            item.owner_id != current_user.id
        ):
            raise HTTPException(status_code=400, detail="Not enough permissions")
        item = self.crud_model.update(db=db, db_obj=item, obj_in=item_in)
        return item

    def delete_item(
        self,
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        id: int,
    ) -> Any:
        """
        Delete an item.
        """
        item = self.crud_model.get(db=db, id=id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if not crud.user.is_superuser(current_user) and (
            item.owner_id != current_user.id
        ):
            raise HTTPException(status_code=400, detail="Not enough permissions")
        item = self.crud_model.remove(db=db, id=id)
        return item


'''
class CRUDAPIExperiment(
    CRUDAPI[SchemaType, CreateSchemaType, UpdateSchemaType, CRUDType]
):
    def create_item(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        item_in: CreateSchemaType,
        experiment_id: int,
    ) -> SchemaType:
        """
        Create new item.
        """
        item = CRUDType.create(
            db=db,
            obj_in=item_in,
            owner_id=current_user.id,
            experiment_id=experiment_id,
        )
        return item


class CRUDAPIDesign(
    CRUDAPI[SchemaType, CreateSchemaType, UpdateSchemaType, CRUDType]
):
    def create_item(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        item_in: CreateSchemaType,
        design_id: int,
    ) -> SchemaType:
        """
        Create new item.
        """
        item = CRUDType.create(
            db=db,
            obj_in=item_in,
            owner_id=current_user.id,
            design_id=design_id,
        )
        return item


class CRUDAPIPart(
    CRUDAPI[SchemaType, CreateSchemaType, UpdateSchemaType, CRUDType]
):
    def create_item(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        item_in: CreateSchemaType,
        part_id: int,
    ) -> SchemaType:
        """
        Create new item.
        """
        item = CRUDType.create(
            db=db,
            obj_in=item_in,
            owner_id=current_user.id,
            part_id=part_id,
        )
        return item


class CRUDAPIDesignPart(
    CRUDAPI[SchemaType, CreateSchemaType, UpdateSchemaType, CRUDType]
):
    def create_item(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        item_in: CreateSchemaType,
        design_id: int,
        part_id: int,
    ) -> SchemaType:
        """
        Create new item.
        """
        item = CRUDType.create(
            db=db,
            obj_in=item_in,
            owner_id=current_user.id,
            design_id=design_id,
            part_id=part_id,
        )
        return item


class CRUDAPIPartSynth(
    CRUDAPI[SchemaType, CreateSchemaType, UpdateSchemaType, CRUDType]
):
    def create_item(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        item_in: CreateSchemaType,
        part_id: int,
        synth_id: Optional[int] = None,
    ) -> SchemaType:
        """
        Create new item.
        """
        item = CRUDType.create(
            db=db,
            obj_in=item_in,
            owner_id=current_user.id,
            design_id=design_id,
            part_id=part_id,
        )
        return item
'''
