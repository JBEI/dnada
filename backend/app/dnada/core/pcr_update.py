#!/usr/bin/env python3
# coding: utf-8

import json
import logging
import time
from datetime import timedelta
from itertools import product
from math import ceil
from typing import Any, Generator, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import requests
from k_means_constrained import KMeansConstrained
from pandera import check_types
from pandera.typing import DataFrame

from dnada import schemas

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def chunker(seq: Sequence[Any], size: int) -> Generator[Sequence[Any], None, None]:
    """Group an iterable into chunks
    Found at: https://stackoverflow.com/a/434328

    Examples
    --------
    >>> list(chunker('ABCDEFG', 3))
    ['ABC', 'DEF', 'G']
    >>> list(chunker([[1],[2],[3],[4],[5],[6],[7],[8],[9]], 4))
    [[[1], [2], [3], [4]], [[5], [6], [7], [8]], [[9]]]
    """
    return (
        seq[pos : pos + size] for pos in range(0, len(seq), size)  # noqa: ignore E203
    )


def call_neb_tm_api(
    primer_sequences: List[List[str]],
) -> pd.DataFrame:  # concentration or prodcode variable?
    successful: bool = False
    tries: int = 1
    while tries <= 3:
        p_data = {
            "seqpairs": primer_sequences,
            "conc": 0.5,
            "prodcode": "q5-0",
            "email": "no-reply@lbl.gov",
        }
        tm_response = requests.post(
            "https://tmapi.neb.com/tm/batch",
            data=json.dumps(p_data),
            headers={"content-type": "application/json"},
        )
        if tm_response.ok:
            tm_oligos = pd.DataFrame(tm_response.json()["data"])
            successful = True
            break
        elif (
            tm_response.status_code == 413
        ):  # PayloadTooLargeError: request entity too large
            logging.debug("Calling NEB API in chunks")
            tm_oligos = pd.concat(
                [
                    call_neb_tm_api(subset)  # type: ignore
                    for subset in chunker(primer_sequences, 100)
                ]
            )
            successful = True
            break
        else:
            logging.debug(f"Try #{tries} failed to call NEB API")
            time.sleep(3)
            tries += 1
    if not successful:
        raise ValueError(
            f"Could not call NEB API: {tm_response.status_code} "
            f": {tm_response.text}"
        )
    return tm_oligos


