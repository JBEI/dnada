import base64
import io
import logging
import zipfile
from typing import Any, Dict, List, Type, TypeVar

import pandas as pd
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.j5_to_echo_utils import convert3WellTo2Well
from app.crud.base import CRUDBase, CRUDBaseWell
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CRUDType = TypeVar("CRUDType", bound=CRUDBase)
WellModelType = TypeVar("WellModelType", bound=CRUDBaseWell)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NoneDetected(Exception):
    pass


def add_stuff_to_db(
    db: Session,
    owner_id: int,
    design_id: int,
    raw_json: str,
    db_model: Type[ModelType],
    crud_model: CRUDType,
    plate_mapping: Dict[str, int] = None,
) -> int:
    num_of_stuff_added: int = 0
    try:
        if raw_json == "{}":
            raise NoneDetected(f"No {db_model.__tablename__}s Found")
        if plate_mapping:
            ready_json = crud_model.format_json(
                db=db,
                raw_json=raw_json,
                owner_id=owner_id,
                design_id=design_id,
                plate_mapping=plate_mapping,
            )
        else:
            ready_json = crud_model.format_json(
                db=db,
                raw_json=raw_json,
                owner_id=owner_id,
                design_id=design_id,
            )
        num_of_stuff_added = crud_model.bulk_create(
            db=db,
            ready_json=ready_json,
        )
    except NoneDetected as none_detected:
        logger.debug(none_detected)
    return num_of_stuff_added


def gather_constructs_for_db(
    db: Session, zip_json: dict, owner_id: int, design_id: int
) -> str:
    design = crud.design.get(db=db, id=design_id)
    if not design:
        return ""
    assemblys = pd.read_json(zip_json["combinatorial"]["assemblys"])
    filenames: List[str] = []
    genbanks: List[str] = []
    for key in zip_json.keys():
        if key.endswith(".gb"):
            filenames.append(key)
            genbanks.append(zip_json[key])
    constructs = pd.DataFrame({"filename": filenames, "genbank": genbanks})
    constructs["name"] = constructs["filename"].str.strip(".gb")
    constructs["j5_construct_id"] = constructs["name"].apply(
        lambda name: assemblys.loc[
            assemblys["Name"] == name, "Number"
        ].values[0]
    )
    constructs["assembly_method"] = constructs["name"].apply(
        lambda name: assemblys.loc[
            assemblys["Name"] == name, "Assembly Method"
        ].values[0]
    )
    return constructs.to_json()


def process_design_to_db(
    db: Session, zip_json: dict, owner_id: int, design_id: int
) -> None:
    # Adding constructs from design to database
    construct_json = gather_constructs_for_db(
        db=db, zip_json=zip_json, owner_id=owner_id, design_id=design_id
    )
    add_stuff_to_db(
        db=db,
        owner_id=owner_id,
        design_id=design_id,
        raw_json=construct_json,
        db_model=models.Construct,
        crud_model=crud.construct,
    )
    # Adding parts from design to database
    add_stuff_to_db(
        db=db,
        owner_id=owner_id,
        design_id=design_id,
        raw_json=zip_json["combinatorial"]["parts"],
        db_model=models.Part,
        crud_model=crud.part,
    )
    # Adding assemblys from design to database
    add_stuff_to_db(
        db=db,
        owner_id=owner_id,
        design_id=design_id,
        raw_json=zip_json["combinatorial"]["assemblys"],
        db_model=models.Assembly,
        crud_model=crud.assembly,
    )
    # Adding synths from design to database
    add_stuff_to_db(
        db=db,
        owner_id=owner_id,
        design_id=design_id,
        raw_json=zip_json["combinatorial"]["synths"],
        db_model=models.Synth,
        crud_model=crud.synth,
    )
    # Adding PCR templates from design to database
    add_stuff_to_db(
        db=db,
        owner_id=owner_id,
        design_id=design_id,
        raw_json=zip_json["combinatorial"]["pcrs"],
        db_model=models.Template,
        crud_model=crud.template,
    )
    # Adding oligos from design to database
    add_stuff_to_db(
        db=db,
        owner_id=owner_id,
        design_id=design_id,
        raw_json=zip_json["combinatorial"]["oligos"],
        db_model=models.Oligo,
        crud_model=crud.oligo,
    )
    # Adding digests from design to database
    add_stuff_to_db(
        db=db,
        owner_id=owner_id,
        design_id=design_id,
        raw_json=zip_json["combinatorial"]["digests"],
        db_model=models.Digest,
        crud_model=crud.digest,
    )
    # Adding pcrs from design to database
    add_stuff_to_db(
        db=db,
        owner_id=owner_id,
        design_id=design_id,
        raw_json=zip_json["combinatorial"]["pcrs"],
        db_model=models.PCR,
        crud_model=crud.pcr,
    )
    return None


