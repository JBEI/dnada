#!/usr/bin/env python3


import datetime
import io
import itertools
from typing import List

import pandas as pd


def condense_plate_reader_data(
    plate_reader_file: io.StringIO,
    plate_map_file: io.StringIO,
    start_date: datetime.date,
) -> str:
    results_file: str = ""
    plate_map_data: pd.DataFrame = pd.read_csv(plate_map_file)
    plate_reader_data: pd.DataFrame = pd.read_csv(plate_reader_file)
    if plate_reader_data.shape[1] <= 5:
        plate_reader_file.seek(0)
        plate_reader_data = pd.read_csv(plate_reader_file, sep="\t")
    plate_reader_data = plate_reader_data.rename(columns={"Sample_ID": "Sample ID"})
    possible_columns: List[str] = ["Time", "Sample ID", "Plate"] + [
        f"{row}{column}" for row, column in itertools.product("ABCDEFGH", range(1, 13))
    ]
    columns_to_drop: List[str] = [
        column for column in plate_reader_data.columns if column not in possible_columns
    ]
    plate_reader_data = plate_reader_data.drop(columns=columns_to_drop)
    results_df: pd.DataFrame = plate_reader_data.melt(
        id_vars="Time", var_name="Well", value_name="OD600"
    ).merge(plate_map_data, how="left", on="Well")
    results_df["Time"] = results_df["Time"].apply(
        lambda timepoint: process_plate_reader_time(
            timepoint=timepoint,
            start_time=datetime.datetime(
                year=start_date.year,
                month=start_date.month,
                day=start_date.day,
            ),
        )
    )
    results_file = results_df.to_csv(index=False, date_format="%Y-%m-%d %I:%M:%S %p")
    return results_file


def process_plate_reader_time(
    timepoint: str, start_time: datetime.datetime
) -> pd.Timestamp:
    """
    Parses time in format:
    H:MM:SS
    1:00:00
    1:10:00
    ...
    23:50:00

    or

    d.HH:MM:SS
    1.00:00:00
    1.00:10:00

    into
    pd.Timedelta
    2 days 01:30:00

    then into
    pd.Datetime
    YYYY-MM-DD HH:MM:SS AM/PM
    """

    fixed_timepoint: str = (
        f'{int(timepoint.split(".")[0])} days {timepoint.split(".")[1]}'
        if len(timepoint.split(".")) == 2
        else "0 days {}".format(
            ":".join(f"{int(unit):02d}" for unit in timepoint.split(":"))
        )
    )
    parsed_time: pd.Timedelta = pd.to_timedelta(fixed_timepoint)
    datetime_time: pd.Timestamp = start_time + parsed_time
    return datetime_time
