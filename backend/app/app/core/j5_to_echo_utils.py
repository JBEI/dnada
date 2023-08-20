#!/usr/bin/env python3

import ast
import itertools
import os
from fnmatch import fnmatch
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from fastapi import HTTPException
from pandera import check_types
from pandera.typing import DataFrame
from app import schemas

OUTPUT_OLIGOS_PLATE_FILENAME = "oligos_plate.csv"
OUTPUT_TEMPLATES_PLATE_FILENAME = "templates_plate.csv"
OUTPUT_PCR_MIX_TUBES_FILENAME = "pcr_mix_tubes.csv"
MONTE_CARLO_STEPS = 100
MAX_WELL_USES = 8


def mkdir(path: str) -> None:
    """Make a directory

    Arguments
    ---------
    path : str
        The path to the directory you want to create

    Returns
    -------
    None
    """
    fullPath = os.path.abspath(os.path.realpath(path))
    if not os.path.isdir(fullPath):
        try:
            os.mkdir(fullPath)
        except Exception:
            pass  # race condition


def stamp(sourceWell: str, location: int) -> str:
    """Stamp a source well from 96-well plate to a 384-well plate

    Arguments
    ---------
    sourceWell : str
        well location on 96-well plate

    location : int
        Either 0, 1, 2, or 3 which corresponds to top-left,
        top-right, bottom-left, or bottom-right.

    Returns
    -------
    destinationWell : str
        well location on 384-well plate

    Examples
    --------
    >>> stamp('A1', 0)
    'A1'
    >>> stamp('A1', 3)
    'B2'
    >>> stamp('A2', 0)
    'A3'
    """
    standard96Wells = [
        f"{row}{column}" for row, column in itertools.product("ABCDEFGH", range(1, 13))
    ]
    assert location in [0, 1, 2, 3], "Not a valid 384-well plate location"
    assert sourceWell in standard96Wells, "Not a valid well in 96-well plate"
    stampMap: Dict[int, Dict[str, str]] = {0: {}, 1: {}, 2: {}, 3: {}}
    stampMap[0] = {
        well96: well384
        for well96, well384 in zip(
            standard96Wells,
            [
                f"{row}{column}"
                for row, column in itertools.product("ACEGIKMO", range(1, 25, 2))
            ],
        )
    }
    stampMap[1] = {
        well96: well384
        for well96, well384 in zip(
            standard96Wells,
            [
                f"{row}{column}"
                for row, column in itertools.product("ACEGIKMO", range(2, 25, 2))
            ],
        )
    }
    stampMap[2] = {
        well96: well384
        for well96, well384 in zip(
            standard96Wells,
            [
                f"{row}{column}"
                for row, column in itertools.product("BDFHJLNP", range(1, 25, 2))
            ],
        )
    }
    stampMap[3] = {
        well96: well384
        for well96, well384 in zip(
            standard96Wells,
            [
                f"{row}{column}"
                for row, column in itertools.product("BDFHJLNP", range(2, 25, 2))
            ],
        )
    }
    destinationWell = stampMap[location][sourceWell]
    return destinationWell


def convert3WellTo2Well(well: str) -> str:
    """Changes notation from 2-index well number to normal

    Arguments
    ---------
    well : str
        well location with 2-index well number, e.g. A01, A02

    Returns
    -------
    normalWell : str
        well location with normal index well number, e.g. A1

    Examples
    --------
    >>> convert3WellTo2Well('A01')
    'A1'
    >>> convert3WellTo2Well('A11')
    'A11'
    >>> convert3WellTo2Well('B03')
    'B3'
    """
    return well[0] + str(int(well[1:]))


def convert2WellTo3Well(well: str) -> str:
    """Changes notation from normal well number to 2-index number

    Arguments
    ---------
    well : str
        well location with normal well number, e.g. A1, A2

    Returns
    -------
    fixedWell : str
        well location with 2-index  well number, e.g. A01, A02

    Examples
    --------
    >>> convert2WellTo3Well('A1')
    'A01'
    >>> convert2WellTo3Well('A11')
    'A11'
    """
    return well[0] + well[1:].zfill(2)


