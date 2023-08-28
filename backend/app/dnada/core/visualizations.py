#!/usr/bin/env python3

from typing import List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def fill_plate(
    incompletePlate: pd.DataFrame,
    size: int = 384,
    fillValue: Union[int, str] = 0,
) -> pd.DataFrame:
    """Fill an incomplete plate pivot table with empty values

    Arguments
    ---------
    incompletePlate : pd.DataFrame
        A plate in the form of a pivot table
        with not all values defined.

    size : int, optional
        The size of the plate. Can be 384
        or 96 or 48. [default: 384]

    fillValue : int or str, optional
        The value to fill the empty cells
        with. [default: 0]

    Returns
    -------
    completePlate : pd.DataFrame
        A plate will all undefined cells filled
        with empty fill value
    """
    assert (
        (size == 96) or (size == 384) or (size == 48)
    ), f"{size} is not a valid plate size"

    shapeMap = {
        384: (list("ABCDEFGHIJKLMNOP"), range(1, 25)),
        96: (list("ABCDEFGH"), range(1, 13)),
        48: (list("ABCDEF"), range(1, 9)),
    }

    for column in shapeMap[size][1]:
        if str(column) not in incompletePlate.columns:
            incompletePlate[str(column)] = np.nan
    for row in shapeMap[size][0]:
        if row not in incompletePlate.index:
            incompletePlate = incompletePlate.append(
                pd.Series(np.nan, name=row, index=incompletePlate.columns)
            )
    completePlate = (
        incompletePlate.reindex(
            sorted(incompletePlate.columns, key=lambda x: int(x)), axis=1
        )
        .sort_index()
        .fillna(fillValue)
    )
    return completePlate


def visualize_plate(
    df: pd.DataFrame, size: int = 384, plateName: Optional[str] = None
) -> Tuple[plt.Figure, plt.axes, pd.DataFrame]:
    """Vizualize Plate with a heatmap and spreadsheet

    Arguments
    ---------
    df : pd.DataFrame
        Given a pandas dataframe containing 3 columns in this order:
        Well Location, Well Annotation, Well Full Name

    size : int, optional
        The size of the plate to vizualize wells on. Can be 96 or
        384 or 48. [default: 384]

    plateName : str, optional
        The name of the plate to vizualize [default: None]

    Returns
    -------
    fig : matplotlib.figure.Figure
        A matplotlib figure holding heatmap

    ax : matplotlib.axes._subplots.AxesSubplot
        The axes subplot that defines the heatmap

    nameDF : pd.DataFrame
        A pandas dataframe that contains detailed
        information about contents of each well.
    """
    assert (
        (size == 96) or (size == 384) or (size == 48)
    ), f"{size} is not a valid plate size"

    df["ROW"] = df.iloc[:, 0].apply(lambda well: well[0])
    df["COL"] = df.iloc[:, 0].apply(lambda well: str(int(well[1:])))
    df["VALUE"] = 1

    valueDF = df.pivot("ROW", "COL", "VALUE")
    annotDF = df.pivot("ROW", "COL", df.columns[1])
    nameDF = df.pivot("ROW", "COL", df.columns[2])

    valueDF = fill_plate(valueDF, size=size, fillValue=0)
    annotDF = fill_plate(annotDF, size=size, fillValue="")
    nameDF = fill_plate(nameDF, size=size, fillValue="")

    fig, ax = plt.subplots(figsize=(24, 18))
    sns.heatmap(
        valueDF,
        cbar=False,
        vmin=0,
        vmax=1,
        annot=annotDF,
        linewidths=0.5,
        fmt="s",
        annot_kws={"size": 10},
    )
    plt.yticks(rotation=0)
    ax.set(title=plateName, ylabel="ROW", xlabel="COLUMN")
    if size == 48:
        ax.invert_yaxis()
        ax.invert_xaxis()
    return (fig, ax, nameDF)


def vizualize_qplating_scheme(
    scheme: str,
) -> List[Tuple[plt.Figure, plt.axes, pd.DataFrame]]:
    """Vizualize qplate plating scheme

    Arguments
    ---------
    scheme : str
        Path to a csv that contains 3 columns:
        96-WELL, QPLATE, and QWELL. These 3 columns should
        contain the information necessary for a 96-well plate
        to be transferred to 2 48-well qplates. The 96_WELL
        column should include all 96 wells A1-H12. The QPLATE
        column shuold include only QPLATE_1 or QPLATE_2 values.
        The QWELL column should only include A1-F8 for both
        QPLATE_1 and QPLATE_2.

    Returns
    -------
    vizPlates : list of 3-tuple
        List of heatmap vizualization of qplates

    Notes
    -----
    In the vizualizations produced, the annotations within
    the boxes correspond to the 96-well. The labels on the
    x and y-axis correspond to the qplate rows and columns
    as if they were being read by the Qpix.
    """
    platingMap = pd.read_csv(scheme, header=0)
    tmpPlate1 = platingMap.loc[
        platingMap["QPLATE"] == "QPLATE_1", ["QWELL", "96_WELL"]
    ].rename(columns={"QWELL": "PLATE WELL", "96_WELL": "ANNOT"})
    tmpPlate1["LIQUID TYPE"] = tmpPlate1["ANNOT"]
    tmpPlate2 = platingMap.loc[
        platingMap["QPLATE"] == "QPLATE_2", ["QWELL", "96_WELL"]
    ].rename(columns={"QWELL": "PLATE WELL", "96_WELL": "ANNOT"})
    tmpPlate2["LIQUID TYPE"] = tmpPlate2["ANNOT"]
    vizPlates = [
        visualize_plate(tmpPlate, 48, f"QPLATE_{i+1}")
        for i, tmpPlate in enumerate([tmpPlate1, tmpPlate2])
    ]
    return vizPlates
