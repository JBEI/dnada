from .crud_assembly import assembly
from .crud_banner import banner
from .crud_construct import construct
from .crud_design import design
from .crud_digest import digest
from .crud_experiment import experiment
from .crud_instruction import instruction
from .crud_oligo import oligo
from .crud_part import part
from .crud_pcr import pcr
from .crud_plate import plate
from .crud_rawdesign import rawdesign
from .crud_result import assemblyresult, pcrresult, sequencingresult
from .crud_resultzip import resultzip
from .crud_run import run
from .crud_synth import synth
from .crud_template import template
from .crud_user import user
from .crud_well import (digestwell, oligoorder96well, oligowell, partwell,
                        pcrwell, synthwell, templatewell)
from .crud_workflow import workflow
from .crud_workflowstep import workflowstep

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
