import numpy as np
from typing import Tuple, Optional, List
from scipy.optimize import OptimizeResult, linprog
import pandas as pd
from pandera.typing import DataFrame
import itertools
from app import schemas


def index_to_384_well(index: int) -> str:
    index = int(index % 384)
    possible_wells: List[str] = [
        f"{row}{column}"
        for row, column in itertools.product("ABCDEFGHIJKLMNOP", range(1, 25))
    ]
    index_well_map = {
        biomek_index: letter_number
        for letter_number, biomek_index in zip(possible_wells, range(1, 385))
    }
    return index_well_map[index]


def optimize_equimolar_assembly_rxn(
    conc: np.ndarray, max_vol: float, max_fmol: float
) -> np.ndarray:
    """
    Arguments
    ---------
    conc: np.array
        Concentrations of each part in a reaction

    max_vol: float
        Max total volume allowed for reaction (in uL)

    max_fmol: float
        Max amount of part used for reaction (in fmols)
    """
    # Objective: maximize mols used subject to following constraints
    c: np.ndarray = conc * -1

    # Each part has maximum mol
    A_ub: np.ndarray = np.diag(c * -1)
    b_ub: np.ndarray = np.full(c.size, fill_value=max_fmol)

    # Total volume of all parts should be less than max_vol
    A_ub = np.vstack([A_ub, np.ones(c.size)])
    b_ub = np.hstack([b_ub, np.array([max_vol])])

    # Each part should use equal mol
    A_eq: np.ndarray = np.eye(N=c.size - 1, M=c.size, k=1)
    np.fill_diagonal(A_eq, -1.0)
    A_eq = A_eq * c

    b_eq: np.ndarray = np.zeros(c.size - 1)

    # Each part volume should be non-negative and under the max volume
    bounds: Tuple[float, Optional[float]] = (0, max_vol)

    # Perform optimization
    result: OptimizeResult = linprog(
        c=c,
        A_ub=A_ub,
        b_ub=b_ub,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
    )
    volumes: np.ndarray = np.zeros(c.size)
    if not result.status:
        volumes = result.x
    return volumes


def add_water_to_assembly(
    assembly_worksheet: pd.DataFrame,
    max_vol: float = 5.0,  # uL
    volume_column: str = "EQUIMOLAR_VOLUME",
) -> pd.DataFrame:
    water_required = (
        max_vol - assembly_worksheet.groupby("Number").agg({volume_column: "sum"})
    ).reset_index()
    water_required["Part Name"] = "water"
    water_required["Destination Plate"] = water_required["Number"].apply(
        lambda number: assembly_worksheet.loc[
            assembly_worksheet["Number"] == number, "Destination Plate"
        ].values[0]
    )
    water_required["Destination Well"] = water_required["Number"].apply(
        lambda number: assembly_worksheet.loc[
            assembly_worksheet["Number"] == number, "Destination Well"
        ].values[0]
    )
    water_required = water_required.loc[
        ~np.isclose(water_required[volume_column], 0.0, atol=1e-3), :
    ]
    water_required["Source Plate"] = "water_plate"
    water_required["Source Well"] = (water_required[volume_column].cumsum() // 45) + 1
    water_required["Source Plate"] = water_required["Source Well"].apply(
        lambda well: f"water_plate_{int(well//384)+1}"
    )
    water_required["Source Well"] = water_required["Source Well"].apply(
        index_to_384_well
    )
    return pd.concat([assembly_worksheet, water_required])


def create_equimolar_assembly_instructions(
    assembly_df: DataFrame[schemas.AssemblyWorksheetSchema],
    quant_df: DataFrame[schemas.PartsWorksheetSchema],
    max_fmol: float = 100.0,
    max_vol: float = 5.0,
    max_part_percentage: float = 1.0,
) -> DataFrame[schemas.EquimolarAssemblyWorksheetSchema]:
    equimolar_worksheet = assembly_df.merge(
        quant_df,
        left_on=["Source Plate", "Source Well"],
        right_on=["PART_PLATE", "PART_WELL"],
    ).sort_values(["Number", "Part Order"])
    # Formula from: https://nebiocalculator.neb.com/#!/dsdnaamt
    equimolar_worksheet["Conc (fmol/uL)"] = (
        (equimolar_worksheet["Conc (ng/uL)"] * 1e-6)
        / ((equimolar_worksheet["PART_LENGTH"] * 617.96) + 36.04)
    ) * 1e12
    equimolar_worksheet["EQUIMOLAR_VOLUME"] = 0

    for rxn in equimolar_worksheet["Number"].unique():
        conc: np.ndarray = equimolar_worksheet.loc[
            equimolar_worksheet["Number"] == rxn, "Conc (fmol/uL)"
        ].values
        vol: np.ndarray = optimize_equimolar_assembly_rxn(
            conc=conc,
            max_vol=max_vol * max_part_percentage,
            max_fmol=max_fmol,
        )
        equimolar_worksheet.loc[
            equimolar_worksheet["Number"] == rxn, "EQUIMOLAR_VOLUME"
        ] = vol
    equimolar_worksheet["fmol_used"] = (
        equimolar_worksheet["Conc (fmol/uL)"] * equimolar_worksheet["EQUIMOLAR_VOLUME"]
    )
    equimolar_worksheet = add_water_to_assembly(
        assembly_worksheet=equimolar_worksheet,
        max_vol=max_vol,
        volume_column="EQUIMOLAR_VOLUME",
    )
    equimolar_worksheet["Transfer Volume"] = (
        equimolar_worksheet["EQUIMOLAR_VOLUME"] * 1000
    ).map(int)
    return equimolar_worksheet
