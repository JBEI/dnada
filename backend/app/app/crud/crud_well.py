from typing import Dict

from pandas import read_json
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud.base import CRUDBaseWell
from app.models.well import (
    DigestWell,
    OligoOrder96Well,
    OligoWell,
    PartWell,
    PCRWell,
    SynthWell,
    TemplateWell,
)


class CRUDOligoWell(
    CRUDBaseWell[models.OligoWell, schemas.WellCreate, schemas.WellUpdate]
):

    """CRUD Methods for Oligo Wells"""

    def format_json(
        self,
        db: Session,
        *,
        raw_json: str,
        owner_id: int,
        workflow_id: int,
        plate_mapping: Dict[str, int]
    ) -> str:
        oligos_df = read_json(raw_json).rename(
            columns={
                "PLATE ID": "plate_name",
                "PLATE WELL": "location",
                "LIQUID TYPE": "oligo_name",
                "VOLUME (uL)": "volume",
            }
        )
        oligos_df["well_type"] = "oligo"
        oligos = (
            db.query(models.Oligo.id)
            .join(models.Design)
            .join(models.Workflow)
            .filter(models.Workflow.id == workflow_id)
        )
        oligos_df["content_id"] = oligos_df["oligo_name"].apply(
            lambda oligo_name: oligos.filter(models.Oligo.name == oligo_name).one()[0]
        )
        oligos_df["owner_id"] = owner_id
        oligos_df["plate_id"] = oligos_df["plate_name"].apply(
            lambda plate_name: plate_mapping[plate_name]
        )
        return oligos_df.loc[
            :,
            [
                "location",
                "volume",
                "well_type",
                "content_id",
                "owner_id",
                "plate_id",
            ],
        ].to_json()


class CRUDOligoOrder96Well(
    CRUDBaseWell[models.OligoOrder96Well, schemas.WellCreate, schemas.WellUpdate]
):

    """CRUD Methods for Oligo Order 96 Wells"""

    def format_json(
        self,
        db: Session,
        *,
        raw_json: str,
        owner_id: int,
        workflow_id: int,
        plate_mapping: Dict[str, int]
    ) -> str:
        pass


class CRUDDigestWell(CRUDBaseWell[DigestWell, schemas.WellCreate, schemas.WellUpdate]):

    """CRUD Methods for Digest Wells"""

    def format_json(
        self,
        db: Session,
        *,
        raw_json: str,
        owner_id: int,
        workflow_id: int,
        plate_mapping: Dict[str, int]
    ) -> str:
        digests_df = read_json(raw_json)
        digests = (
            db.query(models.Digest.id)
            .join(models.Part)
            .join(models.Design)
            .join(models.Workflow)
            .filter(models.Workflow.id == workflow_id)
        )
        digests_df["content_id"] = digests_df["REACTION_NUMBER"].apply(
            lambda digest_id: digests.filter(
                models.Digest.j5_digest_id == digest_id
            ).one()[0]
        )
        digests_df["owner_id"] = owner_id
        digests_df["plate_id"] = digests_df["DIGEST_SOURCE_PLATE"].apply(
            lambda plate_name: plate_mapping[plate_name]
        )
        digests_df["well_type"] = "digest"
        digests_df["volume"] = 50
        digests_df = digests_df.rename(columns={"DIGEST_SOURCE_WELL": "location"})
        return digests_df.loc[
            :,
            [
                "location",
                "volume",
                "well_type",
                "content_id",
                "owner_id",
                "plate_id",
            ],
        ].to_json()


class CRUDSynthWell(CRUDBaseWell[SynthWell, schemas.WellCreate, schemas.WellUpdate]):

    """CRUD Methods for Synth Wells"""

    def format_json(
        self,
        db: Session,
        *,
        raw_json: str,
        owner_id: int,
        workflow_id: int,
        plate_mapping: Dict[str, int]
    ) -> str:
        synths_df = read_json(raw_json)
        synths = (
            db.query(models.Synth.id)
            .join(models.Design)
            .join(models.Workflow)
            .filter(models.Workflow.id == workflow_id)
        )
        synths_df["content_id"] = synths_df["LIQUID TYPE"].apply(
            lambda synth_name: synths.filter(models.Synth.name == synth_name).one()[0]
        )
        synths_df["owner_id"] = owner_id
        synths_df["plate_id"] = synths_df["PLATE ID"].apply(
            lambda plate_name: plate_mapping[plate_name]
        )
        synths_df["well_type"] = "synth"
        synths_df = synths_df.rename(
            columns={"VOLUME (uL)": "volume", "PLATE WELL": "location"}
        )
        return synths_df.loc[
            :,
            [
                "location",
                "volume",
                "well_type",
                "content_id",
                "owner_id",
                "plate_id",
            ],
        ].to_json()


