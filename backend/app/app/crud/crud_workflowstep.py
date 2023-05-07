from app.crud.base import CRUDBaseWorkflow
from app.models.workflowstep import WorkflowStep
from app.schemas.workflowstep import WorkflowStepCreate, WorkflowStepUpdate


class CRUDWorkflowStep(
    CRUDBaseWorkflow[WorkflowStep, WorkflowStepCreate, WorkflowStepUpdate]
):

    """CRUD Methods for WorkflowSteps"""


workflowstep = CRUDWorkflowStep(WorkflowStep)
