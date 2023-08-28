#!/usr/bin/env python3

import io

import pandas as pd


def pandas_read_sql(query, db):
    """Read SQL into DataFrame

    Notes
    -----
    From: "https://towardsdatascience.com/optimizing-pandas-read
    -sql-for-postgres-f31cd7f707ab"
    Copies query to StringIO before reading into Pandas
    Postgres specific method
    """
    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
        query=query, head="HEADER"
    )
    conn = db.raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    return pd.read_csv(store)
