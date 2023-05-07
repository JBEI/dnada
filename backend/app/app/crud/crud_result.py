from app.crud.base import CRUDBaseResult
from app.db.base import AssemblyResult, PCRResult, SequencingResult
from app.schemas import (AssemblyResultCreate, AssemblyResultUpdate,
                         PCRResultCreate, PCRResultUpdate,
                         SequencingResultCreate, SequencingResultUpdate)


class CRUDPCRResult(
    CRUDBaseResult[PCRResult, PCRResultCreate, PCRResultUpdate]
):

    """CRUD Methods for PCR Results"""

    # def format_json(
    #    self,
    #    db: Session,
    #    *,
    #    raw_json: str,
    #    owner_id: int,
    #    design_id: int,
    #    run_mapping: Dict[str, int]
    # ) -> str:
    #    pcrs_df = read_json(raw_json)
    #    pcrs = (
    #        db.query(PCR.id)
    #        .join(Part)
    #        .join(Design)
    #        .filter(Design.id == design_id)
    #    )
    #    pcrs_df["content_id"] = pcrs_df["REACTION_NUMBER"].apply(
    #        lambda pcr_id: pcrs.filter(PCR.j5_pcr_id == pcr_id).one()[0]
    #    )
    #    pcrs_df["owner_id"] = owner_id
    #    pcrs_df["design_id"] = design_id
    #    pcrs_df["run_id"] = pcrs_df["OUTPUT_PLATE"].apply(
    #        lambda run_name: run_mapping[run_name]
    #    )
    #    pcrs_df["result_type"] = "pcr"
    #    pcrs_df["volume"] = 50
    #    pcrs_df = pcrs_df.rename(columns={"OUTPUT_WELL": "location"})
    #    return pcrs_df.loc[
    #        :,
    #        [
    #            "location",
    #            "volume",
    #            "result_type",
    #            "content_id",
    #            "owner_id",
    #            "design_id",
    #            "run_id",
    #        ],
    #    ].to


class CRUDAssemblyResult(
    CRUDBaseResult[
        AssemblyResult, AssemblyResultCreate, AssemblyResultUpdate
    ]
):

    """CRUD Methods for Assembly Results"""


class CRUDSequencingResult(
    CRUDBaseResult[
        SequencingResult, SequencingResultCreate, SequencingResultUpdate
    ]
):

    """CRUD Methods for Sequencing Results"""


pcrresult = CRUDPCRResult(PCRResult)
assemblyresult = CRUDAssemblyResult(AssemblyResult)
sequencingresult = CRUDSequencingResult(SequencingResult)
