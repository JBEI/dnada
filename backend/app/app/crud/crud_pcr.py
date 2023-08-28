from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from pandas import Series, read_json
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app import models
from app.crud.base import CRUDBasePart
from app.models.design import Design
from app.models.experiment import Experiment
from app.models.oligo import Oligo
from app.models.part import Part
from app.models.pcr import PCR
from app.models.template import Template
from app.schemas.pcr import PCRCreate, PCRUpdate


class CRUDPCR(CRUDBasePart[PCR, PCRCreate, PCRUpdate]):

    """CRUD Methods for PCRs"""

    def create(
        self,
        db: Session,
        *,
        obj_in: PCRCreate,
        owner_id: int,
        part_id: int,
        template_id: int,
        forward_oligo_id: int,
        reverse_oligo_id: int,
    ) -> PCR:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data,
            owner_id=owner_id,
            part_id=part_id,
            template_id=template_id,
            forward_oligo_id=forward_oligo_id,
            reverse_oligo_id=reverse_oligo_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
        experiment_id: Optional[int] = None,
        design_id: Optional[int] = None,
        part_id: Optional[int] = None,
        template_id: Optional[int] = None,
    ) -> List[PCR]:
        baseQuery = db.query(self.model)
        if owner_id is not None:
            baseQuery = baseQuery.filter(PCR.owner_id == owner_id)
        if experiment_id is not None:
            baseQuery = (
                baseQuery.join(Part)
                .join(Design)
                .join(Experiment)
                .filter(Experiment.id == experiment_id)
            )
        if design_id is not None:
            baseQuery = baseQuery.join(Part).join(Design).filter(Design.id == design_id)
        if part_id is not None:
            baseQuery = baseQuery.filter(PCR.part_id == part_id)
        if template_id is not None:
            baseQuery = baseQuery.filter(PCR.template_id == template_id)
        return baseQuery.offset(skip).limit(limit).all()

    def bulk_create(self, db: Session, *, ready_json: str) -> int:
        all_objs_in_data = read_json(ready_json)
        objs_in_data = all_objs_in_data.loc[
            :,
            [
                "j5_pcr_id",
                "note",
                "mean_oligo_temp",
                "delta_oligo_temp",
                "mean_oligo_temp_3p",
                "delta_oligo_temp_3p",
                "length",
                "sequence",
                "owner_id",
                "part_id",
                "template_id",
                "forward_oligo_id",
                "reverse_oligo_id",
            ],
        ]
        num_of_objs_created = self._add_df_to_db(db=db, df=objs_in_data)
        ## Add oligo associations
        # all_objs_in_data.apply(
        #    lambda row: self._add_pcr_oligos_association(
        #        db=db, pcr_row=row
        #    ),
        #    axis=1,
        # )
        db.commit()
        return num_of_objs_created

    def _add_pcr_oligos_association(self, db: Session, pcr_row: Series):
        pcr_in_db = (
            db.query(PCR)
            .join(Part)
            .join(Design)
            .filter(
                PCR.owner_id == pcr_row.owner_id,
                Design.id == pcr_row.design_id,
                PCR.j5_pcr_id == pcr_row.j5_pcr_id,
            )
            .one()
        )
        forward_oligo_in_db = (
            db.query(Oligo)
            .filter(
                Oligo.owner_id == pcr_row.owner_id,
                Oligo.design_id == pcr_row.design_id,
                Oligo.j5_oligo_id == pcr_row.oligo_id_F,
            )
            .one()
        )
        reverse_oligo_in_db = (
            db.query(Oligo)
            .filter(
                Oligo.owner_id == pcr_row.owner_id,
                Oligo.design_id == pcr_row.design_id,
                Oligo.j5_oligo_id == pcr_row.oligo_id_R,
            )
            .one()
        )
        pcr_in_db.oligos = [forward_oligo_in_db, reverse_oligo_in_db]
        return None

    def format_json(
        self,
        db: Session,
        *,
        raw_json: str,
        owner_id: int,
        design_id: int,
    ) -> str:
        pcrs = read_json(raw_json).rename(
            columns={
                "ID Number": "j5_pcr_id",
                "Primary Template": "template",
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
        pcrs["owner_id"] = owner_id
        pcrs["design_id"] = design_id
        pcrs["part_id"] = pcrs.apply(
            lambda row: db.query(Part)
            .filter(
                and_(
                    Part.owner_id == row["owner_id"],
                    Part.design_id == row["design_id"],
                    Part.part_type.in_(["Direct Synthesis/PCR", "SOE", "PCR"]),
                    Part.type_id == row["j5_pcr_id"],
                )
            )
            .one()
            .id,
            axis=1,
        )
        pcrs["template_id"] = pcrs.apply(
            lambda row: db.query(Template)
            .filter(
                Template.owner_id == row["owner_id"],
                Template.design_id == row["design_id"],
                Template.name == row["template"],
            )
            .first()
            .id,
            axis=1,
        )
        pcrs["forward_oligo_id"] = pcrs.apply(
            lambda row: db.query(models.Oligo)
            .filter(
                models.Oligo.owner_id == row["owner_id"],
                models.Oligo.design_id == row["design_id"],
                models.Oligo.j5_oligo_id == row["oligo_id_F"],
            )
            .one()
            .id,
            axis=1,
        )
        pcrs["reverse_oligo_id"] = pcrs.apply(
            lambda row: db.query(models.Oligo)
            .filter(
                models.Oligo.owner_id == row["owner_id"],
                models.Oligo.design_id == row["design_id"],
                models.Oligo.j5_oligo_id == row["oligo_id_R"],
            )
            .one()
            .id,
            axis=1,
        )
        return pcrs.to_json()


pcr = CRUDPCR(PCR)
