#!/usr/bin/env python3

from datetime import datetime

from pytz import timezone, utc


def timestamp() -> str:
    date = datetime.now(tz=utc).astimezone(timezone("US/Pacific"))
    return date.strftime("%m/%d/%Y %H:%M:%S")


def today() -> str:
    date = datetime.now(tz=utc).astimezone(timezone("US/Pacific"))
    return date.strftime("%Y%m%d")


if __name__ == "__main__":
    print(timestamp())
