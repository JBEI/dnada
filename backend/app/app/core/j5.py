import io
import json
import logging
from typing import Any, Dict, List, Optional

import pandas as pd
from pandera.typing import DataFrame
from pydantic import BaseModel, validator

from app import schemas
from app.core.dna_utils import translate_dna_to_aa

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def concatenate_dfs(
    dfs: List[pd.DataFrame],
    sorted_by: List[str],
    drop_duplicates_by: List[str],
    id_column_name: str = "ID Number",
) -> Optional[pd.DataFrame]:
    if not dfs:
        return None
    combined_df = (
        pd.concat(dfs)
        .drop_duplicates(subset=drop_duplicates_by)
        .sort_values(by=sorted_by)
        .reset_index(drop=True)
    )
    combined_df[id_column_name] = range(combined_df.shape[0])
    return combined_df


def make_assemblies_skinny(
    df: "DataFrame[schemas.MasterJ5Assemblies]",
) -> "DataFrame[schemas.MasterJ5SkinnyAssemblies]":
    skinnyAssemblyInstructions = pd.DataFrame()
    for i in range(int((df.shape[1] - 3) / 2)):
        tmp = (
            df.melt(
                id_vars=["Number", "Name", "Assembly Method"],
                value_vars=[f"Part(s).{i}"],
                value_name="Part Name",
            )
            .drop(columns=["variable"])
            .merge(
                df.melt(
                    id_vars=["Number", "Name", "Assembly Method"],
                    value_vars=[f"Assembly Piece ID Number.{i}"],
                    value_name="Part ID",
                ).drop(columns=["variable"]),
                on=["Number", "Name", "Assembly Method"],
            )
        )
        tmp["Part Order"] = i
        skinnyAssemblyInstructions = pd.concat(
            [skinnyAssemblyInstructions, tmp], ignore_index=True
        )
    skinnyAssemblyInstructions = (
        skinnyAssemblyInstructions.dropna()
        .sort_values(["Number", "Part Order"])
        .reset_index(drop=True)
    )
    return skinnyAssemblyInstructions


