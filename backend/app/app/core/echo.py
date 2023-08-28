import pandas as pd
from app import schemas
from pandera import check_types
from pandera.typing import DataFrame


@check_types()
def create_echo_instructions(
    worksheet: pd.DataFrame, method: str
) -> DataFrame[schemas.EchoInstructionsSchema]:
    """Given a worksheet, create echo instructions

    Arguments
    ---------
    worksheet : pd.DataFrame
        A pandas dataframe that contains information
        about how to set up PCR or assembly rxns

    method : str
        The type of worksheet given. Can be either
        'pcr', 'assembly', or 'zag'

    Returns
    -------
    echoPlate : pd.DataFrame
        A pandas dataframe that contains echo
        instructions
    """
    if worksheet.empty:
        return pd.DataFrame(
            columns=[
                "Source Plate Name",
                "Source Well",
                "Destination Plate Name",
                "Destination Well",
                "Transfer Volume",
            ]
        )
    echoPlate = pd.DataFrame()
    if method == "pcr":
        echoPlate["Source Plate Name"] = pd.concat(
            [
                worksheet["PRIMER1_PLATE"],
                worksheet["PRIMER2_PLATE"],
                worksheet["TEMPLATE_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Source Well"] = pd.concat(
            [
                worksheet["PRIMER1_WELL"],
                worksheet["PRIMER2_WELL"],
                worksheet["TEMPLATE_WELL"],
            ],
            axis=0,
        )
        echoPlate["Destination Plate Name"] = pd.concat(
            [
                worksheet["OUTPUT_PLATE"],
                worksheet["OUTPUT_PLATE"],
                worksheet["OUTPUT_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Destination Well"] = pd.concat(
            [
                worksheet["OUTPUT_WELL"],
                worksheet["OUTPUT_WELL"],
                worksheet["OUTPUT_WELL"],
            ],
            axis=0,
        )
        echoPlate["Transfer Volume"] = pd.concat(
            [
                worksheet["PRIMER1_VOLUME"],
                worksheet["PRIMER2_VOLUME"],
                worksheet["TEMPLATE_VOLUME"],
            ],
            axis=0,
        )
    elif method == "assembly":
        echoPlate = worksheet.loc[
            :,
            [
                "Source Plate",
                "Source Well",
                "Destination Plate",
                "Destination Well",
            ],
        ]
        echoPlate["Transfer Volume"] = 2000  # nL
        echoPlate = echoPlate.rename(
            columns={
                "Source Plate": "Source Plate Name",
                "Destination Plate": "Destination Plate Name",
            }
        )
    elif method == "equimolar":
        echoPlate = worksheet.loc[
            :,
            [
                "Source Plate",
                "Source Well",
                "Destination Plate",
                "Destination Well",
                "Transfer Volume",
            ],
        ]
        echoPlate = echoPlate.rename(
            columns={
                "Source Plate": "Source Plate Name",
                "Destination Plate": "Destination Plate Name",
            }
        )
    elif method == "zag":
        echoPlate = worksheet.loc[
            :,
            ["PARTS_SOURCE_PLATE", "PARTS_WELL", "ZAG_PLATE", "ZAG_WELL"],
        ].copy()
        echoPlate["Transfer Volume"] = 500
        echoPlate.columns = [
            "Source Plate Name",
            "Source Well",
            "Destination Plate Name",
            "Destination Well",
            "Transfer Volume",
        ]
    elif method == "custom":
        partColumnHeaders = [
            column
            for column in worksheet.columns
            if (column.startswith("Part(s)"))
            and (not column.endswith(("ID", "Source Plate", "Well")))
        ]
        echoPlate["Source Plate Name"] = pd.concat(
            [worksheet[f"{part} Source Plate"] for part in partColumnHeaders],
            axis=0,
        )
        echoPlate["Source Well"] = pd.concat(
            [worksheet[f"{part} Well"] for part in partColumnHeaders],
            axis=0,
        )
        echoPlate["Destination Plate Name"] = pd.concat(
            [worksheet["Assembly Plate"] for part in partColumnHeaders],
            axis=0,
        )
        echoPlate["Destination Well"] = pd.concat(
            [worksheet["Assembly Well"] for part in partColumnHeaders],
            axis=0,
        )
        echoPlate["Transfer Volume"] = 2000  # nL
    elif method == "quant":
        echoPlate = worksheet.loc[
            :,
            [
                "PART_PLATE",
                "PART_WELL",
                "QUANT_PLATE",
                "QUANT_WELL",
                "QUANT_VOLUME",
            ],
        ].copy()
        echoPlate.columns = [
            "Source Plate Name",
            "Source Well",
            "Destination Plate Name",
            "Destination Well",
            "Transfer Volume",
        ]
    elif method == "redo_pcr":
        echoPlate["Source Plate Name"] = pd.concat(
            [
                worksheet["PRIMER1_PLATE"],
                worksheet["PRIMER2_PLATE"],
                worksheet["TEMPLATE_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Source Well"] = pd.concat(
            [
                worksheet["PRIMER1_WELL"],
                worksheet["PRIMER2_WELL"],
                worksheet["TEMPLATE_WELL"],
            ],
            axis=0,
        )
        echoPlate["Destination Plate Name"] = pd.concat(
            [
                worksheet["REDO_PLATE"],
                worksheet["REDO_PLATE"],
                worksheet["REDO_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Destination Well"] = pd.concat(
            [
                worksheet["REDO_WELL"],
                worksheet["REDO_WELL"],
                worksheet["REDO_WELL"],
            ],
            axis=0,
        )
        echoPlate["Transfer Volume"] = pd.concat(
            [
                worksheet["PRIMER1_VOLUME"],
                worksheet["PRIMER2_VOLUME"],
                worksheet["TEMPLATE_VOLUME"],
            ],
            axis=0,
        )
    elif method == "colony_pcr":
        echoPlate["Source Plate Name"] = pd.concat(
            [
                worksheet["PRIMER1_PLATE"],
                worksheet["PRIMER2_PLATE"],
                worksheet["NGS_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Source Well"] = pd.concat(
            [
                worksheet["PRIMER1_WELL"],
                worksheet["PRIMER2_WELL"],
                worksheet["NGS_WELL"],
            ],
            axis=0,
        )
        echoPlate["Destination Plate Name"] = pd.concat(
            [
                worksheet["COLONY_PCR_PLATE"],
                worksheet["COLONY_PCR_PLATE"],
                worksheet["COLONY_PCR_PLATE"],
            ],
            axis=0,
        )
        echoPlate["Destination Well"] = pd.concat(
            [
                worksheet["COLONY_PCR_WELL"],
                worksheet["COLONY_PCR_WELL"],
                worksheet["COLONY_PCR_WELL"],
            ],
            axis=0,
        )
        echoPlate["Transfer Volume"] = pd.concat(
            [
                worksheet["PRIMER1_VOLUME"],
                worksheet["PRIMER2_VOLUME"],
                worksheet["NGS_VOLUME"],
            ],
            axis=0,
        )
    echoPlate = (
        echoPlate.dropna()
        .sort_values(
            [
                "Source Plate Name",
                "Destination Plate Name",
                "Source Well",
                "Destination Well",
            ],
            ascending=[True, True, True, True],
        )
        .reset_index(drop=True)
    )
    return echoPlate