class CRUDPCRWell(CRUDBaseWell[PCRWell, schemas.WellCreate, schemas.WellUpdate]):

    """CRUD Methods for PCR Wells"""

    def format_json(
        self,
        db: Session,
        *,
        raw_json: str,
        owner_id: int,
        workflow_id: int,
        plate_mapping: Dict[str, int]
    ) -> str:
        pcrs_df = read_json(raw_json)
        pcrs = (
            db.query(models.PCR.id)
            .join(models.Part)
            .join(models.Design)
            .join(models.Workflow)
            .filter(models.Workflow.id == workflow_id)
        )
        pcrs_df["content_id"] = pcrs_df["REACTION_NUMBER"].apply(
            lambda pcr_id: pcrs.filter(models.PCR.j5_pcr_id == pcr_id).one()[0]
        )
        pcrs_df["owner_id"] = owner_id
        redo: bool = False
        try:
            pcrs_df["plate_id"] = pcrs_df["OUTPUT_PLATE"].apply(
                lambda plate_name: plate_mapping[plate_name]
            )
        except KeyError:
            redo = True
            pcrs_df["plate_id"] = pcrs_df["REDO_PLATE"].apply(
                lambda plate_name: plate_mapping[plate_name]
            )
        pcrs_df["well_type"] = "pcr"
        pcrs_df["volume"] = 50
        if not redo:
            pcrs_df = pcrs_df.rename(columns={"OUTPUT_WELL": "location"})
        else:
            pcrs_df = pcrs_df.rename(columns={"REDO_WELL": "location"})
        return pcrs_df.loc[
            :,
            [
                "location",
                "volume",
                "well_type",
                "content_id",
                "owner_id",
                "plate_id",
            ],
        ].to_json()


class CRUDTemplateWell(
    CRUDBaseWell[TemplateWell, schemas.WellCreate, schemas.WellUpdate]
):

    """CRUD Methods for Template Wells"""

    def format_json(
        self,
        db: Session,
        *,
        raw_json: str,
        owner_id: int,
        workflow_id: int,
        plate_mapping: Dict[str, int]
    ) -> str:
        templates_df = read_json(raw_json)
        templates = (
            db.query(models.Template.id)
            .join(models.Design)
            .join(models.Workflow)
            .filter(models.Workflow.id == workflow_id)
        )
        templates_df["content_id"] = templates_df["LIQUID TYPE"].apply(
            lambda template_name: templates.filter(
                models.Template.name == template_name
            ).one()[0]
        )
        templates_df["owner_id"] = owner_id
        templates_df["plate_id"] = templates_df["PLATE ID"].apply(
            lambda plate_name: plate_mapping[plate_name]
        )
        templates_df["well_type"] = "template"
        templates_df = templates_df.rename(
            columns={"VOLUME (uL)": "volume", "PLATE WELL": "location"}
        )
        return templates_df.loc[
            :,
            [
                "location",
                "volume",
                "well_type",
                "content_id",
                "owner_id",
                "plate_id",
            ],
        ].to_json()


class CRUDPartWell(CRUDBaseWell[PartWell, schemas.WellCreate, schemas.WellUpdate]):

    """CRUD Methods for Part Wells"""

    def format_json(
        self,
        db: Session,
        *,
        raw_json: str,
        owner_id: int,
        workflow_id: int,
        plate_mapping: Dict[str, int]
    ) -> str:
        parts_df = read_json(raw_json)
        parts = (
            db.query(models.Part.id)
            .join(models.Design)
            .join(models.Workflow)
            .filter(models.Workflow.id == workflow_id)
        )
        parts_df["content_id"] = parts_df["PART_ID"].apply(
            lambda part_id: parts.filter(models.Part.j5_part_id == part_id).one()[0]
        )
        parts_df["owner_id"] = owner_id
        parts_df["plate_id"] = parts_df["PART_PLATE"].apply(
            lambda plate_name: plate_mapping[plate_name]
        )
        parts_df["well_type"] = "part"
        parts_df["volume"] = 50
        parts_df = parts_df.rename(columns={"PART_WELL": "location"})
        return parts_df.loc[
            :,
            [
                "location",
                "volume",
                "well_type",
                "content_id",
                "owner_id",
                "plate_id",
            ],
        ].to_json()


oligowell = CRUDOligoWell(OligoWell)
oligoorder96well = CRUDOligoOrder96Well(OligoOrder96Well)
digestwell = CRUDDigestWell(DigestWell)
synthwell = CRUDSynthWell(SynthWell)
pcrwell = CRUDPCRWell(PCRWell)
templatewell = CRUDTemplateWell(TemplateWell)
partwell = CRUDPartWell(PartWell)