def create_plates(
    db: Session,
    plate_names: List[str],
    owner_id: int,
    workflow_id: int,
    size: int,
    plate_type: str,
    raw_data: str,
) -> List[models.Plate]:
    created_plates: List[models.Plate] = []
    for plate_name in plate_names:
        plate_in = schemas.PlateCreate(
            name=plate_name,
            size=size,
            plate_type=plate_type,
            raw_data=raw_data,
        )
        plate = crud.plate.create(
            db=db,
            obj_in=plate_in,
            owner_id=owner_id,
            workflow_id=workflow_id,
        )
        created_plates.append(plate)
    return created_plates


def create_wells(
    db: Session,
    owner_id: int,
    workflow_id: int,
    raw_json: str,
    db_model: Type[WellModelType],
    crud_model: CRUDType,
    plate_mapping: Dict[str, int] = None,
) -> int:
    num_of_stuff_added: int = 0
    try:
        if raw_json == "{}":
            raise NoneDetected(f"No {db_model.__tablename__}s Found")
        ready_json = crud_model.format_json(
            db=db,
            raw_json=raw_json,
            owner_id=owner_id,
            workflow_id=workflow_id,
            plate_mapping=plate_mapping,
        )
        num_of_stuff_added = crud_model.bulk_create(
            db=db,
            ready_json=ready_json,
        )
    except NoneDetected as none_detected:
        logger.debug(none_detected)
    return num_of_stuff_added


def process_workflow_to_db(
    db: Session,
    workflow_objs: Dict[str, List[dict]],
    owner_id: int,
    workflow_id: int,
) -> None:
    model_map: Dict[str, Dict[str, Any]] = {
        "synth": {"db": models.SynthWell, "crud": crud.synthwell},
        "pcr": {"db": models.PCRWell, "crud": crud.pcrwell},
        "template": {
            "db": models.TemplateWell,
            "crud": crud.templatewell,
        },
        "oligo": {"db": models.OligoWell, "crud": crud.oligowell},
        "digest": {"db": models.DigestWell, "crud": crud.digestwell},
        "part": {"db": models.PartWell, "crud": crud.partwell},
    }
    # Create each step in workflow
    for step in workflow_objs["steps"]:
        workflow_step_in = schemas.WorkflowStepCreate(
            name=step["name"],
            number=step["number"],
            title=step["title"],
            status=step["status"],
        )
        crud.workflowstep.create(
            db=db,
            obj_in=workflow_step_in,
            owner_id=owner_id,
            workflow_id=workflow_id,
        )
    # Create each plate in workflow
    for plate_csv in workflow_objs["plate_csvs"]:
        plates: list = create_plates(
            db=db,
            plate_names=plate_csv["plate_names"],
            owner_id=owner_id,
            workflow_id=workflow_id,
            size=plate_csv["size"],
            plate_type=plate_csv["plate_type"],
            raw_data=plate_csv["raw_data"],
        )
        plate_mapping: Dict[str, int] = {
            str(plate.name): plate.id for plate in plates
        }
        create_wells(
            db=db,
            owner_id=owner_id,
            workflow_id=workflow_id,
            raw_json=pd.read_csv(
                io.StringIO(plate_csv["raw_data"])
            ).to_json(),
            db_model=model_map[plate_csv["plate_type"]]["db"],
            crud_model=model_map[plate_csv["plate_type"]]["crud"],
            plate_mapping=plate_mapping,
        )
    # Create each instruction in workflow
    for instruction in workflow_objs["instructions"]:
        if instruction["category"] == "pcr_worksheet":
            instruction["data"] = update_pcr_worksheet(
                db=db,
                worksheet=instruction["data"],
                owner_id=owner_id,
                workflow_id=workflow_id,
            )
        instruction_in = schemas.InstructionCreate(
            category=instruction["category"],
            data=instruction["data"],
            trial=instruction["trial"],
        )
        crud.instruction.create(
            db=db,
            obj_in=instruction_in,
            owner_id=owner_id,
            workflow_id=workflow_id,
        )
    return None


