from app.crud.base import CRUDBaseWorkflow
from app.models.instruction import Instruction
from app.schemas.instruction import InstructionCreate, InstructionUpdate


class CRUDInstruction(
    CRUDBaseWorkflow[Instruction, InstructionCreate, InstructionUpdate]
):

    """CRUD Methods for Instructions"""


instruction = CRUDInstruction(Instruction)
