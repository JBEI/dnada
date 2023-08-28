import io
import os
from datetime import datetime
import pandas as pd
import openpyxl

from app.core.j5_to_echo_utils import stamp

NGS_TEMPLATE_FILE: str = os.path.join(
    os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))),
    "ngs_form_empty_template_v2.xlsx",
)


def setup_ngs_worksheets(
    glycerol_stock_file: io.StringIO,
    registry_file: io.StringIO,
    username: str,
) -> tuple[pd.DataFrame, dict[str, io.BytesIO]]:
    glycerol: pd.DataFrame = pd.read_csv(glycerol_stock_file)
    registry: pd.DataFrame = (
        pd.read_csv(registry_file)
        .rename(
            columns={
                "name": "Name",
                "Part_ID": "Part ID",
                "part id": "Part ID",
                "part_id": "Part ID",
            }
        )
        .loc[:, ["Name", "Part ID"]]
    )
    ngs_worksheet: pd.DataFrame = glycerol.merge(
        right=registry,
        how="left",
        left_on="name",
        right_on="Name",
    )
    ngs_worksheet["Sample_Name"] = (
        ngs_worksheet["GLYCEROL_PLATE"] + "-" + ngs_worksheet["GLYCEROL_WELL"]
    )
    ngs_worksheet["NGS_PLATE"] = ngs_worksheet["GLYCEROL_PLATE"].apply(
        lambda plate: "{username} {plate_number} {date}".format(
            username=username,
            plate_number=((int(plate.split("_")[-1]) - 1) // 4) + 1,
            date=datetime.today().strftime("%Y%m%d")[2:],
        )
    )
    ngs_worksheet["NGS_WELL"] = ngs_worksheet.apply(
        lambda row: stamp(
            row["GLYCEROL_WELL"],
            (int(row["GLYCEROL_PLATE"].split("_")[-1]) - 1) % 4,
        ),
        axis=1,
    )

    submission_excels: dict[str, io.BytesIO] = {}
    submission_excel: io.BytesIO
    for plate in ngs_worksheet["NGS_PLATE"].unique():
        submission_excel = io.BytesIO()
        workbook = openpyxl.load_workbook(filename=NGS_TEMPLATE_FILE)
        worksheet = workbook.active
        worksheet["AI33"] = "Rows, Quads"
        for i, value in enumerate(
            ngs_worksheet.loc[ngs_worksheet["NGS_PLATE"] == plate, "Sample_Name"].values
        ):
            worksheet[f"AK{34 + i}"] = value
            worksheet[f"AM{34 + i}"] = "Plasmid__purified"
        for i, value in enumerate(
            ngs_worksheet.loc[ngs_worksheet["NGS_PLATE"] == plate, "Part ID"].values
        ):
            worksheet[f"AL{34 + i}"] = value
        workbook.save(submission_excel)
        submission_excel.seek(0)
        submission_excels[plate] = submission_excel

    return ngs_worksheet, submission_excels
