# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.assembly import Assembly  # noqa
from app.models.associations import pcr_to_oligo_association  # noqa
from app.models.design import Design  # noqa
from app.models.digest import Digest  # noqa
from app.models.experiment import Experiment  # noqa
from app.models.instruction import Instruction  # noqa
from app.models.oligo import Oligo  # noqa
from app.models.part import Part  # noqa
from app.models.pcr import PCR  # noqa
from app.models.plate import Plate  # noqa
from app.models.rawdesign import RawDesign  # noqa
from app.models.result import AssemblyResult  # noqa
from app.models.result import PCRResult  # noqa
from app.models.result import SequencingResult  # noqa
from app.models.resultzip import ResultZip  # noqa
from app.models.run import Run  # noqa
from app.models.synth import Synth  # noqa
from app.models.template import Template  # noqa
from app.models.user import User  # noqa
from app.models.well import DigestWell  # noqa
from app.models.workflow import Workflow  # noqa
from app.models.workflowstep import WorkflowStep  # noqa
