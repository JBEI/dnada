from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBaseDesign
from app.models.workflow import Workflow
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate


class CRUDWorkflow(CRUDBaseDesign[Workflow, WorkflowCreate, WorkflowUpdate]):

    """CRUD Methods for Workflows"""

    def create(
        self,
        db: Session,
        *,
        obj_in: WorkflowCreate,
        owner_id: int,
        experiment_id: int,
        design_id: int,
        resultzip_id: int
    ) -> Workflow:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data,
            owner_id=owner_id,
            experiment_id=experiment_id,
            design_id=design_id,
            resultzip_id=resultzip_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


workflow = CRUDWorkflow(Workflow)
