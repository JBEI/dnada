from dnada.crud.base import CRUDBaseWorkflow
from dnada.models.workflowstep import WorkflowStep
from dnada.schemas.workflowstep import WorkflowStepCreate, WorkflowStepUpdate


class CRUDWorkflowStep(
    CRUDBaseWorkflow[WorkflowStep, WorkflowStepCreate, WorkflowStepUpdate]
):

    """CRUD Methods for WorkflowSteps"""


workflowstep = CRUDWorkflowStep(WorkflowStep)
