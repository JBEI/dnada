from dnada.crud.base import CRUDBaseWorkflow
from dnada.models.instruction import Instruction
from dnada.schemas.instruction import InstructionCreate, InstructionUpdate


class CRUDInstruction(
    CRUDBaseWorkflow[Instruction, InstructionCreate, InstructionUpdate]
):

    """CRUD Methods for Instructions"""


instruction = CRUDInstruction(Instruction)
