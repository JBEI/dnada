#!/usr/bin/env python3

from typing import List

from app import schemas
from app.api.utils.time import today


def condense_designs(designs: List[schemas.J5Design]) -> schemas.J5Design:
    master_j5: schemas.MasterJ5 = schemas.MasterJ5.condense_designs(
        [design.master_j5 for design in designs]
    )
    condensed_j5_design: schemas.J5Design = schemas.J5Design(
        zip_file_name=f"{today()}_condensed_design",
        master_j5=master_j5,
        plasmid_maps=[
            plasmid_map for design in designs for plasmid_map in design.plasmid_maps
        ],
        plasmid_designs=[
            plasmid_design
            for design in designs
            for plasmid_design in design.plasmid_designs
        ],
    )
    return condensed_j5_design
