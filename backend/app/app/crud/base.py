from typing import (Any, Dict, Generic, List, Optional, Tuple, Type,
                    TypeVar, Union)

from fastapi.encoders import jsonable_encoder
from pandas import DataFrame, read_json
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.base_class import Base
from app.models.design import Design
from app.models.experiment import Experiment
from app.models.part import Part

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class MultipleObjectsReturned(Exception):
    pass


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete
        (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def find(
        self,
        db: Session,
        *,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        obj_in_data = self._exclude_unset(jsonable_encoder(obj_in))
        db_objs = db.query(self.model).filter_by(**obj_in_data)
        return db_objs.all()

    def find_one_or_none(
        self,
        db: Session,
        *,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_in_data = self._exclude_unset(jsonable_encoder(obj_in))
        db_objs = db.query(self.model).filter_by(**obj_in_data)
        return db_objs.one_or_none()

    def create(
        self, db: Session, *, obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def bulk_create(self, db: Session, *, ready_json: str) -> int:
        objs_in_data = read_json(ready_json)
        num_of_objs_created = self._add_df_to_db(db=db, df=objs_in_data)
        return num_of_objs_created

    def _add_df_to_db(self, db: Session, *, df: DataFrame) -> int:
        df.to_sql(
            self.model.__tablename__,
            con=db.connection(),
            if_exists="append",
            index=False,
        )
        db.commit()
        return df.shape[0]

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        if "password" in update_data:
            setattr(
                db_obj,
                "hashed_password",
                get_password_hash(update_data["password"]),
            )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def bulk_remove(
        self, db: Session, *, ids: List[int]
    ) -> List[ModelType]:
        objs = []
        for id in ids:
            obj = db.query(self.model).get(id)
            db.delete(obj)
            db.commit()
            objs.append(obj)
        return objs

    def find_and_bulk_remove(
        self,
        db: Session,
        *,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        objs: List[ModelType] = self.find(db=db, obj_in=obj_in)
        objs = self.bulk_remove(db=db, ids=[obj.id for obj in objs])
        return objs

    def format_json(
        self,
        db: Session,
        *,
        raw_json: str,
        owner_id: int,
        design_id: int,
        plate_mapping: Optional[Dict[str, int]] = None,
    ) -> str:
        return "PASS"

    def _exclude_unset(self, d: dict) -> dict:
        """Remove entries in dict with value None

        From:
        https://medium.com/better-programming/how-to-remove-
        null-none-values-from-a-dictionary-in-python-1bedf1aab5e4
        """
        clean = {}
        for key, value in d.items():
            if isinstance(value, dict):
                nested = self._exclude_unset(value)
                if len(nested.keys()) > 0:
                    clean[key] = nested
            elif value is not None:
                clean[key] = value
        return clean


class CRUDBaseOwner(
    CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]
):

    """CRUDBase with an Owner present"""

    def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
    ) -> List[ModelType]:
        baseQuery = db.query(self.model)
        if owner_id is not None:
            baseQuery = baseQuery.filter(self.model.owner_id == owner_id)
        return baseQuery.offset(skip).limit(limit).all()

    def find(
        self,
        db: Session,
        *,
        owner_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        obj_in_data = self._exclude_unset(jsonable_encoder(obj_in))
        db_objs = db.query(self.model).filter_by(
            owner_id=owner_id, **obj_in_data
        )
        return db_objs.all()

    def find_and_bulk_remove(
        self,
        db: Session,
        *,
        owner_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        objs: List[ModelType] = self.find(
            db=db, obj_in=obj_in, owner_id=owner_id
        )
        objs = self.bulk_remove(db=db, ids=[obj.id for obj in objs])
        return objs

    def get_or_create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
    ) -> Tuple[ModelType, bool]:
        created: bool = False  # boolean specifying whether new obj created
        db_objs = self.find(db=db, owner_id=owner_id, obj_in=obj_in)
        if len(db_objs) == 0:
            db_obj = self.create(db=db, obj_in=obj_in, owner_id=owner_id)
            created = True
        elif len(db_objs) == 1:
            db_obj = db_objs[0]
        else:
            # If more than one "identical" object found, then raise error
            raise MultipleObjectsReturned(db_objs)
        return (db_obj, created)

    def update_or_create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        defaults: UpdateSchemaType,
    ) -> Tuple[ModelType, bool]:
        created: bool = False  # boolean specifying whether new obj created
        db_objs = self.find(db=db, owner_id=owner_id, obj_in=obj_in)
        if len(db_objs) == 0:
            db_obj = self.create(db=db, obj_in=obj_in, owner_id=owner_id)
            db_obj = self.update(db=db, db_obj=db_obj, obj_in=defaults)
            created = True
        elif len(db_objs) == 1:
            db_obj = self.update(db=db, db_obj=db_objs[0], obj_in=defaults)
        else:
            # If more than one "identical" object found, then raise error
            raise MultipleObjectsReturned(db_objs)
        return (db_obj, created)

    def update_or_create_old(
        self, db: Session, *, obj_in: UpdateSchemaType, owner_id: int
    ) -> Tuple[ModelType, bool]:
        created: bool = False  # boolean specifying whether new obj created
        db_objs = self.find(db=db, owner_id=owner_id, obj_in=obj_in)
        if len(db_objs) == 0:
            db_obj = self.create(db=db, obj_in=obj_in, owner_id=owner_id)
            created = True
        elif len(db_objs) == 1:
            db_obj = self.update(
                db=db, db_obj=db_objs[0], obj_in=jsonable_encoder(obj_in)
            )
        else:
            # If more than one "identical" object found, then delete all
            # objects except last one, and update last one
            for obj in db_objs[:-1]:
                self.remove(db=db, id=obj.id)
            db_obj = self.update(
                db=db, db_obj=db_objs[-1], obj_in=jsonable_encoder(obj_in)
            )
        return (db_obj, created)


class CRUDBaseExperiment(
    CRUDBaseOwner[ModelType, CreateSchemaType, UpdateSchemaType]
):

    """CRUDBase with an Owner and Experiment present"""

    def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        experiment_id: int,
    ) -> ModelType:
        try:
            obj_in_data = jsonable_encoder(obj_in)
        except UnicodeDecodeError:
            # Dumb Hack to store resultzip in database
            # This is because jsonable_encoder can't decode cp437 encoded
            # bytes. It by default decodes bytes using utf-8 which won't
            # work with zip file
            # See these issues on pydantic:
            # https://github.com/samuelcolvin/pydantic/issues/692
            # https://github.com/samuelcolvin/pydantic/issues/951
            obj_in_data = {"data": obj_in.data}
        db_obj = self.model(
            **obj_in_data, owner_id=owner_id, experiment_id=experiment_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
        experiment_id: Optional[int] = None,
    ) -> List[ModelType]:
        baseQuery = db.query(self.model)
        if owner_id is not None:
            baseQuery = baseQuery.filter(self.model.owner_id == owner_id)
        if experiment_id is not None:
            baseQuery = baseQuery.filter(
                self.model.experiment_id == experiment_id
            )
        return baseQuery.offset(skip).limit(limit).all()

    def find(
        self,
        db: Session,
        *,
        experiment_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        obj_in_data = self._exclude_unset(jsonable_encoder(obj_in))
        db_objs = db.query(self.model).filter_by(
            experiment_id=experiment_id, **obj_in_data
        )
        return db_objs.all()

    def find_and_bulk_remove(
        self,
        db: Session,
        *,
        experiment_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        objs: List[ModelType] = self.find(
            db=db, obj_in=obj_in, experiment_id=experiment_id
        )
        objs = self.bulk_remove(db=db, ids=[obj.id for obj in objs])
        return objs

    def update_or_create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        experiment_id: int,
    ) -> Tuple[ModelType, bool]:
        created: bool = False  # boolean specifying whether new obj created
        db_objs = self.find(
            db=db, experiment_id=experiment_id, obj_in=obj_in
        )
        if len(db_objs) == 0:
            db_obj = self.create(
                db=db,
                obj_in=obj_in,
                owner_id=owner_id,
                experiment_id=experiment_id,
            )
            created = True
        elif len(db_objs) == 1:
            db_obj = self.update(
                db=db, db_obj=db_objs[0], obj_in=jsonable_encoder(obj_in)
            )
        else:
            # If more than one "identical" object found, then delete all
            # objects except last one, and update last one
            for obj in db_objs[:-1]:
                self.remove(db=db, id=obj.id)
            db_obj = self.update(
                db=db, db_obj=db_objs[-1], obj_in=jsonable_encoder(obj_in)
            )
        return (db_obj, created)


class CRUDBaseDesign(
    CRUDBaseExperiment[ModelType, CreateSchemaType, UpdateSchemaType]
):

    """CRUDBase with an Owner, Experiment, and Design present"""

    def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        design_id: int,
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data, owner_id=owner_id, design_id=design_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
        experiment_id: Optional[int] = None,
        design_id: Optional[int] = None,
    ) -> List[ModelType]:
        baseQuery = db.query(self.model)
        if owner_id is not None:
            baseQuery = baseQuery.filter(self.model.owner_id == owner_id)
        if experiment_id is not None:
            baseQuery = (
                baseQuery.join(Design)
                .join(Experiment)
                .filter(Experiment.id == experiment_id)
            )
        if design_id is not None:
            baseQuery = baseQuery.filter(self.model.design_id == design_id)
        return baseQuery.offset(skip).limit(limit).all()

    def find(
        self,
        db: Session,
        *,
        design_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        obj_in_data = self._exclude_unset(jsonable_encoder(obj_in))
        db_objs = db.query(self.model).filter_by(
            design_id=design_id, **obj_in_data
        )
        return db_objs.all()

    def find_and_bulk_remove(
        self,
        db: Session,
        *,
        design_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        objs: List[ModelType] = self.find(
            db=db, obj_in=obj_in, design_id=design_id
        )
        objs = self.bulk_remove(db=db, ids=[obj.id for obj in objs])
        return objs

    def update_or_create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        design_id: int,
    ) -> Tuple[ModelType, bool]:
        created: bool = False  # boolean specifying whether new obj created
        db_objs = self.find(db=db, design_id=design_id, obj_in=obj_in)
        if len(db_objs) == 0:
            db_obj = self.create(
                db=db,
                obj_in=obj_in,
                owner_id=owner_id,
                design_id=design_id,
            )
            created = True
        elif len(db_objs) == 1:
            db_obj = self.update(
                db=db, db_obj=db_objs[0], obj_in=jsonable_encoder(obj_in)
            )
        else:
            # If more than one "identical" object found, then delete all
            # objects except last one, and update last one
            for obj in db_objs[:-1]:
                self.remove(db=db, id=obj.id)
            db_obj = self.update(
                db=db, db_obj=db_objs[-1], obj_in=jsonable_encoder(obj_in)
            )
        return (db_obj, created)


class CRUDBasePart(
    CRUDBaseDesign[ModelType, CreateSchemaType, UpdateSchemaType]
):

    """CRUDBase with an Owner, Experiment, Design, and Part present"""

    def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        part_id: int,
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data, owner_id=owner_id, part_id=part_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
        experiment_id: Optional[int] = None,
        design_id: Optional[int] = None,
        part_id: Optional[int] = None,
    ) -> List[ModelType]:
        baseQuery = db.query(self.model)
        if owner_id is not None:
            baseQuery = baseQuery.filter(self.model.owner_id == owner_id)
        if experiment_id is not None:
            baseQuery = (
                baseQuery.join(Part)
                .join(Design)
                .join(Experiment)
                .filter(Experiment.id == experiment_id)
            )
        if design_id is not None:
            baseQuery = (
                baseQuery.join(Part)
                .join(Design)
                .filter(Design.id == design_id)
            )
        if part_id is not None:
            baseQuery = baseQuery.filter(self.model.part_id == part_id)
        return baseQuery.offset(skip).limit(limit).all()

    def find(
        self,
        db: Session,
        *,
        part_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        obj_in_data = self._exclude_unset(jsonable_encoder(obj_in))
        db_objs = db.query(self.model).filter_by(
            part_id=part_id, **obj_in_data
        )
        return db_objs.all()

    def find_and_bulk_remove(
        self,
        db: Session,
        *,
        part_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        objs: List[ModelType] = self.find(
            db=db, obj_in=obj_in, part_id=part_id
        )
        objs = self.bulk_remove(db=db, ids=[obj.id for obj in objs])
        return objs

    def update_or_create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        part_id: int,
    ) -> Tuple[ModelType, bool]:
        created: bool = False  # boolean specifying whether new obj created
        db_objs = self.find(db=db, part_id=part_id, obj_in=obj_in)
        if len(db_objs) == 0:
            db_obj = self.create(
                db=db,
                obj_in=obj_in,
                owner_id=owner_id,
                part_id=part_id,
            )
            created = True
        elif len(db_objs) == 1:
            db_obj = self.update(
                db=db, db_obj=db_objs[0], obj_in=jsonable_encoder(obj_in)
            )
        else:
            # If more than one "identical" object found, then delete all
            # objects except last one, and update last one
            for obj in db_objs[:-1]:
                self.remove(db=db, id=obj.id)
            db_obj = self.update(
                db=db, db_obj=db_objs[-1], obj_in=jsonable_encoder(obj_in)
            )
        return (db_obj, created)


class CRUDBaseWorkflow(
    CRUDBaseDesign[ModelType, CreateSchemaType, UpdateSchemaType]
):

    """CRUDBase with an Owner, Experiment, Design, and Workflow present"""

    def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        workflow_id: int,
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data, owner_id=owner_id, workflow_id=workflow_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
        experiment_id: Optional[int] = None,
        design_id: Optional[int] = None,
        workflow_id: Optional[int] = None,
    ) -> List[ModelType]:
        baseQuery = db.query(self.model)
        if owner_id is not None:
            baseQuery = baseQuery.filter(self.model.owner_id == owner_id)
        if experiment_id is not None:
            baseQuery = (
                baseQuery.join(Workflow)
                .join(Design)
                .join(Experiment)
                .filter(Experiment.id == experiment_id)
            )
        if design_id is not None:
            baseQuery = (
                baseQuery.join(Workflow)
                .join(Design)
                .filter(Design.id == design_id)
            )
        if workflow_id is not None:
            baseQuery = baseQuery.filter(
                self.model.workflow_id == workflow_id
            )
        return baseQuery.offset(skip).limit(limit).all()

    def find(
        self,
        db: Session,
        *,
        workflow_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        obj_in_data = self._exclude_unset(jsonable_encoder(obj_in))
        db_objs = db.query(self.model).filter_by(
            workflow_id=workflow_id, **obj_in_data
        )
        return db_objs.all()

    def find_and_bulk_remove(
        self,
        db: Session,
        *,
        workflow_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        objs: List[ModelType] = self.find(
            db=db, obj_in=obj_in, workflow_id=workflow_id
        )
        objs = self.bulk_remove(db=db, ids=[obj.id for obj in objs])
        return objs

    def update_or_create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        workflow_id: int,
    ) -> Tuple[ModelType, bool]:
        created: bool = False  # boolean specifying whether new obj created
        db_objs = self.find(db=db, workflow_id=workflow_id, obj_in=obj_in)
        if len(db_objs) == 0:
            db_obj = self.create(
                db=db,
                obj_in=obj_in,
                owner_id=owner_id,
                workflow_id=workflow_id,
            )
            created = True
        elif len(db_objs) == 1:
            db_obj = self.update(
                db=db, db_obj=db_objs[0], obj_in=jsonable_encoder(obj_in)
            )
        else:
            # If more than one "identical" object found, then delete all
            # objects except last one, and update last one
            for obj in db_objs[:-1]:
                self.remove(db=db, id=obj.id)
            db_obj = self.update(
                db=db, db_obj=db_objs[-1], obj_in=jsonable_encoder(obj_in)
            )
        return (db_obj, created)


class CRUDBaseInstruction(
    CRUDBaseWorkflow[ModelType, CreateSchemaType, UpdateSchemaType]
):

    """CRUDBase with an Instruction present"""

    def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        instruction_id: int,
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data, owner_id=owner_id, instruction_id=instruction_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
        experiment_id: Optional[int] = None,
        design_id: Optional[int] = None,
        workflow_id: Optional[int] = None,
        instruction_id: Optional[int] = None,
    ) -> List[ModelType]:
        baseQuery = db.query(self.model)
        if owner_id is not None:
            baseQuery = baseQuery.filter(self.model.owner_id == owner_id)
        if experiment_id is not None:
            baseQuery = (
                baseQuery.join(Workflow)
                .join(Design)
                .join(Experiment)
                .filter(Experiment.id == experiment_id)
            )
        if design_id is not None:
            baseQuery = (
                baseQuery.join(Workflow)
                .join(Design)
                .filter(Design.id == design_id)
            )
        if workflow_id is not None:
            baseQuery = baseQuery.filter(
                self.model.workflow_id == workflow_id
            )
        if instruction_id is not None:
            pass
        return baseQuery.offset(skip).limit(limit).all()

    def find(
        self,
        db: Session,
        *,
        instruction_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        obj_in_data = self._exclude_unset(jsonable_encoder(obj_in))
        db_objs = db.query(self.model).filter_by(
            instruction_id=instruction_id, **obj_in_data
        )
        return db_objs.all()

    def find_and_bulk_remove(
        self,
        db: Session,
        *,
        instruction_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        objs: List[ModelType] = self.find(
            db=db, obj_in=obj_in, instruction_id=instruction_id
        )
        objs = self.bulk_remove(db=db, ids=[obj.id for obj in objs])
        return objs

    def update_or_create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        instruction_id: int,
    ) -> Tuple[ModelType, bool]:
        created: bool = False  # boolean specifying whether new obj created
        db_objs = self.find(
            db=db, instruction_id=instruction_id, obj_in=obj_in
        )
        if len(db_objs) == 0:
            db_obj = self.create(
                db=db,
                obj_in=obj_in,
                owner_id=owner_id,
                instruction_id=instruction_id,
            )
            created = True
        elif len(db_objs) == 1:
            db_obj = self.update(
                db=db, db_obj=db_objs[0], obj_in=jsonable_encoder(obj_in)
            )
        else:
            # If more than one "identical" object found, then delete all
            # objects except last one, and update last one
            for obj in db_objs[:-1]:
                self.remove(db=db, id=obj.id)
            db_obj = self.update(
                db=db, db_obj=db_objs[-1], obj_in=jsonable_encoder(obj_in)
            )
        return (db_obj, created)


class CRUDBaseWell(
    CRUDBaseWorkflow[ModelType, CreateSchemaType, UpdateSchemaType]
):

    """CRUDBase with an Owner, Experiment, Design, Plate, and some
    type of content present, e.g. Oligo, Digest, PCR"""

    def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        plate_id: int,
        content_id: int,
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data,
            owner_id=owner_id,
            plate_id=plate_id,
            content_id=content_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
        experiment_id: Optional[int] = None,
        design_id: Optional[int] = None,
        plate_id: Optional[int] = None,
    ) -> List[ModelType]:
        baseQuery = db.query(self.model)
        if owner_id is not None:
            baseQuery = baseQuery.filter(self.model.owner_id == owner_id)
        if experiment_id is not None:
            baseQuery = (
                baseQuery.join(Design)
                .join(Experiment)
                .filter(Experiment.id == experiment_id)
            )
        if design_id is not None:
            baseQuery = baseQuery.filter(self.model.design_id == design_id)
        if plate_id is not None:
            baseQuery = baseQuery.filter(self.model.plate_id == plate_id)
        return baseQuery.offset(skip).limit(limit).all()

    def _add_df_to_db(self, db: Session, *, df: DataFrame) -> int:
        contents = df.to_dict(orient="records")
        wells = [self.model(**content) for content in contents]
        db.add_all(wells)
        db.commit()
        return len(wells)

    def find(
        self,
        db: Session,
        *,
        plate_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        obj_in_data = self._exclude_unset(jsonable_encoder(obj_in))
        db_objs = db.query(self.model).filter_by(
            plate_id=plate_id, **obj_in_data
        )
        return db_objs.all()

    def find_and_bulk_remove(
        self,
        db: Session,
        *,
        plate_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        objs: List[ModelType] = self.find(
            db=db, obj_in=obj_in, plate_id=plate_id
        )
        objs = self.bulk_remove(db=db, ids=[obj.id for obj in objs])
        return objs

    def update_or_create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        plate_id: int,
        content_id: int,
    ) -> Tuple[ModelType, bool]:
        created: bool = False  # boolean specifying whether new obj created
        db_objs = self.find(db=db, plate_id=plate_id, obj_in=obj_in)
        if len(db_objs) == 0:
            db_obj = self.create(
                db=db,
                obj_in=obj_in,
                owner_id=owner_id,
                plate_id=plate_id,
                content_id=content_id,
            )
            created = True
        elif len(db_objs) == 1:
            db_obj = self.update(
                db=db, db_obj=db_objs[0], obj_in=jsonable_encoder(obj_in)
            )
        else:
            # If more than one "identical" object found, then delete all
            # objects except last one, and update last one
            for obj in db_objs[:-1]:
                self.remove(db=db, id=obj.id)
            db_obj = self.update(
                db=db, db_obj=db_objs[-1], obj_in=jsonable_encoder(obj_in)
            )
        return (db_obj, created)


class CRUDBaseResult(
    CRUDBaseWorkflow[ModelType, CreateSchemaType, UpdateSchemaType]
):

    """CRUDBase with an Owner, Experiment, Design, Run, and some
    type of sample present, e.g. PCR"""

    def create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        run_id: int,
        sample_id: int,
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data,
            owner_id=owner_id,
            run_id=run_id,
            sample_id=sample_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
        experiment_id: Optional[int] = None,
        design_id: Optional[int] = None,
        workflow_id: Optional[int] = None,
        run_id: Optional[int] = None,
    ) -> List[ModelType]:
        baseQuery = db.query(self.model)
        if owner_id is not None:
            baseQuery = baseQuery.filter(self.model.owner_id == owner_id)
        if experiment_id is not None:
            baseQuery = (
                baseQuery.join(Run)
                .join(Workflow)
                .join(Design)
                .join(Experiment)
                .filter(Experiment.id == experiment_id)
            )
        if design_id is not None:
            baseQuery = baseQuery.filter(self.model.design_id == design_id)
        if run_id is not None:
            baseQuery = baseQuery.filter(self.model.run_id == run_id)
        return baseQuery.offset(skip).limit(limit).all()

    def _add_df_to_db(self, db: Session, *, df: DataFrame) -> int:
        contents = df.to_dict(orient="records")
        wells = [self.model(**content) for content in contents]
        db.add_all(wells)
        db.commit()
        return len(wells)

    def find(
        self,
        db: Session,
        *,
        run_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        obj_in_data = self._exclude_unset(jsonable_encoder(obj_in))
        db_objs = db.query(self.model).filter_by(
            run_id=run_id, **obj_in_data
        )
        return db_objs.all()

    def find_and_bulk_remove(
        self,
        db: Session,
        *,
        run_id: int,
        obj_in: Union[CreateSchemaType, UpdateSchemaType, Dict[str, Any]],
    ) -> List[ModelType]:
        objs: List[ModelType] = self.find(
            db=db, obj_in=obj_in, run_id=run_id
        )
        objs = self.bulk_remove(db=db, ids=[obj.id for obj in objs])
        return objs

    def update_or_create(
        self,
        db: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: int,
        run_id: int,
        sample_id: int,
    ) -> Tuple[ModelType, bool]:
        created: bool = False  # boolean specifying whether new obj created
        db_objs = self.find(db=db, run_id=run_id, obj_in=obj_in)
        if len(db_objs) == 0:
            db_obj = self.create(
                db=db,
                obj_in=obj_in,
                owner_id=owner_id,
                run_id=run_id,
                sample_id=sample_id,
            )
            created = True
        elif len(db_objs) == 1:
            db_obj = self.update(
                db=db, db_obj=db_objs[0], obj_in=jsonable_encoder(obj_in)
            )
        else:
            # If more than one "identical" object found, then delete all
            # objects except last one, and update last one
            for obj in db_objs[:-1]:
                self.remove(db=db, id=obj.id)
            db_obj = self.update(
                db=db, db_obj=db_objs[-1], obj_in=jsonable_encoder(obj_in)
            )
        return (db_obj, created)
