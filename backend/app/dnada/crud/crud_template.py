from typing import Optional

from fastapi.encoders import jsonable_encoder
from pandas import read_json
from sqlalchemy.orm import Session

from dnada import models
from dnada.crud.base import CRUDBaseDesign
from dnada.models.template import Template
from dnada.schemas.template import TemplateCreate, TemplateUpdate


class CRUDTemplate(CRUDBaseDesign[Template, TemplateCreate, TemplateUpdate]):

    """CRUD Methods for Templates"""

    def create(
        self,
        db: Session,
        *,
        obj_in: TemplateCreate,
        owner_id: int,
        design_id: int,
        synth_id: Optional[int] = None,
    ) -> Template:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data,
            owner_id=owner_id,
            design_id=design_id,
            synth_id=synth_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def format_json(
        self,
        db: Session,
        *,
        raw_json: str,
        owner_id: int,
        design_id: int,
    ) -> str:
        templates = read_json(raw_json).rename(
            columns={
                "ID Number": "j5_pcr_id",
                "Primary Template": "name",
                "ID Number.1": "oligo_id_F",
                "Name": "oligo_name_F",
                "ID Number.2": "oligo_id_R",
                "Name.1": "oligo_name_R",
                "Note": "note",
                "Mean Oligo Tm": "mean_oligo_temp",
                "Delta Oligo Tm": "delta_oligo_temp",
                "Mean Oligo Tm (3' only)": "mean_oligo_temp_3p",
                "Delta Oligo Tm (3' only)": "delta_oligo_temp_3p",
                "Length": "length",
                "Sequence": "sequence",
            }
        )
        templates = templates.drop_duplicates("name", keep="first")
        templates["owner_id"] = owner_id
        templates["design_id"] = design_id
        templates["synth_id"] = templates.apply(
            lambda row: db.query(models.Synth)
            .filter(
                models.Synth.owner_id == row["owner_id"],
                models.Synth.design_id == row["design_id"],
                models.Synth.name == row["name"],
            )
            .first()
            .id
            if row["note"] == "Direct Synthesis"
            else None,
            axis=1,
        )
        templates["j5_template_id"] = range(templates.sort_values("name").shape[0])
        return templates.loc[
            :,
            [
                "j5_template_id",
                "name",
                "owner_id",
                "design_id",
                "synth_id",
            ],
        ].to_json()


template = CRUDTemplate(Template)
