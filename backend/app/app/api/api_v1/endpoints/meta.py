from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps

router = APIRouter()


class Query(BaseModel):
    query: str

    class Config:
        schema_extra = {
            "example": {
                "query": "db.query(models.Plate).join(models.Workflow).filter(models.Workflow.id == 3).filter(models.Plate.plate_type == 'pcr').first().wells[0]"
            }
        }


# @router.post("/query")
# def query_stuff(
#     *,
#     db: Session = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
#     query: Query,
# ) -> Any:
#     """
#     Very dangerous function not for production! :)
#     """
#     # if not crud.user.is_superuser(current_user):
#     #     raise HTTPException(
#     #         status_code=400, detail="Not enough permissions"
#     #     )
#     if not query.query.startswith("db.query("):
#         raise HTTPException(status_code=400, detail="Invalid query")
#     import pandas as pd

#     # return pd.read_sql(
#     #     eval(query.query + ".statement"), db.connection(),
#     # ).to_csv()
#     # print(query.query)
#     # print(
#     #     db.query(models.User)
#     #     .join(models.Experiment)
#     #     .join(models.Workflow)
#     #     .join(models.Instruction)
#     #     .join(models.Run)
#     #     .filter(models.User.id == current_user.id)
#     #     .all()
#     # )
#     allPCRResults = (
#         db.query(models.PCRResult)
#         .join(models.Run)
#         .join(models.Instruction)
#         .join(models.Workflow)
#         .join(models.Experiment)
#         .join(models.User)
#         .filter(models.User.id == current_user.id)
#         .all()
#     )
#     print(allPCRResults)
#     print(allPCRResults[0])
#     print(vars(allPCRResults[0]))
#     # return pd.read_sql(
#     #     db.query(models.PCRResult)
#     #     .join(models.Run)
#     #     .join(models.Instruction)
#     #     .join(models.Workflow)
#     #     .join(models.Experiment)
#     #     .join(models.User)
#     #     .filter(models.User.id == current_user.id)
#     #     .statement,
#     #     db.bind,
#     # )
#     # return pd.read_sql(
#     #     db.query(models.User)
#     #     .join(models.Experiment)
#     #     .join(models.Workflow)
#     #     .join(models.Instruction)
#     #     .join(models.Run)
#     #     .filter(models.User.id == current_user.id)
#     #     .statement,
#     #     db.connection(),
#     # )


@router.get("/query/pcr")
def query_pcr(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    workflow_id: int,  # workflow_id
) -> Any:
    """
    query = (db.query(
            models.PCRResult.id,
            models.PCRResult.polymerase,
            models.PCRResult.good,
            models.PCRResult.sample_id,
            models.PCRWell.location,
            models.PCR.length,
            models.PCR.sequence)
        .join(models.Run)
        .join(models.Instruction)
        .join(models.Workflow)
        .join(models.PCRWell)
        .join(models.PCR, models.PCR.id == models.PCRWell.content_id)
        .filter(models.Workflow.id == id)
        .all())
    """
    workflow = crud.workflow.get(db=db, id=workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not crud.user.is_superuser(current_user) and (
        workflow.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    query = pd.read_sql(
        db.query(
            models.PCRResult.id,
            models.PCRResult.polymerase,
            models.PCRResult.good,
            models.PCRResult.sample_id,
            models.PCRWell.location,
            models.PCR.length,
            models.PCR.sequence,
        )
        .join(models.Run)
        .join(models.Instruction)
        .join(models.Workflow)
        .join(models.PCRWell)
        .join(models.PCR, models.PCR.id == models.PCRWell.content_id)
        .filter(models.Workflow.id == workflow_id)
        .statement,
        db.bind,
    )
    return query.to_csv()


@router.get("/query/assembly")
def query_assembly(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    workflow_id: int,  # workflow_id
) -> Any:
    """
    db.query(
            models.Workflow.id.label("workflow_id"),
            models.Construct.name,
            models.Construct.assembly_method,
            models.AssemblyResult.id.label("assemblyresult_id"),
            models.AssemblyResult.colonies,
        )
        .join(models.AssemblyResult)
        .join(models.Run)
        .join(models.Instruction)
        .join(models.Workflow)
        .filter(models.Workflow.id == workflow_id)
        .all()
    """
    workflow = crud.workflow.get(db=db, id=workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not crud.user.is_superuser(current_user) and (
        workflow.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    query = pd.read_sql(
        db.query(
            models.Workflow.id.label("workflow_id"),
            models.Construct.name,
            models.Construct.assembly_method,
            models.AssemblyResult.id.label("assemblyresult_id"),
            models.AssemblyResult.colonies,
        )
        .join(models.AssemblyResult)
        .join(models.Run)
        .join(models.Instruction)
        .join(models.Workflow)
        .filter(models.Workflow.id == workflow_id)
        .statement,
        db.bind,
    )
    return query.to_csv()


@router.get("/query/sequencing")
def query_sequencing(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    workflow_id: int,  # workflow_id
) -> Any:
    """
    db.query(
            models.Workflow.id.label("workflow_id"),
            models.Construct.name,
            models.Construct.assembly_method,
            models.SequencingResult.id.label("sequencingresult_id"),
            models.SequencingResult.sequencing,
        )
        .join(models.SequencingResult)
        .join(models.Run)
        .join(models.Instruction)
        .join(models.Workflow)
        .filter(models.Workflow.id == workflow_id)
    """
    workflow = crud.workflow.get(db=db, id=workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not crud.user.is_superuser(current_user) and (
        workflow.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    query = pd.read_sql(
        db.query(
            models.Workflow.id.label("workflow_id"),
            models.Construct.name,
            models.Construct.assembly_method,
            models.SequencingResult.id.label("sequencingresult_id"),
            models.SequencingResult.sequencing,
        )
        .join(models.SequencingResult)
        .join(models.Run)
        .join(models.Instruction)
        .join(models.Workflow)
        .filter(models.Workflow.id == workflow_id)
        .statement,
        db.bind,
    )
    return query.to_csv()


@router.get("/query/overall")
def query_overall(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    workflow_id: int,  # workflow_id
) -> Any:
    """
    db.query(
            models.Workflow.id.label("workflow_id"),
            models.Construct.name,
            models.Construct.assembly_method,
            models.AssemblyResult.id.label("assemblyresult_id"),
            models.AssemblyResult.colonies,
            models.SequencingResult.id.label("sequencingresult_id"),
            models.SequencingResult.sequencing,
            models.Construct.genbank,
        )
        .join(
            models.AssemblyResult,
            models.AssemblyResult.sample_id == models.Construct.id,
        )
        .join(
            models.SequencingResult,
            models.SequencingResult.sample_id == models.Construct.id,
        )
        .filter(models.Workflow.id == workflow_id)
    """
    workflow = crud.workflow.get(db=db, id=workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not crud.user.is_superuser(current_user) and (
        workflow.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    query = pd.read_sql(
        db.query(
            models.Workflow.id.label("workflow_id"),
            models.Construct.name,
            models.Construct.assembly_method,
            models.AssemblyResult.id.label("assemblyresult_id"),
            models.AssemblyResult.colonies,
            models.SequencingResult.id.label("sequencingresult_id"),
            models.SequencingResult.sequencing,
            models.Construct.genbank,
        )
        .join(
            models.AssemblyResult,
            models.AssemblyResult.sample_id == models.Construct.id,
        )
        .join(
            models.SequencingResult,
            models.SequencingResult.sample_id == models.Construct.id,
        )
        .filter(models.Workflow.id == workflow_id)
        .statement,
        db.bind,
    )
    return query.to_csv()