def update_pcr_worksheet(
    db: Session, worksheet: str, owner_id: int, workflow_id: int
) -> str:
    pcr_worksheet = pd.read_csv(io.StringIO(worksheet))
    pcr_worksheet["owner_id"] = owner_id
    pcr_worksheet["workflow_id"] = workflow_id
    pcr_worksheet["design_id"] = crud.workflow.get(
        db=db, id=workflow_id
    ).design_id
    pcr_worksheet["pcr_id"] = pcr_worksheet["REACTION_NUMBER"].apply(
        lambda rxn_number: db.query(models.PCR.id)
        .join(models.Part)
        .join(models.Design)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.PCR.j5_pcr_id == rxn_number)
        .one()[0]
    )
    pcr_worksheet["template_id"] = pcr_worksheet["TEMPLATE_NAME"].apply(
        lambda name: db.query(models.Template.id)
        .join(models.Design)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.Template.name == name)
        .one()[0]
    )
    pcr_worksheet["template_plate_id"] = pcr_worksheet[
        "TEMPLATE_PLATE"
    ].apply(
        lambda name: db.query(models.Plate.id)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.Plate.plate_type == "template")
        .filter(models.Plate.name == name)
        .one()[0]
    )
    pcr_worksheet["template_well_id"] = pcr_worksheet.apply(
        lambda row: db.query(models.TemplateWell.id)
        .join(models.Plate)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.TemplateWell.plate_id == row["template_plate_id"])
        .filter(
            models.TemplateWell.location
            == convert3WellTo2Well(row["TEMPLATE_WELL"])
        )
        .one()[0],
        axis=1,
    )
    pcr_worksheet["oligo1_id"] = pcr_worksheet["PRIMER1_NAME"].apply(
        lambda name: db.query(models.Oligo.id)
        .join(models.Design)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.Oligo.name == name)
        .one()[0]
    )
    pcr_worksheet["oligo2_id"] = pcr_worksheet["PRIMER2_NAME"].apply(
        lambda name: db.query(models.Oligo.id)
        .join(models.Design)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.Oligo.name == name)
        .one()[0]
    )
    pcr_worksheet["oligo1_plate_id"] = pcr_worksheet[
        "PRIMER1_PLATE"
    ].apply(
        lambda name: db.query(models.Plate.id)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.Plate.plate_type == "oligo")
        .filter(models.Plate.name == name)
        .one()[0]
    )
    pcr_worksheet["oligo2_plate_id"] = pcr_worksheet[
        "PRIMER2_PLATE"
    ].apply(
        lambda name: db.query(models.Plate.id)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.Plate.plate_type == "oligo")
        .filter(models.Plate.name == name)
        .one()[0]
    )
    pcr_worksheet["oligo1_well_id"] = pcr_worksheet.apply(
        lambda row: db.query(models.OligoWell.id)
        .join(models.Plate)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.OligoWell.plate_id == row["oligo1_plate_id"])
        .filter(
            models.OligoWell.location
            == convert3WellTo2Well(row["PRIMER1_WELL"])
        )
        .one()[0],
        axis=1,
    )
    pcr_worksheet["oligo2_well_id"] = pcr_worksheet.apply(
        lambda row: db.query(models.OligoWell.id)
        .join(models.Plate)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.OligoWell.plate_id == row["oligo2_plate_id"])
        .filter(
            models.OligoWell.location
            == convert3WellTo2Well(row["PRIMER2_WELL"])
        )
        .one()[0],
        axis=1,
    )
    pcr_worksheet["pcr_plate_id"] = pcr_worksheet["OUTPUT_PLATE"].apply(
        lambda name: db.query(models.Plate.id)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.Plate.plate_type == "pcr")
        .filter(models.Plate.name == name)
        .one()[0]
    )
    pcr_worksheet["pcr_well_id"] = pcr_worksheet.apply(
        lambda row: db.query(models.PCRWell.id)
        .join(models.Plate)
        .join(models.Workflow)
        .filter(models.Workflow.owner_id == owner_id)
        .filter(models.Workflow.id == workflow_id)
        .filter(models.PCRWell.plate_id == row["pcr_plate_id"])
        .filter(models.PCRWell.location == row["OUTPUT_WELL"])
        .one()[0],
        axis=1,
    )
    pcr_worksheet["sample_id"] = pcr_worksheet["pcr_well_id"]
    return pcr_worksheet.to_csv()


