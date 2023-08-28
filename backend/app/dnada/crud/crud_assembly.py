from fastapi.encoders import jsonable_encoder
from pandas import read_json
from sqlalchemy.orm import Session

from dnada.crud.base import CRUDBaseDesign
from dnada.models.assembly import Assembly
from dnada.models.construct import Construct
from dnada.models.part import Part
from dnada.schemas.assembly import AssemblyCreate, AssemblyUpdate


class CRUDAssembly(CRUDBaseDesign[Assembly, AssemblyCreate, AssemblyUpdate]):

    """CRUD Methods for Assemblys"""

    def create(
        self,
        db: Session,
        *,
        obj_in: AssemblyCreate,
        owner_id: int,
        design_id: int,
        construct_id: int,
        part_id: int,
    ) -> Assembly:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(
            **obj_in_data,
            owner_id=owner_id,
            design_id=design_id,
            construct_id=construct_id,
            part_id=part_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def format_json(
        self, db: Session, *, raw_json: str, owner_id: int, design_id: int
    ) -> str:
        assemblys = read_json(raw_json).rename(
            columns={
                "Number": "j5_assembly_id",
                "Name": "name",
                "Assembly Method": "assembly_method",
                "Part Name": "part_name",
                "Part ID": "j5_part_id",
                "Part Order": "bin",
            }
        )
        assemblys["owner_id"] = owner_id
        assemblys["design_id"] = design_id
        assemblys["part_id"] = assemblys.apply(
            lambda row: db.query(Part)
            .filter(
                Part.j5_part_id == row.j5_part_id,
                Part.design_id == row.design_id,
            )
            .one()
            .id,
            axis=1,
        )
        assemblys["construct_id"] = assemblys.apply(
            lambda row: db.query(Construct)
            .filter(
                Construct.j5_construct_id == row.j5_assembly_id,
                Construct.design_id == row.design_id,
            )
            .one()
            .id,
            axis=1,
        )
        return assemblys.loc[
            :,
            [
                "j5_assembly_id",
                "name",
                "assembly_method",
                "bin",
                "owner_id",
                "construct_id",
                "design_id",
                "part_id",
            ],
        ].to_json()


assembly = CRUDAssembly(Assembly)
