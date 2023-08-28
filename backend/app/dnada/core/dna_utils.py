#!/usr/bin/env python3

from Bio.Seq import Seq


def translate_dna_to_aa(dna: str) -> str:
    if len(dna) % 3 != 0:
        return ""
    return str(Seq(dna).translate())