def add_assembly_instructions_to_db(
    db: Session, owner_id: int, workflow_id: int, assembly_zip: io.BytesIO
) -> models.Instruction:
    crud.instruction.find_and_bulk_remove(
        db=db,
        workflow_id=workflow_id,
        obj_in={"category": "assembly_instructions.zip", "trial": 1},
    )
    crud.instruction.find_and_bulk_remove(
        db=db,
        workflow_id=workflow_id,
        obj_in={"category": "possible_constructs.csv", "trial": 1},
    )
    crud.instruction.find_and_bulk_remove(
        db=db,
        workflow_id=workflow_id,
        obj_in={
            "category": "possible_constructs_worksheet.csv",
            "trial": 1,
        },
    )
    crud.instruction.find_and_bulk_remove(
        db=db,
        workflow_id=workflow_id,
        obj_in={"category": "possible_assembly_worksheet.csv", "trial": 1},
    )
    crud.instruction.find_and_bulk_remove(
        db=db,
        workflow_id=workflow_id,
        obj_in={
            "category": "possible_assembly_echo_instructions.csv",
            "trial": 1,
        },
    )
    crud.instruction.find_and_bulk_remove(
        db=db,
        workflow_id=workflow_id,
        obj_in={
            "category": "possible_plating_instructions_biomek.csv",
            "trial": 1,
        },
    )

    # Create Zip File Instruction
    assembly_zip.seek(0)
    zip_file_instruction_in = schemas.InstructionCreate(
        category="assembly_instructions.zip",
        trial=1,
        data=base64.b64encode(assembly_zip.read()).decode("utf-8"),
    )
    zip_file_instruction: models.Instruction = crud.instruction.create(
        db=db,
        obj_in=zip_file_instruction_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )

    assembly_zip.seek(0)
    with zipfile.ZipFile(assembly_zip, mode="r") as F:
        possible_constructs: str = F.read(
            "possible_assembly/possible_constructs.csv"
        ).decode("utf-8")
        possible_constructs_worksheet: str = F.read(
            "possible_assembly/possible_constructs_worksheet.csv"
        ).decode("utf-8")
        possible_assembly_worksheet: str = F.read(
            "possible_assembly/possible_assembly_worksheet.csv"
        ).decode("utf-8")
        possible_assembly_echo_instructions: str = F.read(
            "possible_assembly/possible_assembly_echo_instructions.csv"
        ).decode("utf-8")
        possible_plating_instructions_biomek: str = F.read(
            "possible_assembly/possible_plating_instructions_biomek.csv"
        ).decode("utf-8")

    # Create possible_constructs.csv
    possible_constructs_in = schemas.InstructionCreate(
        category="possible_constructs.csv",
        trial=1,
        data=possible_constructs,
    )
    crud.instruction.create(
        db=db,
        obj_in=possible_constructs_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    # Create possible_constructs_worksheet.csv
    possible_constructs_worksheet_in = schemas.InstructionCreate(
        category="possible_constructs_worksheet.csv",
        trial=1,
        data=possible_constructs_worksheet,
    )
    crud.instruction.create(
        db=db,
        obj_in=possible_constructs_worksheet_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    # Create possible_assembly_worksheet.csv
    possible_assembly_worksheet_in = schemas.InstructionCreate(
        category="possible_assembly_worksheet.csv",
        trial=1,
        data=possible_assembly_worksheet,
    )
    crud.instruction.create(
        db=db,
        obj_in=possible_assembly_worksheet_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    # Create possible_assembly_echo_instructions.csv
    possible_assembly_echo_instructions_in = schemas.InstructionCreate(
        category="possible_assembly_echo_instructions.csv",
        trial=1,
        data=possible_assembly_echo_instructions,
    )
    crud.instruction.create(
        db=db,
        obj_in=possible_assembly_echo_instructions_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    # Create possible_plating_instructions_biomek.csv
    possible_plating_instructions_biomek_in = schemas.InstructionCreate(
        category="possible_plating_instructions_biomek.csv",
        trial=1,
        data=possible_plating_instructions_biomek,
    )
    crud.instruction.create(
        db=db,
        obj_in=possible_plating_instructions_biomek_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    return zip_file_instruction


def add_plating_instructions_to_db(
    db: Session, owner_id: int, workflow_id: int, plating_instructions: str
) -> models.Instruction:
    crud.instruction.find_and_bulk_remove(
        db=db,
        workflow_id=workflow_id,
        obj_in={"category": "plating_instructions.csv", "trial": 1},
    )
    plating_instructions_db: models.Instruction = crud.instruction.create(
        db=db,
        obj_in=schemas.InstructionCreate(
            category="plating_instructions.csv",
            trial=1,
            data=plating_instructions,
        ),
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    return plating_instructions_db


def add_consolidate_pcr_instructions_to_db(
    db: Session, owner_id: int, workflow_id: int, instruct_zip: io.BytesIO
) -> models.Instruction:
    """
    Takes in consolidate pcr zip file and returns
    instruction that contains zip file
    """
    crud.instruction.find_and_bulk_remove(
        db=db,
        workflow_id=workflow_id,
        obj_in={"category": "consolidate_pcr_workflow.zip", "trial": 1},
    )
    crud.instruction.find_and_bulk_remove(
        db=db,
        workflow_id=workflow_id,
        obj_in={"category": "consolidate_pcr_biomek.csv", "trial": 1},
    )
    crud.instruction.find_and_bulk_remove(
        db=db,
        workflow_id=workflow_id,
        obj_in={"category": "consolidated_pcr_worksheet.csv", "trial": 1},
    )
    crud.instruction.find_and_bulk_remove(
        db=db,
        workflow_id=workflow_id,
        obj_in={"category": "pcr_workbook.xlsx", "trial": 1},
    )

    # Create Zip File Instruction
    instruct_zip.seek(0)
    zip_file_instruction_in = schemas.InstructionCreate(
        category="consolidate_pcr_workflow.zip",
        trial=1,
        data=base64.b64encode(instruct_zip.read()).decode("utf-8"),
    )
    zip_file_instruction: models.Instruction = crud.instruction.create(
        db=db,
        obj_in=zip_file_instruction_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )

    instruct_zip.seek(0)
    with zipfile.ZipFile(instruct_zip, mode="r") as F:
        biomek_instructions: str = F.read(
            "biomek_instructions.csv"
        ).decode("utf-8")
        consolidated_pcr_worksheet: str = F.read(
            "consolidated_pcr_worksheet.csv"
        ).decode("utf-8")
        consolidate_pcr_workbook: str = base64.b64encode(
            F.read("consolidate_pcr_workbook.xlsx")
        ).decode("utf-8")

    # Create biomek_instructions.csv
    biomek_instruction_in = schemas.InstructionCreate(
        category="consolidate_pcr_biomek.csv",
        trial=1,
        data=biomek_instructions,
    )
    crud.instruction.create(
        db=db,
        obj_in=biomek_instruction_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    # Create consolidated_pcr_worksheet.csv
    pcr_worksheet_instruction_in = schemas.InstructionCreate(
        category="consolidated_pcr_worksheet.csv",
        trial=1,
        data=consolidated_pcr_worksheet,
    )
    crud.instruction.create(
        db=db,
        obj_in=pcr_worksheet_instruction_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    # Create consolidate_pcr_workbook.xlsx
    pcr_workbook_instruction_in = schemas.InstructionCreate(
        category="pcr_workbook.xlsx",
        trial=1,
        data=consolidate_pcr_workbook,
    )
    crud.instruction.create(
        db=db,
        obj_in=pcr_workbook_instruction_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    return zip_file_instruction


def add_pcr_redo_instructions_to_db(
    db: Session,
    owner_id: int,
    workflow_id: int,
    pcr_redo_instructions: Dict[str, str],
    trial: int,
    settings: dict,
) -> Any:
    redo_pcr_df: pd.DataFrame = pd.read_csv(
        io.StringIO(pcr_redo_instructions["worksheet"])
    )
    redo_worksheet_instruction_in = schemas.InstructionCreate(
        category="pcr_worksheet",
        trial=trial,
        data=pcr_redo_instructions["worksheet"],
    )
    redo_pcr_echo_instruction_in = schemas.InstructionCreate(
        category="pcr_echo_instructions.csv",
        trial=trial,
        data=pcr_redo_instructions["echo_instructions"],
    )
    crud.instruction.create(
        db=db,
        obj_in=redo_worksheet_instruction_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    crud.instruction.create(
        db=db,
        obj_in=redo_pcr_echo_instruction_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    plates: list = create_plates(
        db=db,
        plate_names=list(
            redo_pcr_df[settings["pcrRedoPlateColumn"]].unique()
        ),
        owner_id=owner_id,
        workflow_id=workflow_id,
        size=96,
        plate_type="pcr",
        raw_data=pcr_redo_instructions["worksheet"],
    )
    plate_mapping: Dict[str, int] = {
        str(plate.name): plate.id for plate in plates
    }
    create_wells(
        db=db,
        owner_id=owner_id,
        workflow_id=workflow_id,
        raw_json=redo_pcr_df.to_json(),
        db_model=models.PCRWell,
        crud_model=crud.pcrwell,
        plate_mapping=plate_mapping,
    )
    return None
