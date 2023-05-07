#!/usr/bin/env python3

import shutil
import tempfile
import zipfile
from typing import List

from fastapi import UploadFile

from app import schemas


def process_j5_zip_upload(upload_file: UploadFile) -> schemas.J5Design:
    with tempfile.NamedTemporaryFile(delete=True, suffix=".zip") as tmp:
        shutil.copyfileobj(upload_file.file, tmp)
        zip_file = zipfile.ZipFile(tmp, mode="r")
        zip_file_name: str = upload_file.filename
        plasmid_maps: List[schemas.PlasmidMap] = []
        plasmid_designs: List[schemas.PlasmidDesign] = []
        master_j5: schemas.MasterJ5
        for subfile in zip_file.namelist():
            if subfile.endswith(".gb"):
                plasmid_design_filename = subfile.replace(".gb", ".csv")
                plasmid_maps.append(
                    schemas.PlasmidMap(
                        filename=subfile,
                        contents=zip_file.read(subfile).decode("utf8"),
                    )
                )
                plasmid_designs.append(
                    schemas.PlasmidDesign(
                        filename=plasmid_design_filename,
                        contents=zip_file.read(
                            plasmid_design_filename
                        ).decode("utf8"),
                    )
                )
            elif subfile.endswith(".eug"):
                continue
            elif subfile.endswith("combinatorial.csv"):
                csv_file: str = zip_file.read(subfile).decode("utf8")
                master_j5 = schemas.MasterJ5.parse_csv(csv_file)
            elif subfile.endswith(".csv"):
                continue
            elif subfile.endswith(".zip"):
                continue
        j5_design: schemas.J5Design = schemas.J5Design(
            zip_file_name=zip_file_name,
            master_j5=master_j5,
            plasmid_maps=plasmid_maps,
            plasmid_designs=plasmid_designs,
        )
    return j5_design