class MasterJ5(BaseModel):
    """J5 Combinatorial Design CSV"""

    header: Optional[str] = None
    raw_csv: Optional[str] = None
    direct_synthesis: "Optional[DataFrame[schemas.MasterJ5Synthesis]]" = None
    digests: "Optional[DataFrame[schemas.MasterJ5Digests]]" = None
    oligos: "Optional[DataFrame[schemas.MasterJ5Oligos]]" = None
    pcr_reactions: "Optional[DataFrame[schemas.MasterJ5PCRs]]" = None
    parts: "Optional[DataFrame[schemas.MasterJ5Parts]]" = None
    part_sources: "Optional[DataFrame[schemas.MasterJ5PartSources]]" = None
    assemblies: "Optional[DataFrame[schemas.MasterJ5Assemblies]]" = None
    skinny_assemblies: "Optional[DataFrame[schemas.MasterJ5SkinnyAssemblies]]" = None

    def add_digests(self, section_str: str) -> None:
        self.digests = schemas.MasterJ5Digests.validate(
            pd.read_csv(io.StringIO(section_str), skiprows=1)
        )

    def add_oligos(self, section_str: str) -> None:
        self.oligos = schemas.MasterJ5Oligos.validate(
            pd.read_csv(io.StringIO(section_str), skiprows=1)
        )

    def add_direct_synthesis(self, section_str: str) -> None:
        self.direct_synthesis = schemas.MasterJ5Synthesis.validate(
            pd.read_csv(io.StringIO(section_str), skiprows=1)
        )

    def add_part_sources(self, section_str: str) -> None:
        self.part_sources = schemas.MasterJ5PartSources.validate(
            pd.read_csv(io.StringIO(section_str), skiprows=2).assign(
                AA_Sequence=lambda df: df.Sequence.apply(translate_dna_to_aa)
            )
        )

    def add_pcr_reactions(self, section_str: str) -> None:
        df = pd.read_csv(io.StringIO(section_str), skiprows=1)
        df = df.rename(
            columns={
                "ID Number.1": "forward_primer_id",
                "Name": "forward_primer_name",
                "ID Number.2": "reverse_primer_id",
                "Name.1": "reverse_primer_name",
            }
        )
        self.pcr_reactions = schemas.MasterJ5PCRs.validate(df)

    def add_parts(self, section_str: str, method: str) -> None:
        df = pd.read_csv(io.StringIO(section_str), skiprows=1).assign(Method=method)
        if self.parts is None:
            self.parts = schemas.MasterJ5Parts.validate(df)
        else:
            self.parts = schemas.MasterJ5Parts.validate(self.parts.append(df))

    def add_assemblies(self, section_str: str) -> None:
        df = pd.read_csv(io.StringIO(section_str), skiprows=2)
        df = df.rename(
            columns={
                "Part(s)": "Part(s).0",
                "Assembly Piece ID Number": "Assembly Piece ID Number.0",
            }
        )
        self.assemblies = schemas.MasterJ5Assemblies.validate(df)

        self.skinny_assemblies = schemas.MasterJ5SkinnyAssemblies.validate(
            make_assemblies_skinny(self.assemblies)
        )

    @classmethod
    def parse_csv(cls, master_j5_csv: str) -> "MasterJ5":
        """Parse original combinatorial.csv file into MasterJ5 object"""
        logging.debug("Beginning to parse J5 combinatorial csv")
        section_strs: List[str] = [
            section.strip() for section in master_j5_csv.split("\n\n")
        ]
        if not section_strs:
            raise KeyError("There wasn't a single section found in the master_j5 file")

        master_j5: MasterJ5 = cls()

        master_j5.raw_csv = master_j5_csv
        master_j5.header = section_strs[0]
        for section_str in section_strs[1:]:
            if section_str.startswith('"Digest Linearized Pieces'):
                master_j5.add_digests(section_str)
            elif section_str.startswith('"Non-degenerate Part IDs and Sources'):
                master_j5.add_part_sources(section_str)
            elif section_str.startswith('"Direct Synthesis'):
                master_j5.add_direct_synthesis(section_str)
            elif section_str.startswith('"Oligo Synthesis'):
                master_j5.add_oligos(section_str)
            elif section_str.startswith('"PCR Reactions'):
                master_j5.add_pcr_reactions(section_str)
            elif section_str.startswith('"Assembly Pieces (SLIC/Gibson/CPEC)'):
                master_j5.add_parts(section_str, method="SLIC/Gibson/CPEC")
            elif section_str.startswith('"Assembly Pieces (Golden-gate)'):
                master_j5.add_parts(section_str, method="Golden-gate")
            elif section_str.startswith('"Combinations of Assembly Pieces'):
                master_j5.add_assemblies(section_str)
            elif section_str.startswith(
                '"Suggested Assembly Piece Contigs For Hierarchical Assembly'  # noqa: E501
            ):
                pass
            elif section_str.startswith('"Assembly Parameters'):
                pass
            elif section_str.startswith('"Note'):
                pass
            elif section_str.startswith('"Combinatorial overhang/overlap design:'):
                pass
            elif section_str.startswith(
                '"Target Bin Selected Relative Overlap Positions and Extra'
            ):
                pass
            elif section_str.startswith(
                '"Target Bin Selected Relative Overhang Positions'
            ):
                pass
            else:
                unexpected_title = section_str.split("\n")[0]
                raise KeyError(
                    f'Unexpected section with title "{unexpected_title}" : {section_str}'
                )
        logging.debug("Finished parsing J5 combinatorial csv")
        return master_j5

    @classmethod
    def condense_designs(cls, individual_designs: List["MasterJ5"]) -> "MasterJ5":
        """Condense multiple MasterJ5 designs into single MasterJ5"""
        master_j5: MasterJ5 = cls()

        master_j5.header = "\n".join(
            str(design.header) for design in individual_designs
        )
        master_j5.raw_csv = "\n".join(
            str(design.raw_csv) for design in individual_designs
        )

        combined_digests: Optional[pd.DataFrame] = concatenate_dfs(
            [
                design.digests
                for design in individual_designs
                if design.digests is not None
            ],
            sorted_by=["Sequence Source"],
            drop_duplicates_by=["Sequence"],
        )
        master_j5.digests = (
            schemas.MasterJ5Digests.validate(combined_digests)
            if combined_digests is not None
            else None
        )
        combined_part_sources: Optional[pd.DataFrame] = concatenate_dfs(
            [
                design.part_sources
                for design in individual_designs
                if design.part_sources is not None
            ],
            sorted_by=["Name"],
            drop_duplicates_by=["Sequence"],
        )
        master_j5.part_sources = (
            schemas.MasterJ5PartSources.validate(combined_part_sources)
            if combined_part_sources is not None
            else None
        )
        combined_synthesis: Optional[pd.DataFrame] = concatenate_dfs(
            [
                design.direct_synthesis
                for design in individual_designs
                if design.direct_synthesis is not None
            ],
            sorted_by=["Name"],
            drop_duplicates_by=["Sequence"],
        )
        master_j5.direct_synthesis = (
            schemas.MasterJ5Synthesis.validate(combined_synthesis)
            if combined_synthesis is not None
            else None
        )
        combined_oligos: Optional[pd.DataFrame] = concatenate_dfs(
            [
                design.oligos
                for design in individual_designs
                if design.oligos is not None
            ],
            sorted_by=["Name"],
            drop_duplicates_by=["Sequence"],
        )
        master_j5.oligos = (
            schemas.MasterJ5Oligos.validate(combined_oligos)
            if combined_oligos is not None
            else None
        )
        combined_pcrs: Optional[pd.DataFrame] = concatenate_dfs(
            [
                design.pcr_reactions
                for design in individual_designs
                if design.pcr_reactions is not None
            ],
            sorted_by=["forward_primer_name", "reverse_primer_name"],
            drop_duplicates_by=[
                "forward_primer_name",
                "reverse_primer_name",
                "Sequence",
            ],
        )
        if combined_pcrs is not None and master_j5.oligos is not None:
            combined_pcrs = (
                combined_pcrs.merge(
                    right=master_j5.oligos[["ID Number", "Name"]].rename(
                        columns={
                            "ID Number": "forward_primer_id",
                            "Name": "forward_primer_name",
                        }
                    ),
                    how="left",
                    on=["forward_primer_name"],
                )
                .merge(
                    right=master_j5.oligos[["ID Number", "Name"]].rename(
                        columns={
                            "ID Number": "reverse_primer_id",
                            "Name": "reverse_primer_name",
                        }
                    ),
                    how="left",
                    on=["reverse_primer_name"],
                )
                .assign(
                    forward_primer_id=(
                        lambda df: df.forward_primer_id_y.fillna(df.forward_primer_id_x)
                    ),
                    reverse_primer_id=(
                        lambda df: df.reverse_primer_id_y.fillna(df.reverse_primer_id_x)
                    ),
                )
                .drop(
                    columns=[
                        "forward_primer_id_x",
                        "forward_primer_id_y",
                        "reverse_primer_id_x",
                        "reverse_primer_id_y",
                    ]
                )[
                    [
                        "ID Number",
                        "Primary Template",
                        "Alternate Template",
                        "forward_primer_id",
                        "forward_primer_name",
                        "reverse_primer_id",
                        "reverse_primer_name",
                        "Note",
                        "Mean Oligo Tm",
                        "Delta Oligo Tm",
                        "Mean Oligo Tm (3' only)",
                        "Delta Oligo Tm (3' only)",
                        "Length",
                        "Sequence",
                    ]
                ]
            )
        master_j5.pcr_reactions = (
            schemas.MasterJ5PCRs.validate(combined_pcrs)
            if combined_pcrs is not None
            else None
        )

        updated_design_parts: List[DataFrame[schemas.MasterJ5Parts]] = []
        for design_parts in [
            design.parts for design in individual_designs if design.parts is not None
        ]:
            new_design_parts = design_parts.copy()
            if master_j5.pcr_reactions is not None:
                new_design_parts = (
                    new_design_parts.merge(
                        right=master_j5.pcr_reactions[["ID Number", "Sequence"]].rename(
                            columns={
                                "ID Number": "Type ID Number",
                            }
                        ),
                        how="left",
                        on=["Sequence"],
                    )
                    .assign(
                        **{
                            "Type ID Number": lambda df: df["Type ID Number_y"].fillna(
                                df["Type ID Number_x"]
                            )
                        }
                    )
                    .drop(
                        columns=[
                            "Type ID Number_x",
                            "Type ID Number_y",
                        ]
                    )
                )
            if master_j5.digests is not None:
                new_design_parts = (
                    new_design_parts.merge(
                        right=master_j5.digests[["ID Number", "Sequence"]].rename(
                            columns={
                                "ID Number": "Type ID Number",
                            }
                        ),
                        how="left",
                        on=["Sequence"],
                    )
                    .assign(
                        **{
                            "Type ID Number": lambda df: df["Type ID Number_y"].fillna(
                                df["Type ID Number_x"]
                            )
                        }
                    )
                    .drop(
                        columns=[
                            "Type ID Number_x",
                            "Type ID Number_y",
                        ]
                    )
                )
            updated_design_parts.append(new_design_parts)
        combined_parts: Optional[pd.DataFrame] = concatenate_dfs(
            updated_design_parts,
            sorted_by=["Type", "Type ID Number"],
            drop_duplicates_by=["Sequence"],
        )
        master_j5.parts = (
            schemas.MasterJ5Parts.validate(combined_parts)
            if combined_parts is not None
            else None
        )

        # Get mapping from old part ID to new part ID
        part_id_mappings: List[pd.DataFrame] = []
        for updated_design_part in updated_design_parts:
            if master_j5.parts is not None:
                # updated_design_part has original ID Number with updated
                # Type ID Number
                # master_j5.parts has updated ID Number
                # and updated Type ID Number
                # Merge to get mapping from original ID Number to
                # updated ID Number
                part_id_mapping = (
                    updated_design_part[["ID Number", "Type", "Type ID Number"]]
                    .merge(
                        right=master_j5.parts[
                            ["ID Number", "Type", "Type ID Number"]
                        ].rename(columns={"ID Number": "New ID Number"}),
                        how="left",
                        on=["Type", "Type ID Number"],
                    )[["ID Number", "New ID Number"]]
                    .astype(pd.Int64Dtype())
                )
                part_id_mappings.append(part_id_mapping)

        updated_design_assemblies: List[DataFrame[schemas.MasterJ5Assemblies]] = []
        for i, design_assemblies in enumerate(
            [
                design.assemblies
                for design in individual_designs
                if design.assemblies is not None
            ]
        ):
            if master_j5.parts is not None:
                updated_design_assembly = design_assemblies.copy()
                for j in range(int((design_assemblies.shape[1] - 3) / 2)):
                    name_of_column_to_update = f"Assembly Piece ID Number.{j}"
                    updated_design_assembly[
                        name_of_column_to_update
                    ] = updated_design_assembly.merge(
                        right=part_id_mappings[i].rename(
                            columns={
                                "ID Number": name_of_column_to_update,
                            }
                        ),
                        how="left",
                        on=name_of_column_to_update,
                    )[
                        "New ID Number"
                    ]
                updated_design_assemblies.append(updated_design_assembly)
        combined_assemblies: Optional[pd.DataFrame] = concatenate_dfs(
            updated_design_assemblies,
            sorted_by=["Name"],
            drop_duplicates_by=["Name"],
            id_column_name="Number",
        )
        master_j5.assemblies = (
            schemas.MasterJ5Assemblies.validate(combined_assemblies)
            if combined_assemblies is not None
            else None
        )
        master_j5.skinny_assemblies = (
            schemas.MasterJ5SkinnyAssemblies.validate(
                make_assemblies_skinny(master_j5.assemblies)
            )
            if master_j5.assemblies is not None
            else None
        )

        return master_j5

    @classmethod
    def parse_json(cls, master_j5_json: str) -> "MasterJ5":
        """Parse MasterJ5.to_json() serialization into MasterJ5 object"""
        master_j5_dict: Dict[str, Any] = json.loads(master_j5_json)

        master_j5: MasterJ5 = cls()

        master_j5.header = master_j5_dict["header"]
        master_j5.digests = pd.read_json(master_j5_dict["digests"])
        master_j5.part_sources = pd.read_json(master_j5_dict["part_sources"])
        master_j5.direct_synthesis = pd.read_json(master_j5_dict["direct_synthesis"])
        master_j5.oligos = pd.read_json(master_j5_dict["oligos"])
        master_j5.pcr_reactions = pd.read_json(master_j5_dict["pcr_reactions"])
        master_j5.parts = pd.read_json(master_j5_dict["parts"])
        master_j5.assemblies = pd.read_json(master_j5_dict["assemblies"])
        master_j5.skinny_assemblies = pd.read_json(master_j5_dict["skinny_assemblies"])

        return master_j5

    def to_json(self) -> str:
        """Serialize MasterJ5 object into json"""
        return json.dumps(
            {
                "header": self.header,
                "digests": (
                    self.digests.to_json() if self.digests is not None else None
                ),
                "part_sources": (
                    self.part_sources.to_json()
                    if self.part_sources is not None
                    else None
                ),
                "direct_synthesis": (
                    self.direct_synthesis.to_json()
                    if self.direct_synthesis is not None
                    else None
                ),
                "oligos": (self.oligos.to_json() if self.oligos is not None else None),
                "pcr_reactions": (
                    self.pcr_reactions.to_json()
                    if self.pcr_reactions is not None
                    else None
                ),
                "parts": (self.parts.to_json() if self.parts is not None else None),
                "assemblies": (
                    self.assemblies.to_json() if self.assemblies is not None else None
                ),
                "skinny_assemblies": (
                    self.skinny_assemblies.to_json()
                    if self.skinny_assemblies is not None
                    else None
                ),
            },
            indent=4,
        )

    def to_file(self, filename: Optional[str] = None) -> str:
        contents: str = "\n\n".join(
            str(a)
            for a in [
                self.header,
                self.part_sources.to_csv(index=False)
                if self.part_sources is not None
                else None,
                self.digests.to_csv(index=False) if self.digests is not None else None,
                self.direct_synthesis.to_csv(index=False)
                if self.direct_synthesis is not None
                else None,
                self.oligos.to_csv(index=False) if self.oligos is not None else None,
                self.pcr_reactions.to_csv(index=False)
                if self.pcr_reactions is not None
                else None,
                self.parts.to_csv(index=False) if self.parts is not None else None,
                self.assemblies.to_csv(index=False)
                if self.assemblies is not None
                else None,
                self.skinny_assemblies.to_csv(index=False)
                if self.skinny_assemblies is not None
                else None,
            ]
        )
        if filename:
            with open(filename, "w") as F:
                F.write(contents)
        return contents

    class config:
        json_encoders = {
            pd.DataFrame: lambda v: v.to_json(),
        }


class File(BaseModel):
    filename: str
    contents: str


class PlasmidMap(File):
    pass


class PlasmidDesign(File):
    pass


class J5Design(BaseModel):
    zip_file_name: str
    master_j5: MasterJ5
    plasmid_maps: List[PlasmidMap]
    plasmid_designs: List[PlasmidDesign]

    @validator("plasmid_maps")
    def plasmid_names_must_be_unique(cls, v: List[PlasmidMap]) -> List[PlasmidMap]:
        plasmid_names = [plasmid.filename for plasmid in v]
        if len(plasmid_names) != len(set(plasmid_names)):
            raise ValueError("Plasmid names must be unique")
        return v

    def to_json(self) -> str:
        return json.dumps(
            {
                "zip_file_name": self.zip_file_name,
                "master_j5": self.master_j5.to_json(),
                "plasmid_maps": [p.json() for p in self.plasmid_maps],
                "plasmid_designs": [p.json() for p in self.plasmid_designs],
            }
        )