def distributeWells(
    numberOfUses: int,
    availableWells: List[Tuple[str, str]],
    maxWellUses: int = 5,
) -> List[Tuple[str, str]]:
    """Distributes uses to available wells

    Arguments
    ---------
    numberOfUses : int
        The number of times that a particular part
        is being used

    availableWells : list of 2-tuples
        A list of strings containing well locations that
        a part is contained in
        e.g. [('parts_plate_1','M20'), ('parts_plate_1','O20')]

    maxWellUses : int, optional
        The maximum number of times that a well
        can be used [default: 5]

    Returns
    -------
    distributedWells : list
        A distributed series of wells so that a single
        well is not used more than maxWellUses times.

    Raises
    ------
    IndexError
        If there are not enough available wells for the
        number of uses then that is a problem. Either change
        the maxWellUses, decrease the numberOfUses, or increase
        the number of availableWells.

    Examples
    --------
    >>> distributeWells(6,
    ... [('parts_plate_1','M20'), ('parts_plate_1','O20')], maxWellUses=5)
    ['M20', 'M20', 'M20', 'M20', 'M20', 'O20']
    >>> distributeWells(5,
    ... [('parts_plate_1','M20'), ('parts_plate_1','O20')], maxWellUses=5)
    ['M20', 'M20', 'M20', 'M20', 'M20']
    >>> distributeWells(6,
    ... [('parts_plate_1','M20'), ('parts_plate_1','O20')], maxWellUses=4)
    ['M20', 'M20', 'M20', 'M20', 'O20', 'O20']
    """
    try:
        distributedWells = [
            availableWells[i // maxWellUses] for i in range(numberOfUses)
        ]
    except IndexError:
        raise HTTPException(
            status_code=500,
            detail="Not enough available wells for number of uses",
        )
    return distributedWells


def collectFiles(pattern: str, directory: str) -> list:
    """Collect files that match pattern in directory

    Arguments
    ---------
    pattern : str
        Glob pattern

    directory : str
        Path to a directory that function will search files

    Returns
    -------
    matchedFiles : list
        A list of full file paths to files that match pattern

    Notes
    -----
    Also excludes files that come from masterzippedsequences
    directory. This directory normally comes in a zip file in
    every j5 design, but if unzipped will contain source plasmid
    genbank files. Any directory that is named
    masterzippedsequences will be excluded from matching.
    """
    matchedFiles = []
    for path, subdirs, files in os.walk(directory):
        for file in files:
            if fnmatch(file, pattern):
                matchedFiles.append(os.path.join(path, file))
    return [
        matchedFile
        for matchedFile in matchedFiles
        if "masterzippedsequences" not in matchedFile
    ]


def necessaryRxnsFromUses(numberOfUses: int, maxRxnUses: int = 4) -> int:
    """Find the number of rxns necessary for its uses

    Arguments
    ---------
    numberOfUses : int
        The number of uses that a part will get

    maxRxnUses : int
        The number of rxns that a well can sustain

    Returns
    -------
    numberOfRxns : int
        The number of rxns necessary to meet part demands

    Examples
    --------
    >>> necessaryRxnsFromUses(1)
    1
    >>> necessaryRxnsFromUses(2)
    1
    >>> necessaryRxnsFromUses(3)
    1
    >>> necessaryRxnsFromUses(4)
    1
    >>> necessaryRxnsFromUses(5)
    2
    """
    return (numberOfUses - 1) // maxRxnUses + 1


def fillPlate(
    incompletePlate: pd.DataFrame, size: int = 384, fillValue: int = 0
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


def unstamp(destWell):
    """Unstamp a dest well from 384-well plate to a 96-well plate

    Arguments
    ---------
    destWell : str
        well location on 384-well plate

    Returns
    -------
    sourceWell : str
        well location on 96-well plate

    Examples
    --------
    >>> unstamp('A1')
    'A1'
    >>> unstamp('A2')
    'A1'
    >>> unstamp('A3')
    'A2'
    >>> unstamp('B5')
    'A3'
    >>> unstamp('C5')
    'B3'
    """
    standard384Wells = [
        f"{row}{column}"
        for row, column in itertools.product("ABCDEFGHIJKLMNOP", range(1, 25))
    ]
    [f"{row}{column}" for row, column in itertools.product("ABCDEFGH", range(1, 13))]
    assert destWell in standard384Wells, "Not a valid well in 384-well plate"
    stampMap = {
        well384: well96
        for well384, well96 in zip(
            standard384Wells,
            [
                f"{row}{column}"
                for row, column in itertools.product(
                    "AABBCCDDEEFFGGHH",
                    [
                        1,
                        1,
                        2,
                        2,
                        3,
                        3,
                        4,
                        4,
                        5,
                        5,
                        6,
                        6,
                        7,
                        7,
                        8,
                        8,
                        9,
                        9,
                        10,
                        10,
                        11,
                        11,
                        12,
                        12,
                    ],
                )
            ],
        )
    }
    sourceWell = stampMap[destWell]
    return sourceWell


def unstampOligos(destWell):
    """Unstamp a dest well from 384-well plate to a 96-well plate

    Used for maximizing space in 96 well plate

    Arguments
    ---------
    destWell : str
        well location on 96-well plate

    Returns
    -------
    sourceWell : str
        well location on 384-well plate

    Examples
    --------
    >>> unstamp('A1')
    'A1'
    >>> unstamp('A2')
    'B1'
    >>> unstamp('A3')
    'A2'
    >>> unstamp('B5')
    'C3'
    >>> unstamp('C5')
    'E3'
    """
    standard384Wells = [
        f"{row}{column}"
        for row, column in itertools.product("ABCDEFGHIJKLMNOP", range(1, 25))
    ]
    [f"{row}{column}" for row, column in itertools.product("ABCDEFGH", range(1, 13))]
    assert destWell in standard384Wells, "Not a valid well in 384-well plate"
    stampMap = {
        well384: well96
        for well384, well96 in zip(
            standard384Wells,
            [
                f"{row}{column}"
                for row, column in list(
                    list(
                        zip(
                            "ABABABABABABABABABABABAB",
                            [
                                1,
                                1,
                                2,
                                2,
                                3,
                                3,
                                4,
                                4,
                                5,
                                5,
                                6,
                                6,
                                7,
                                7,
                                8,
                                8,
                                9,
                                9,
                                10,
                                10,
                                11,
                                11,
                                12,
                                12,
                            ],
                        )
                    )
                    + list(
                        zip(
                            "CDCDCDCDCDCDCDCDCDCDCDCD",
                            [
                                1,
                                1,
                                2,
                                2,
                                3,
                                3,
                                4,
                                4,
                                5,
                                5,
                                6,
                                6,
                                7,
                                7,
                                8,
                                8,
                                9,
                                9,
                                10,
                                10,
                                11,
                                11,
                                12,
                                12,
                            ],
                        )
                    )
                    + list(
                        zip(
                            "EFEFEFEFEFEFEFEFEFEFEFEF",
                            [
                                1,
                                1,
                                2,
                                2,
                                3,
                                3,
                                4,
                                4,
                                5,
                                5,
                                6,
                                6,
                                7,
                                7,
                                8,
                                8,
                                9,
                                9,
                                10,
                                10,
                                11,
                                11,
                                12,
                                12,
                            ],
                        )
                    )
                    + list(
                        zip(
                            "GHGHGHGHGHGHGHGHGHGHGHGH",
                            [
                                1,
                                1,
                                2,
                                2,
                                3,
                                3,
                                4,
                                4,
                                5,
                                5,
                                6,
                                6,
                                7,
                                7,
                                8,
                                8,
                                9,
                                9,
                                10,
                                10,
                                11,
                                11,
                                12,
                                12,
                            ],
                        )
                    )
                )
                * 4
            ],
        )
    }
    sourceWell = stampMap[destWell]
    return sourceWell


def processPeakTable(peakTableFile, plateName, write=True, need3Well=False):
    """Find dominant peaks in ZAG Peak File

    Arguments
    ---------
    peakTableFile : str
        Path to a peak file produced by the ZAG

    plateName : str
        The name of the plate that the ZAG analyzed.
        Use this to correlate zag results with
        expected size table

    write : bool, optional
        Whether to write the results of the peak table
        processing to disk [default: True]

    need3Well : bool, optional
        Whether the index for the pcr worksheet is 2 or
        3 indexed meaning is it A1 vs A01. [default: False]

    Returns
    -------
    fullPlate : pandas.DataFrame
        A dataframe containing information about the dominant
        peak in each well

    Notes
    -----
    Currently, the dominant peak is found by filtering all
    the peaks identified in the peak table with % Concentration
    greater than 50 and integrated concentration greater
    than 5 ng/uL.

    Note that this discriminates against those samples that have
    multiple defined peaks, e.g. if a sample has 2 peaks with both
    having 48% Conc. it will be filtered out.
    """
    peakTable = pd.read_csv(peakTableFile, header=0, index_col=0)
    sizeThreshold = 175
    rfuThreshold = 1500
    for well in peakTable.index.unique():
        filteredArea = peakTable.loc[
            (peakTable.index == well) & (peakTable["Size (bp)"] < sizeThreshold),
            "ng/ul",
        ].sum()
        originalWellTIC = peakTable.loc[peakTable.index == well, "TIC (ng/ul)"].max()
        filteredWellTIC = originalWellTIC - filteredArea
        peakTable.loc[peakTable.index == well, "TIC (ng/ul)"] = filteredWellTIC
        peakTable.loc[
            (peakTable.index == well) & (peakTable["Size (bp)"] < sizeThreshold),
            "ng/ul",
        ] = 0
        peakTable.loc[peakTable.index == well, "% (Conc.)"] = peakTable.loc[
            peakTable.index == well, :
        ].apply(lambda row: (row["ng/ul"] / row["TIC (ng/ul)"]) * 100, axis=1)
    validPeaks = peakTable.loc[
        (peakTable["% (Conc.)"] > 40.0)
        & (peakTable["ng/ul"] > 2.0)
        & (peakTable["Size (bp)"] > sizeThreshold)
        & (peakTable["RFU"] > rfuThreshold),
        ["% (Conc.)", "Size (bp)", "nmole/L", "ng/ul"],
    ]
    allPlateWells = np.array(
        [
            f"{row}{column}"
            for row, column in itertools.product("ABCDEFGH", range(1, 13))
        ]
    )
    wellsWithoutPeaks = allPlateWells[
        np.isin(allPlateWells, validPeaks.index, invert=True)
    ]
    wellsWithoutPeaksDF = pd.DataFrame(
        {
            "% (Conc.)": np.nan,
            "Size (bp)": np.nan,
            "nmole/L": np.nan,
            "ng/ul": np.nan,
        },
        index=wellsWithoutPeaks,
    )
    wellsWithoutPeaksDF = wellsWithoutPeaksDF.rename_axis("Well")
    fullPlate = validPeaks.append(wellsWithoutPeaksDF).sort_values(by="Well")
    fullPlate["SOURCE_PLATE"] = plateName
    if need3Well:
        fullPlate["SOURCE_LOCATION"] = fullPlate.apply(
            lambda row: "#".join([row["SOURCE_PLATE"], convert2WellTo3Well(row.name)]),
            axis=1,
        )
    else:
        fullPlate["SOURCE_LOCATION"] = fullPlate.apply(
            lambda row: "#".join([row["SOURCE_PLATE"], row.name]), axis=1
        )
    if write:
        fullPlate.to_csv(peakTableFile.replace(".csv", "-processed.csv"), index=True)
    return fullPlate


def bandIsExpected(band, expected, threshold=0.50):
    """Determine if band falls within a threshold of expected size

    Arguments
    ---------
    band : int
        The band size calculated by the ZAG

    expected : int
        The expected band size

    threshold : float, optional
        Optional threshold value between 0 and 1 [default: 0.30]

    Returns
    -------
    good : bool
        True if the band falls withing a threshold of expected size,
        False otherwise
    """
    good = False
    if (expected * (1 - threshold) < band) and (band < expected * (1 + threshold)):
        good = True
    return good


def determineSuccessfulBands(
    pcrWorksheet,
    peakTables,
    plateColumns=("OUTPUT_PLATE", "OUTPUT_WELL", "EXPECTED_SIZE"),
    tolerance=0.55,
    need3Well=False,
):
    """Determine whether bands are valid

    Arguments
    ---------
    pcrWorksheet : DataFrame
        Clean pcr worksheet with expected
        band size information

    peakTables : dict
        Dictionary of plate name to zag results; key to value
        pairs. The plate name should correspond to the name of
        the plate analyzed and the plate location on the
        pcr worksheet

    plateColumns : 3-tuple, optional
        Optional 3-tuple containing the pcr worksheet column names
        of the zag analyzed plate and
        well and size [default: ('OUTPUT_PLATE', 'OUTPUT_WELL', 'EXPECTED_SIZE')]

    tolerance : float
        Threshold for error when evaluating band sizes

    need3Well : bool, optional
        Whether the index for the pcr worksheet is 2 or
        3 indexed meaning is it A1 vs A01. [default: False]

    Returns
    -------
    updatedPcrWorksheet : pandas.DataFrame
        Updated pcr worksheet containing zag analysis information
    """
    pcrDF = pcrWorksheet
    need3Well = True
    pcrDF["OUTPUT_LOCATION"] = pcrDF.apply(
        lambda row: "#".join(
            [
                row[plateColumns[0]],
                convert2WellTo3Well(row[plateColumns[1]]),
            ]
        ),
        axis=1,
    )
    peakTablesData = pd.concat(
        [
            processPeakTable(
                peakTables[peakTable],
                peakTable,
                write=False,
                need3Well=need3Well,
            )
            for peakTable in peakTables
        ]
    )
    pcrDF["BAND_SIZE"] = pcrDF.apply(
        lambda row: peakTablesData.loc[
            row["OUTPUT_LOCATION"] == peakTablesData["SOURCE_LOCATION"],
            "Size (bp)",
        ].values[-1],
        axis=1,
    )
    pcrDF["BAND_%_OF_TOTAL"] = pcrDF.apply(
        lambda row: peakTablesData.loc[
            row["OUTPUT_LOCATION"] == peakTablesData["SOURCE_LOCATION"],
            "% (Conc.)",
        ].values[-1],
        axis=1,
    )
    pcrDF["BAND_CONC_ng/ul"] = pcrDF.apply(
        lambda row: peakTablesData.loc[
            row["OUTPUT_LOCATION"] == peakTablesData["SOURCE_LOCATION"],
            "ng/ul",
        ].values[-1],
        axis=1,
    )
    pcrDF["BAND_CONC_nmole/L"] = pcrDF.apply(
        lambda row: peakTablesData.loc[
            row["OUTPUT_LOCATION"] == peakTablesData["SOURCE_LOCATION"],
            "nmole/L",
        ].values[-1],
        axis=1,
    )
    pcrDF["GOOD"] = pcrDF.apply(
        lambda row: bandIsExpected(
            row["BAND_SIZE"], row[plateColumns[2]], threshold=tolerance
        ),
        axis=1,
    )
    return pcrDF


def findPossibleConstructs(pcrWorksheet, assemblyWorksheet):
    """Determine whether all pcr parts for a construct exist

    Arguments
    ---------
    pcrWorksheet : str
        Path to a clean pcr worksheet containing 'GOOD' column
        that is made from a ZAG analysis of PCRs

    assemblyWorksheet : str
        Path to a clean assembly worksheet containing
        a 'Part Locations' column

    Returns
    -------
    updatedAssemblyWorksheet : pandas.DataFrame
        An updated clean assembly worksheet containing two
        extra columns that signify whether the parts required
        for each construct exist

    Notes
    -----
    Assumes that we always have digested and synthesized pieces
    """
    pcrDF = pd.read_csv(pcrWorksheet, header=0, index_col=0)
    assemblyDF = pd.read_csv(
        assemblyWorksheet,
        header=0,
        index_col=0,
        converters={"Part Locations": ast.literal_eval},
    )

    if "Part Locations" not in assemblyDF.columns:
        assemblyDF["Part Locations"] = assemblyDF.apply(
            lambda row: [
                (
                    row[column],
                    row[column.replace("Source Plate", "Well")],
                    "PCR",
                )
                for column in assemblyDF.columns.values
                if (column.endswith("Source Plate") and not pd.isna(row[column]))
            ],
            axis=1,
        )

    assemblyDF["Part Existence"] = assemblyDF["Part Locations"].apply(
        lambda partLocations: [
            (
                pcrDF.loc[
                    (pcrDF["PARTS_SOURCE_PLATE"] == partLocation[0])
                    & (pcrDF["PARTS_WELL"] == partLocation[1]),
                    "GOOD",
                ].values[0]
                if partLocation[2] == "PCR"
                else True
            )
            for partLocation in partLocations
        ]
    )
    assemblyDF["Construct Good"] = assemblyDF["Part Existence"].apply(
        lambda constructParts: all(constructParts)
    )
    return assemblyDF


def identifyPartsForConstruct(row, partColumnHeaders, quantResults):
    constructStuff = []
    for part in partColumnHeaders:
        try:
            concentration = quantResults.loc[
                (row[f"{part} Source Plate"] == quantResults["PARTS_SOURCE_PLATE"])
                & (row[f"{part} Well"] == quantResults["PARTS_WELL"]),
                "CONC",
            ].values[0]
            constructStuff.append(
                (
                    row[f"{part} Source Plate"],
                    row[f"{part} Well"],
                    row["Destination Plate"],
                    row["Destination Well"],
                    concentration,
                )
            )
        except IndexError:
            pass
    return constructStuff


def calculateSingleConstructEquimolarVolumes(constructData, maxfmol=100, maxVolume=5):
    """Create Equimolar Assembly instructions

    Arguments
    ---------
    constructData : 5-tuple
        5-tuple containing source plate, source well, dest plate, dest
        well, and concentration of each part in construct

    maxfmol : float
        Maximum picomols of DNA to use for a given part

    maxVolume : float
        Maximum volume for an assembly rxn including all parts

    Returns
    -------
    echoInstructions : pd.DataFrame
        Assembly echo instructions

    Notes
    -----
    Logical process:
    1. Try to see if each part can obtain the max fmol and
    maintain a total assembly volume less than the max volume. If
    it can, then fill the rest with water
    2. If it can't, then decrease the fmol obtained until the maxVolume
    threshold can be maintained
    """
    numbers = np.array([part[4] for part in constructData])
    trueMaxfmol = maxVolume / np.sum(1 / numbers)
    if trueMaxfmol > maxfmol:
        realfmol = maxfmol
        volumes = realfmol / numbers
        water = maxVolume - sum(volumes)
    else:
        realfmol = trueMaxfmol
        volumes = realfmol / numbers
        water = 0
    newData = []
    for i, info in enumerate(constructData):
        newData.append(
            [
                info[0],  # source plate
                info[1],  # source well
                info[2],  # dest plate
                info[3],  # dest well
                info[4],  # conc
                volumes[i],  # volume
                realfmol,  # total fmol
            ]
        )
    return (newData, water)


def createEquimolarAssemblyInstructions(assemblyDF, quantDF, maxfmol=100, maxVolume=5):
    """Create Equimolar Assembly instructions

    Arguments
    ---------
    assemblyDF : pd.DataFrame
        Clean assembly instructions

    quantDF : pd.DataFrame
        Quantification results containing at least 3 columns:
        PARTS_SOURCE_PLATE, PARTS_WELL, CONC

    maxfmol : float
        Maximum picomols of DNA to use for a given part

    maxVolume : float
        Maximum volume for an assembly rxn including all parts

    Returns
    -------
    echoInstructions : pd.DataFrame
        Assembly echo instructions

    Notes
    -----
    Logical process:
    1. Try to see if each part can obtain the max fmol and
    maintain a total assembly volume less than the max volume. If
    it can, then fill the rest with water
    2. If it can't, then decrease the fmol obtained until the maxVolume
    threshold can be maintained
    """
    partColumnHeaders = [
        column
        for column in assemblyDF.columns
        if (column.startswith("Part(s)"))
        and (not column.endswith(("ID", "Source Plate", "Well")))
    ]
    equimolarAssemblyInfo = assemblyDF.apply(
        lambda row: calculateSingleConstructEquimolarVolumes(
            identifyPartsForConstruct(row, partColumnHeaders, quantDF),
            maxfmol=maxfmol,
            maxVolume=maxVolume,
        ),
        axis=1,
    )
    sourcePlate, sourceWell, destPlate, destWell, vol, fmol, conc = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for construct in equimolarAssemblyInfo.values:
        sourcePlate += [feature[0] for feature in construct[0]]
        sourceWell += [feature[1] for feature in construct[0]]
        destPlate += [feature[2] for feature in construct[0]]
        destWell += [feature[3] for feature in construct[0]]
        conc += [feature[4] for feature in construct[0]]
        vol += [int(feature[5] * 1000) for feature in construct[0]]
        fmol += [feature[6] for feature in construct[0]]
    worksheet = pd.DataFrame(
        {
            "Source Plate Name": sourcePlate,
            "Source Well": sourceWell,
            "Destination Plate Name": destPlate,
            "Destination Well": destWell,
            "Transfer Volume": vol,
            "Conc (fmol/uL)": conc,
            "fmol Transferred": fmol,
        }
    )
    for construct in equimolarAssemblyInfo:
        worksheet.append(
            pd.DataFrame(
                {
                    "Source Plate Name": "water_plate",
                    "Source Well": "TODO",
                    "Destination Plate Name": construct[0][0][2],
                    "Destination Well": construct[0][0][3],
                    "Transfer Volume": construct[1],
                    "Conc (fmol/uL)": 0,
                    "fmol Transferred": 0,
                },
                index=[0],
            )
        ).reset_index(drop=True)
    worksheet = (
        worksheet.dropna()
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
    worksheet["Conc (fmol/uL)"] = worksheet["Conc (fmol/uL)"].round(12)
    worksheet["fmol Transferred"] = worksheet["fmol Transferred"].round(12)
    return worksheet


def flattenColumn(df, column):
    """Flatten a list in a dataframe

    Notes
    -----
    Adapted from: https://stackoverflow.com/q/21160134

    column is a string of the column's name.
    for each value of the column's element (which might be a list),
    duplicate the rest of columns at the corresponding row with the (each) value.

    Arguments
    ---------
    df : pd.DataFrame
        Pandas dataframe that contains a column with list values

    column : str
        The name of the column that you wish to flatten

    Returns
    -------
    flattenedDF : pd.DataFrame
        Flattened pandas dataframe
    """
    columnFlat = pd.DataFrame(
        [
            [i, cFlattened]
            for i, y in df[column].apply(list).iteritems()
            for cFlattened in y
        ],
        columns=["I", column],
    )
    columnFlat = columnFlat.set_index("I")
    return df.drop(column, 1).merge(columnFlat, left_index=True, right_index=True)


def convertWellToBiomekNumber(well):
    """Convert a well to a number

    Arguments
    ---------
    well : str or int
        A well. If it is a int datatype, assume it is
        a correct biomek number. If it is a string
        datatype, assume it is a well of form "A03".

    Returns
    -------
    number : int
        Biomek number identification of well
    """
    if well.isdigit():
        biomekNumber = well
    elif isinstance(well, str):
        biomekMap = {
            well: number + 1
            for number, well in enumerate(
                [
                    f"{row}{column}"
                    for row, column in itertools.product("ABCDEFGH", range(1, 13))
                ]
            )
        }
        biomekNumber = biomekMap[convert3WellTo2Well(well)]
    else:
        raise TypeError(f"{well} is not in correct format")
    return biomekNumber


def generateConsolidationInstructions(consolidatedWorksheet):
    """Make biomek and human instructions for consolidated PCR rxns

    Arguments
    ---------
    consolidatedWorksheet : pd.DataFrame
        PCR Worksheet that contains consolidated PCR rxns
        from multiple trials. Needs to have the following columns:
        GOOD, trial, src_plate, src_well, OUTPUT_PLATE, and
        OUTPUT_WELL

    Returns
    -------
    humanInstructions : pd.DataFrame
        CSV containing information needed by human to
        consolidate PCR rxns

    plateMap : pd.DataFrame
        CSV containing information needed to convert
        human-readable plate names to Biomek plate names

    robotInstructions : pd.DataFrame
        CSV containing information needed by Biomek to
        consolidate PCR rxns
    """
    # Collecting information about consolidation for instructions
    consolidatedWorksheet = consolidatedWorksheet.loc[
        consolidatedWorksheet["GOOD"]
    ].copy()
    consolidatedWorksheet["trial_src_plate"] = (
        consolidatedWorksheet["trial"] + "#" + consolidatedWorksheet["src_plate"]
    )
    numberOfSrcPlates = int(consolidatedWorksheet["trial_src_plate"].unique().size)
    numberOfDestPlates = int(consolidatedWorksheet["OUTPUT_PLATE"].unique().size)
    numberOfSamples = int(sum(consolidatedWorksheet["GOOD"]))
    volumeToMove = 50  # uL

    # Preparing human readable csv instructions
    templateDF = pd.DataFrame(
        {
            "variable_name": [
                "src_plt_num",
                "dest_plt_num",
                "sample_num",
            ],
            "value": [
                numberOfSrcPlates,
                numberOfDestPlates,
                numberOfSamples,
            ],
        }
    )
    templateDF = pd.concat(
        [
            templateDF,
            consolidatedWorksheet["trial_src_plate"],
            consolidatedWorksheet["src_well"],
            consolidatedWorksheet["OUTPUT_PLATE"],
            consolidatedWorksheet["OUTPUT_WELL"],
        ],
        axis=1,
    )
    templateDF["vol"] = volumeToMove
    templateDF = templateDF.rename(
        columns={
            "trial_src_plate": "src_plt",
            "src_well": "src_well",
            "OUTPUT_PLATE": "dest_plt",
            "OUTPUT_WELL": "dest_well",
        }
    ).reset_index(drop=True)

    # Preparing plate map csv
    srcPlates = np.sort(templateDF["src_plt"].unique())
    destPlates = np.sort(templateDF["dest_plt"].unique())
    srcMap = [(f"src_{i+1}", srcPlate) for i, srcPlate in enumerate(srcPlates)]
    destMap = [(f"dest_{i+1}", destPlate) for i, destPlate in enumerate(destPlates)]
    plateMaps = pd.DataFrame(srcMap + destMap, columns=["biomek_name", "plate_name"])

    # Making biomek readable csv instructions
    biomekInstructions = templateDF.copy()
    for i, plate in enumerate(plateMaps["plate_name"]):
        biomekInstructions = biomekInstructions.replace(
            plate, plateMaps["biomek_name"][i]
        )

    return templateDF, plateMaps, biomekInstructions


def subsequentWell(plateNumber, well, direction="row"):
    """Finds subsequent empty well

    Arguments
    ---------
    plateNumber : int
        Index of plate

    well : str
        Well location of well

    direction : str
        Can be either row or col. Determines orientation.

    Returns
    -------
    2-tuple
        plate name and well of following empty well

    Examples
    --------
    >>> subsequentWell(1, 'A4', direction='row')
    (1, 'A5')
    >>> subsequentWell(1, 'A4', direction='col')
    (1, 'B4')
    >>> subsequentWell(1, 'A12', direction='row')
    (1, 'B1')
    """
    rows = "ABCDEFGH"
    well = convert2WellTo3Well(well)
    if well == "H12":
        nextPlate = plateNumber + 1
        nextRow = "A"
        nextColumn = 1
    else:
        nextPlate = plateNumber
        row, column = well[0], int(well[1:])
        if direction == "row":
            if column == 12:
                nextRow = rows[rows.index(row) + 1]
                nextColumn = 1
            else:
                nextRow = row
                nextColumn = column + 1
        else:
            if row == "H":
                nextRow = "A"
                nextColumn = column + 1
            else:
                nextRow = rows[rows.index(row) + 1]
                nextColumn = column
    return (nextPlate, f"{nextRow}{nextColumn}")


def addControlToAssembly(control, assemblyDF):
    """Add control assembly reaction

    Arguments
    ---------
    control : pd.Series
        Row from assemblyPartsDF that contains part
        which can act as a control

    assemblyDF : pd.DataFrame
        cleanAssemblyInstructionsDF that will be modified
        in place to add control reaction

    Returns
    -------
    None
        The assemblyDF will be modified in place!
    """
    # Getting location where to put control
    assemblyMethod = (
        "SLIC/Gibson/CPEC"
        if not pd.isna(control["Overlap with Next (bps)"])
        else "Golden-gate"
    )
    assemblyDFSubset = assemblyDF.loc[
        assemblyDF["Assembly Method"] == assemblyMethod, :
    ]
    lastMethod, lastPlate, lastWell = assemblyDFSubset.iloc[-1][
        ["Assembly Method", "Destination Plate", "Destination Well"]
    ].values
    lastPlateNumber = int(lastPlate.split("_")[-1])
    nextPlateNumber, nextWell = subsequentWell(
        lastPlateNumber, lastWell, direction="row"
    )
    nextPlate = "_".join(lastPlate.split("_")[:-1] + [str(nextPlateNumber)])

    # Making a name for control row
    rowName = f'{control["Part(s)"]}_control'

    # Adding control to assembly if not already in
    if rowName not in assemblyDF.index:
        assemblyDF = assemblyDF.append(pd.Series(name=rowName))
        assemblyDF.loc[rowName, "Part(s)"] = control["Part(s)"]
        assemblyDF.loc[rowName, "Part(s) ID"] = control["ID Number"]
        assemblyDF.loc[rowName, "Part(s) Source Plate"] = control[
            "FIRST_PART_SOURCE_PLATE"
        ]
        assemblyDF.loc[rowName, "Part(s) Well"] = control["FIRST_PART_WELL"]
        assemblyDF.loc[
            rowName, "Complete Construct Name"
        ] = f'(-) {control["Part(s)"]} control'
        assemblyDF.loc[rowName, "Assembly Method"] = assemblyMethod
        assemblyDF.loc[rowName, "Destination Plate"] = nextPlate
        assemblyDF.loc[rowName, "Destination Well"] = nextWell
        assemblyDF.loc[rowName, "Parts Summary"] = control["Part(s)"]

    return assemblyDF


def water_transfer(assembly_df, mm_conc, final_assembly_volume):
    """Creates Echo instructions for adding water to assembly plates.

    Arguments
    ---------
    assembly: pd.Datafrane
        Dataframe corresponding to equimolar assembly Echo instructions.

    mm_conc : int
        User-defined concentration of Gibson Assembly Master Mix.

    final_assembly_volume : float
        User-defined reaction volume for all Gibson assemblies.

    Returns
    ---------
    assembly_water : pd.Dataframe
        Dataframe containing Echo instructions for assembly parts and water.
    """
    # Creating 'water' dataframe to take in data from the input dataframe
    water = pd.DataFrame(
        columns=(
            "Source Plate Name",
            "Source Well",
            "Destination Plate Name",
            "Destination Well",
            "Transfer Volume",
            "Parts Volume",
        ),
        index=assembly_df.index,
    )
    water["Source Plate Name"] = "water_plate_1"
    water["Destination Plate Name"] = assembly_df["Destination Plate Name"]
    wells = [""] * (len(assembly_df))
    aliquot = [0] * (len(assembly_df))
    i = 0
    j = 0
    destination = assembly_df["Destination Well"]
    volume = assembly_df["Transfer Volume"]
    # Filling a list of wells for unique assembly destinaiton wells, and
    # calculating volume of parts in those wells
    # List of wells is as long as the number of source wells, then reduced
    # to actual amount of destination wells later
    for i in range(len(assembly_df)):
        if destination[i] not in wells:
            wells[j] = destination[i]
            aliquot[j] = aliquot[j] + volume[i]
            j += 1
        else:
            wells[j] = "remove"
            j += 1
    # Adding unique destination wells to dataframe as wells for needing water
    # transfer
    # Also adding volumes of parts in those wells
    water["Destination Well"] = wells
    water["Parts Volume"] = aliquot
    # Determination of water to add to each destination well based on user
    # input, in units of nL
    water_for_assembly = (final_assembly_volume * 1000) / mm_conc
    water["Transfer Volume"] = water_for_assembly - water["Parts Volume"]
    i = 0
    deletion = water["Transfer Volume"].values.tolist()
    remove = []
    for i in range(len(water)):
        if deletion[i] == water_for_assembly:
            remove.append(i)
    # Removing wells with no water to be added, and temporary columns used
    # in water volume calculations
    water.drop(remove, inplace=True)
    water.drop(columns="Parts Volume", inplace=True)
    water_to_transfer = water["Transfer Volume"].values.tolist()
    # Reducing transfer volume to zero if parts volume greater than final
    # assembly volume
    for i in range(len(water_to_transfer)):
        if water_to_transfer[i] <= 0:
            water_to_transfer[i] = 0
    water["Transfer Volume"] = water_to_transfer
    # Calculating total volume of water to transfer to destination plate
    total_water = 0
    i = 0
    for i in range(len(water_to_transfer)):
        total_water = total_water + water_to_transfer[i]

    # Now determining how many wells are necessary to fill destination wells
    # with water
    # Assigning each water well 40 uL to use, assuming 65 uL start and end
    # is 20 uL
    class water_well:
        well_name = ""
        well_volume = 40000

    # water_wells = int((total_water//40000) + 1)
    water_wells = (total_water // 40000) + 1
    wells_to_add = []
    i = 0
    label = ""
    # Assigning of names to water wells necessary to fill destination wells
    while i <= water_wells:
        if i <= 23:
            label = "A"
        if i > 23 and i <= 47:
            label = "B"
        if i > 47 and i <= 71:
            label = "C"
        if i > 71 and i <= 95:
            label = "D"
        if i > 95 and i <= 119:
            label = "E"
        if i > 119 and i <= 143:
            label = "F"
        if i > 143 and i <= 167:
            label = "G"
        if i > 167 and i <= 191:
            label = "H"
        if i > 191 and i <= 215:
            label = "I"
        if i > 215 and i <= 239:
            label = "J"
        if i > 239 and i <= 263:
            label = "K"
        if i > 263 and i <= 287:
            label = "L"
        if i > 287 and i <= 311:
            label = "M"
        if i > 311 and i <= 335:
            label = "N"
        if i > 335 and i <= 359:
            label = "O"
        if i > 359 and i <= 383:
            label = "P"
        well_to_add_to_list = water_well()
        well_to_add_to_list.well_name = label + str(i + 1)
        wells_to_add.append(well_to_add_to_list)
        i += 1

    # Determination of how many destination wells a water source well can fill,
    # and what destination wells to fill per water source well
    class stopping:
        location = 0
        volume = 0
        error = "error"

    well_limit = 0
    when_to_stop = []
    i = 0
    for i in range(len(water_to_transfer)):
        well_limit = well_limit + water_to_transfer[i]
        if well_limit >= 30000:
            stop = stopping()
            stop.location = i
            stop.volume = well_limit
            when_to_stop.append(stop)
            well_limit = 0
        if well_limit >= 40000:
            stop = stopping()
            when_to_stop.append(stop.error)
            well_limit = 0
    last_entry = stopping()
    last_entry.location = len(water)
    i = 0
    j = 0
    wells_for_df = []
    recent_end = 0
    counter = 0
    for i in range(len(when_to_stop)):
        for j in range(recent_end, when_to_stop[i].location):
            wells_for_df.append(wells_to_add[i].well_name)
        recent_end = when_to_stop[i].location
        counter += 1
    for i in range(recent_end, last_entry.location):
        wells_for_df.append(wells_to_add[counter].well_name)
        if wells_to_add[counter].well_volume > 40000:
            wells_for_df[i] = "error"
    # Making file output
    water["Source Well"] = wells_for_df
    assembly_df.drop(columns="Conc (fmol/uL)", inplace=True)
    assembly_df.drop(columns="fmol Transferred", inplace=True)
    to_join = [assembly_df, water]
    assembly_water = pd.concat(to_join)
    assembly_water = assembly_water.reset_index(drop=True)
    return assembly_water


def tube_to_plate(clean_df, reaction):
    # Set up plate orders
    plt_let = "ABCDEFGH"
    plt_num = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    plt_96_number = list(range(1, 97, 1))
    plt_96_alphanum = []
    for char in plt_let:
        for i in plt_num:
            plt_96_alphanum.append(char + str(i))
    plt_loc = zip(plt_96_alphanum, plt_96_number)
    plt_dict = dict(plt_loc)

    # Prepare unique df
    user_df = pd.DataFrame(columns=("OUTPUT_PLATE", "OUTPUT_WELL"))
    if reaction == "dpni":
        user_df["OUTPUT_PLATE"] = clean_df["OUTPUT_PLATE"]
        user_df["OUTPUT_WELL"] = clean_df["OUTPUT_WELL"]
        dest_plt_list = [
            "assemblytoautomate_PCR_plate_1",
            "assemblytoautomate_PCR_plate_2",
            "assemblytoautomate_PCR_plate_3",
            "assemblytoautomate_PCR_plate_4",
        ]
    elif reaction == "assembly":
        user_df["OUTPUT_PLATE"] = clean_df["Destination Plate"]
        user_df["OUTPUT_WELL"] = clean_df["Destination Well"]
        dest_plt_list = [
            "gibson_plate_1",
            "gibson_plate_2",
            "gibson_plate_3",
            "gibson_plate_4",
        ]
    unique_df = pd.DataFrame(columns=("OUTPUT_PLATE", "OUTPUT_WELL"))
    unique_plate = []
    unique_wells = []
    for i in range(len(user_df)):
        if user_df["OUTPUT_WELL"][i] not in unique_wells:
            unique_plate.append(user_df["OUTPUT_PLATE"][i])
            unique_wells.append(user_df["OUTPUT_WELL"][i])
    unique_df["OUTPUT_PLATE"] = unique_plate
    unique_df["OUTPUT_WELL"] = unique_wells
    user_df = unique_df

    # Cleaning up the well names for biomek
    wells = pd.Series(user_df["OUTPUT_WELL"])
    element_list = []
    new_wells = []
    for element in wells:
        element_list = list(element)
        if element_list[1] == "0":
            element_list[1] = ""
        new_wells.append("".join(element_list))
    wells = pd.Series(new_wells)
    user_df["OUTPUT_WELL"] = wells

    # calculate dest_plt_num
    dest_plt_num = len(user_df["OUTPUT_PLATE"].unique())
    # calculate sample_num
    sample_num = len(user_df["OUTPUT_PLATE"])
    # create a df with dest_plt_num and and sample_num info
    var_df = pd.DataFrame(
        {
            "variable_name_0": ["dest_plt_num"],
            "value_0": [dest_plt_num],
            "variable_name_1": ["sample_num"],
            "value_1": [sample_num],
        }
    )
    dest_plates = list(user_df["OUTPUT_PLATE"].unique())
    user_keys = user_df["OUTPUT_WELL"]
    user_ID = []
    for user_key in user_keys:
        for key, value in plt_dict.items():
            if user_key == key:
                user_ID.append(value)
    user_df["ID"] = user_ID
    dest_1_ID = list(user_df["ID"][user_df["OUTPUT_PLATE"] == dest_plt_list[0]])
    dest_2_ID = list(user_df["ID"][user_df["OUTPUT_PLATE"] == dest_plt_list[1]])
    dest_3_ID = list(user_df["ID"][user_df["OUTPUT_PLATE"] == dest_plt_list[2]])
    dest_4_ID = list(user_df["ID"][user_df["OUTPUT_PLATE"] == dest_plt_list[3]])
    dest_ID = [dest_1_ID, dest_2_ID, dest_3_ID, dest_4_ID]
    dest_ID = [x for x in dest_ID if x != []]
    dest_df = pd.DataFrame({"dest_pos": dest_plates, "dest_well": dest_ID})
    dest_df["dest_well"] = dest_df["dest_well"].astype(str).str.replace("\[|\]|'", "")
    biomek_frames = [var_df, dest_df]
    biomek_df = pd.concat(biomek_frames, axis=1, join="outer")
    return biomek_df


@check_types()
def gather_construct_worksheet(
    assembly_worksheet: DataFrame[schemas.AssemblyWorksheetSchema],
) -> DataFrame[schemas.ConstructWorksheetSchema]:
    construct_worksheet = (
        assembly_worksheet.loc[
            :,
            [
                "Number",
                "Name",
                "Parts Summary",
                "Assembly Method",
                "Destination Plate",
                "Destination Well",
            ],
        ]
        .groupby("Number")
        .first()
        .reset_index()
        .rename(
            columns={
                "Number": "j5_construct_id",
                "Name": "name",
                "Parts Summary": "parts",
                "Assembly Method": "assembly_method",
                "Destination Plate": "src_plate",
                "Destination Well": "src_well",
            }
        )
    )
    return construct_worksheet