def run_kmeans_constrained(
    tm_mean: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate optimal zone temperatures

    Notes
    -----
    Post processing is performed in order to obtain sorted zone labels
    based on temperature. For example,
    cluster_centers may look like:
        array([[72.        ],
                [54.        ],
                [71.71428571],
                [64.2       ],
                [66.2       ],
                [72.        ],
                [67.        ],
                [72.        ],
                [72.        ],
                [72.        ],
                [72.        ],
                [72.        ]])
    cluster_labels will look like:
        {
            0: 72.0,
            1: 54.0,
            2: 71.71428571428571,
            3: 64.2,
            4: 66.2,
            5: 72.0,
            6: 67.0,
            7: 72.0,
            8: 72.0,
            9: 72.0,
            10: 72.0,
            11: 72.0
        }
    cluster_ids will look like:
        {
            0: 5,
            1: 0,
            2: 4,
            3: 1,
            4: 2,
            5: 6,
            6: 3,
            7: 7,
            8: 8,
            9: 9,
            10: 10,
            11: 11}
    where each key is the kgroup label and each value is the
    physical zone id which can then be used to obtain each
    physical zone id temperature.
    """
    kcount = 6 * ((len(tm_mean) // 96) + 1)

    if len(tm_mean) < 6:
        cluster_centers = tm_mean.values
        labels = np.arange(len(tm_mean))
        return labels, cluster_centers
    elif len(tm_mean) < 16:
        size_max = None
    else:
        size_max = 16

    kgroups = KMeansConstrained(n_clusters=kcount, size_max=size_max).fit(tm_mean)

    labels = kgroups.labels_
    cluster_centers = kgroups.cluster_centers_

    return labels, cluster_centers


def get_zone_wells(ZoneID: int, n: int) -> List[str]:
    assert n >= 0 and n <= 16, "n must be between 0 and 16"
    return [
        f"{row}{col}"
        for col, row in list(product([ZoneID * 2 + 1, (ZoneID + 1) * 2], "ABCDEFGH"))
    ][:n]


@check_types()
def distribute_pcr(
    templates: DataFrame[schemas.TemplatesPlateSchema],
    oligos: DataFrame[schemas.OligosPlateSchema],
    oligosseq: DataFrame[schemas.OligosOrderSchema],
    pcrrxns: Optional[DataFrame[schemas.MasterJ5PCRs]],
    assemblies: DataFrame[schemas.AssemblyVolumeSchema],
    max_well_uses: int,
) -> Tuple[
    DataFrame[schemas.PCRInstructionsSchema],
    DataFrame[schemas.PCRThermocyclerSchema],
]:
    if pcrrxns is None:
        raise ValueError("Cannot distribute empty PCR rxns")
    oligos_with_sequence = oligos.merge(
        right=oligosseq[["Name", "Sequence"]],
        how="left",
        left_on="LIQUID TYPE",
        right_on="Name",
    )
    pcr_instructions_build = templates.merge(
        right=pcrrxns,
        how="right",
        left_on="LIQUID TYPE",
        right_on="Primary Template",
    ).rename(
        columns={
            "LIQUID TYPE": "TEMPLATE_NAME",
            "PLATE ID": "TEMPLATE_PLATE",
            "PLATE WELL": "TEMPLATE_WELL",
            "VOLUME (uL)": "TEMPLATE_VOLUME",
        }
    )
    pcr_instructions_build = oligos_with_sequence.merge(
        right=pcr_instructions_build,
        how="right",
        left_on="LIQUID TYPE",
        right_on="forward_primer_name",
    )
    pcr_instructions_build = oligos_with_sequence.merge(
        right=pcr_instructions_build,
        how="right",
        left_on="LIQUID TYPE",
        right_on="reverse_primer_name",
    )

    pcr_instructions_build = pcr_instructions_build.rename(
        columns={
            "LIQUID TYPE_x": "PRIMER2_NAME",
            "PLATE ID_x": "PRIMER2_PLATE",
            "PLATE WELL_x": "PRIMER2_WELL",
            "VOLUME (uL)_x": "PRIMER2_VOLUME",
            "LIQUID TYPE_y": "PRIMER1_NAME",
            "PLATE ID_y": "PRIMER1_PLATE",
            "PLATE WELL_y": "PRIMER1_WELL",
            "VOLUME (uL)_y": "PRIMER1_VOLUME",
            "Length": "EXPECTED_SIZE",
            "Sequence": "PRIMER2_SEQUENCE",
            "Sequence_x": "PRIMER1_SEQUENCE",
        }
    )
    pcr_instructions_build = pcr_instructions_build.loc[
        :,
        [
            "ID Number",
            "TEMPLATE_NAME",
            "TEMPLATE_PLATE",
            "TEMPLATE_WELL",
            "PRIMER1_NAME",
            "PRIMER1_PLATE",
            "PRIMER1_WELL",
            "PRIMER1_SEQUENCE",
            "PRIMER2_NAME",
            "PRIMER2_PLATE",
            "PRIMER2_WELL",
            "PRIMER2_SEQUENCE",
            "Mean Oligo Tm",
            "EXPECTED_SIZE",
        ],
    ]

    pcr_instructions_build["TEMPLATE_VOLUME"] = 100
    pcr_instructions_build["PRIMER1_VOLUME"] = 250
    pcr_instructions_build["PRIMER2_VOLUME"] = 250
    assemblies = assemblies.loc[
        (assemblies["TYPE"].isin(["PCR", "SOE", "Direct Synthesis/PCR"])),
        :,
    ]
    pcr_instructions_build = pcr_instructions_build.merge(
        right=assemblies,
        how="left",
        left_on="ID Number",
        right_on="TYPE_ID",
    )
    pcr_instructions_build["REACTION_NUMBER"] = pcr_instructions_build["ID Number"]

    pcr_instructions = pd.DataFrame(columns=pcr_instructions_build.columns)
    for row in pcr_instructions_build.index:
        for welluse in range(
            ceil(pcr_instructions_build.at[row, "NUMBER_OF_USES"] / max_well_uses)
        ):
            pcr_instructions = pd.concat(
                [pcr_instructions, pcr_instructions_build.iloc[[row]]]
            )

    tm_mean_df = call_neb_tm_api(
        primer_sequences=pcr_instructions.loc[
            :, ["PRIMER1_SEQUENCE", "PRIMER2_SEQUENCE"]
        ].values.tolist()
    )

    pcr_instructions = pcr_instructions.merge(
        tm_mean_df.loc[:, ["seq1", "seq2", "ta"]]
        .groupby(["seq1", "seq2"])
        .agg("first")
        .reset_index()
        .rename(columns={"ta": "Mean Oligo Tm (NEB)"}),
        how="left",
        left_on=["PRIMER1_SEQUENCE", "PRIMER2_SEQUENCE"],
        right_on=["seq1", "seq2"],
    )
    pcr_instructions["OPTIMAL_ANNEALING_TEMP"] = pcr_instructions["Mean Oligo Tm (NEB)"]

    labels, cluster_centers = run_kmeans_constrained(
        tm_mean=pcr_instructions["OPTIMAL_ANNEALING_TEMP"].to_frame()
    )

    cluster_labels = {i: t[0] for i, t in enumerate(cluster_centers)}
    cluster_ids = {
        label[0]: i
        for i, label in enumerate(
            sorted(cluster_labels.items(), key=lambda item: item[1])
        )
    }

    reaction_temperatures = cluster_centers[labels]
    reaction_labels = np.vectorize(lambda label: cluster_ids[label])(labels)

    pcr_instructions["THERMOCYCLER_ZONE_ANNEALING_TEMP"] = reaction_temperatures
    pcr_instructions["THERMOCYCLER_ZONE"] = reaction_labels
    pcr_instructions["THERMOCYCLER_ZONE_ID"] = pcr_instructions["THERMOCYCLER_ZONE"] % 6
    pcr_instructions = pcr_instructions.sort_values(
        by=["THERMOCYCLER_ZONE", "OPTIMAL_ANNEALING_TEMP", "ID Number"]
    ).reset_index(drop=True)

    pcr_instructions["THERMOCYCLER_BLOCK"] = pcr_instructions["THERMOCYCLER_ZONE"] // 6
    pcr_instructions["OUTPUT_PLATE"] = pcr_instructions["THERMOCYCLER_BLOCK"].apply(
        lambda block_id: f"pcr_plate_{block_id+1}"
    )

    pcr_instructions["OUTPUT_WELL"] = ""
    for block in pcr_instructions["THERMOCYCLER_BLOCK"].unique():
        for zone in pcr_instructions["THERMOCYCLER_ZONE_ID"].unique():
            n_samples = pcr_instructions.loc[
                (pcr_instructions["THERMOCYCLER_BLOCK"] == block)
                & (pcr_instructions["THERMOCYCLER_ZONE_ID"] == zone),
                "OUTPUT_WELL",
            ].shape[0]
            pcr_instructions.loc[
                (pcr_instructions["THERMOCYCLER_BLOCK"] == block)
                & (pcr_instructions["THERMOCYCLER_ZONE_ID"] == zone),
                "OUTPUT_WELL",
            ] = get_zone_wells(ZoneID=zone, n=n_samples)

    pcr_instructions = pcr_instructions.loc[
        :,
        [
            "REACTION_NUMBER",
            "TEMPLATE_NAME",
            "TEMPLATE_PLATE",
            "TEMPLATE_WELL",
            "TEMPLATE_VOLUME",
            "PRIMER1_NAME",
            "PRIMER1_PLATE",
            "PRIMER1_WELL",
            "PRIMER1_VOLUME",
            "PRIMER2_NAME",
            "PRIMER2_PLATE",
            "PRIMER2_WELL",
            "PRIMER2_VOLUME",
            "Mean Oligo Tm",
            "Mean Oligo Tm (NEB)",
            "OUTPUT_PLATE",
            "OUTPUT_WELL",
            "OPTIMAL_ANNEALING_TEMP",
            "THERMOCYCLER_BLOCK",
            "THERMOCYCLER_ZONE",
            "THERMOCYCLER_ZONE_ANNEALING_TEMP",
            "EXPECTED_SIZE",
        ],
    ]

    thermocycler = (
        pcr_instructions.loc[
            :,
            [
                "THERMOCYCLER_BLOCK",
                "THERMOCYCLER_ZONE",
                "THERMOCYCLER_ZONE_ANNEALING_TEMP",
                "OUTPUT_PLATE",
                "EXPECTED_SIZE",
            ],
        ]
        .groupby(
            [
                "THERMOCYCLER_BLOCK",
                "THERMOCYCLER_ZONE",
                "THERMOCYCLER_ZONE_ANNEALING_TEMP",
                "OUTPUT_PLATE",
            ]
        )
        .agg({"EXPECTED_SIZE": max})
        .reset_index()
        .rename(
            columns={
                "OUTPUT_PLATE": "BLOCK_NAME",
                "THERMOCYCLER_BLOCK": "BLOCK ID",
                "THERMOCYCLER_ZONE": "BLOCK ZONE",
                "EXPECTED_SIZE": "PLATE_LONGEST_PCR",
            }
        )
    )
    thermocycler["BLOCK ZONE"] = thermocycler["BLOCK ZONE"] % 6
    thermocycler["PLATE_EXTENSION_TIME"] = thermocycler["PLATE_LONGEST_PCR"].apply(
        lambda pcr_length: timedelta(seconds=int((pcr_length / 1000) * 30))
    )
    return (pcr_instructions, thermocycler)
