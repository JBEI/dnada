#!/usr/bin/env python3

import io
import zipfile
from datetime import datetime
from typing import Dict, Tuple

import pandas as pd

from app.api.utils.post_automation import create_plate_column, create_well_column
from app.core.echo import create_echo_instructions
from app.core.j5_to_echo_utils import stamp

# From:
# https://arep.med.harvard.edu/labgc/adnan/projects/Utilities/revcomp.html
COMPLEMENT_TABLE: Dict[int, str] = str.maketrans(
    {
        "A": "T",
        "T": "A",
        "G": "C",
        "C": "G",
        "M": "K",
        "K": "M",
        "B": "V",
        "V": "B",
        "D": "H",
        "H": "D",
        "U": "A",
        "N": "N",
    }
)


def reverse_complement(dna: str) -> str:
    return dna.translate(COMPLEMENT_TABLE)[::-1]


class PrimerWillNotAnneal(Exception):
    """Primer sequence not found in template"""


class PrimerAnnealsMultipleTimes(Exception):
    """Primer sequence found multiple times"""


def slice_plasmid(template: str, start: int, stop: int) -> str:
    """Slice circular plasmid"""
    if stop > start:
        return template[start:stop]
    else:
        return template[start:] + template[:stop]


def simulate_pcr(template: str, fwd_primer: str, rev_primer: str) -> Tuple[int, str]:
    """Calculates length of PCR"""
    template = template.upper()
    start: int = template.find(fwd_primer.upper())
    if start == -1:
        raise PrimerWillNotAnneal(f"Forward primer: {fwd_primer}")
    if template.find(fwd_primer.upper(), start + 1) != -1:
        raise PrimerAnnealsMultipleTimes(f"Forward primer: {fwd_primer}")
    stop: int = template.find(reverse_complement(rev_primer.upper()))
    if stop == -1:
        raise PrimerWillNotAnneal(f"Reverse primer: {rev_primer}")
    if template.find(rev_primer.upper(), stop + 1) != -1:
        raise PrimerAnnealsMultipleTimes(f"Reverse primer: {rev_primer}")
    pcr: str = slice_plasmid(
        template=template, start=start, stop=stop + len(rev_primer)
    )
    length: int = len(pcr)
    return length, pcr


def create_colony_pcr_instructions(
    glycerol_file: io.StringIO,
    plasmid_sequences_file: io.StringIO,
    forward_primer: str,
    reverse_primer: str,
    username: str,
    reaction_volume: int = 10,  # uL
) -> io.BytesIO:
    glycerol: pd.DataFrame = pd.read_csv(glycerol_file)
    sequences: pd.DataFrame = pd.read_csv(plasmid_sequences_file)

    # 10 uL reactions
    glycerol["NGS_PLATE"] = glycerol["GLYCEROL_PLATE"].apply(
        lambda plate: "{username} {plate_number} {date}".format(
            username=username,
            plate_number=int(plate.split("_")[-1]) // 4 + 1,
            date=datetime.today().strftime("%Y%m%d")[2:],
        )
    )
    glycerol["NGS_WELL"] = glycerol.apply(
        lambda row: stamp(
            row["GLYCEROL_WELL"],
            (int(row["GLYCEROL_PLATE"].split("_")[-1]) - 1) % 4,
        ),
        axis=1,
    )
    glycerol["NGS_VOLUME"] = 100
    glycerol["PRIMER1_SEQ"] = forward_primer
    glycerol["PRIMER1_PLATE"] = "colony_pcr_primer_plate"
    glycerol["PRIMER1_WELL"] = "O22"
    glycerol["PRIMER1_VOLUME"] = 4 * reaction_volume
    glycerol["PRIMER2_SEQ"] = reverse_primer
    glycerol["PRIMER2_PLATE"] = "colony_pcr_primer_plate"
    glycerol["PRIMER2_WELL"] = "O24"
    glycerol["PRIMER2_VOLUME"] = 4 * reaction_volume
    glycerol["PCR_LENGTH"] = glycerol["name"].apply(
        lambda plasmid: simulate_pcr(
            template=sequences.loc[sequences.Name == plasmid, "Bases"].values[0],
            fwd_primer=forward_primer,
            rev_primer=reverse_primer,
        )[0]
        if not pd.isna(plasmid)
        else 0
    )
    glycerol["COLONY_PCR_PLATE"] = create_plate_column(
        number=glycerol.shape[0],
        template="colony_pcr_plate_{}",
        plate_size=96,
    )
    glycerol["COLONY_PCR_WELL"] = create_well_column(
        number=glycerol.shape[0], plate_size=96, how="col"
    )
    colony_pcr_worksheet = glycerol
    colony_pcr_echo_instructions = create_echo_instructions(
        colony_pcr_worksheet, method="colony_pcr"
    )

    zip_results = io.BytesIO()
    with zipfile.ZipFile(zip_results, "w") as archive:
        archive.writestr(
            "colony_pcr/colony_pcr_worksheet.csv",
            colony_pcr_worksheet.to_csv(index=False),
        )
        archive.writestr(
            "colony_pcr/colony_pcr_echo_instructions.csv",
            colony_pcr_echo_instructions.to_csv(index=False),
        )
    zip_results.seek(0)
    return zip_results
