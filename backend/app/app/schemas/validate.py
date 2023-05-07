from typing import Dict, Optional, Type

import pandas as pd
import pandera as pa
import pandera.extensions as extensions
from pandera.typing import Series
from pydantic import BaseModel

ALLOWED_NUCLEOTIDES = set("ATCG")
ALLOWED_AMINO_ACIDS = set("RHKDESTNQCGPAVILMFYW*")


@extensions.register_check_method()
def is_dna_sequence(col: Series[str]) -> Series[bool]:
    """Check if string contains valid nucleotides
    Notes: https://stackoverflow.com/a/1323374
    """
    return col.str.upper().apply(set) <= ALLOWED_NUCLEOTIDES


@extensions.register_check_method()
def is_aa_sequence(col: Series[str]) -> Series[bool]:
    """Check if string contains valid amino acids
    Notes: https://stackoverflow.com/a/1323374
    """
    return col.str.upper().apply(set) <= ALLOWED_AMINO_ACIDS


class ValidationResponse(BaseModel):
    ok: bool
    text: str


class RegistryPlasmidSchema(pa.SchemaModel):
    Principal_Investigator: Series[str] = pa.Field(
        alias="Principal Investigator"
    )
    Principal_Investigator_Email: Series[str] = pa.Field(
        alias="Principal Investigator Email"
    )
    BioSafety_Level: Series[int] = pa.Field(
        alias="BioSafety Level", isin=[1, 2, 3]
    )
    Name: Series[str] = pa.Field()
    Alias: Series[str] = pa.Field(nullable=True)
    Keywords: Series[str] = pa.Field(nullable=True)
    Summary: Series[str] = pa.Field()
    Notes: Series[str] = pa.Field(nullable=True)
    References: Series[str] = pa.Field(nullable=True)
    Links: Series[str] = pa.Field(nullable=True)
    Status: Series[str] = pa.Field(
        isin=["Complete", "In Progress", "Abandoned", "Planned"]
    )
    Creator: Series[str] = pa.Field()
    Creator_Email: Series[str] = pa.Field(alias="Creator Email")
    Circular: Series[bool] = pa.Field()
    Promoters: Series[str] = pa.Field()
    Replicates_In: Series[str] = pa.Field(alias="Replicates In")
    Selection_Markers: Series[str] = pa.Field(alias="Selection Markers")
    Plasmid_Use: Series[str] = pa.Field(
        alias="Plasmid Use",
        isin=[
            "Expression",
            "Cloning",
            "Synthetic Biology",
            "CRISPR",
            "RNAi",
            "Other",
        ],
    )
    Intellectual_Property: Series[str] = pa.Field(
        alias="Intellectual Property"
    )
    Origin_of_Replication: Series[str] = pa.Field(
        alias="Origin of Replication"
    )
    Backbone: Series[str] = pa.Field()
    Sequence_File: Series[str] = pa.Field(alias="Sequence File")

    class Config:
        strict = False
        coerce = True


class PeakTableSchema(pa.SchemaModel):
    Well: Series[str] = pa.Field()
    Sample_ID: Series[str] = pa.Field(alias="Sample ID")
    Peak_ID: Series[int] = pa.Field(alias="Peak ID", ge=1)
    Size: Series[int] = pa.Field(alias="Size (bp)")
    Percent_Conc: Series[float] = pa.Field(
        alias="% (Conc.) (ng/uL)", gt=0, nullable=True
    )
    nmole_per_L: Series[float] = pa.Field(alias="nmole/L", gt=0)
    ng_per_uL: Series[float] = pa.Field(alias="ng/ul", gt=0)
    RFU: Series[int] = pa.Field(gt=0)
    TIC: Series[float] = pa.Field(alias="TIC (ng/ul)", gt=0)
    TIM: Series[float] = pa.Field(alias="TIM (nmole/L)", gt=0)
    Total_Conc: Series[float] = pa.Field(alias="Total Conc. (ng/ul)", gt=0)
    DQN: Optional[Series[str]] = pa.Field(nullable=True)
    Threshold: Optional[Series[str]] = pa.Field(nullable=True)

    class Config:
        strict = False
        coerce = True


class RegistryWorksheetSchema(pa.SchemaModel):
    Name: Series[str] = pa.Field()
    Part_ID: Series[str] = pa.Field()

    class Config:
        strict = True
        coerce = True


class SynthsPlateSchema(pa.SchemaModel):
    PLATE_ID: Series[str] = pa.Field(alias="PLATE ID")
    PLATE_WELL: Series[str] = pa.Field(alias="PLATE WELL")
    LIQUID_TYPE: Series[str] = pa.Field(alias="LIQUID TYPE")
    VOLUME: Series[int] = pa.Field(alias="VOLUME (uL)", gt=0)
    SEQUENCE: Series[str] = pa.Field(is_dna_sequence=())

    class Config:
        strict = True
        coerce = True


class OligosPlateSchema(pa.SchemaModel):
    PLATE_ID: Series[str] = pa.Field(alias="PLATE ID")
    PLATE_WELL: Series[str] = pa.Field(alias="PLATE WELL")
    LIQUID_TYPE: Series[str] = pa.Field(alias="LIQUID TYPE")
    VOLUME: Series[int] = pa.Field(alias="VOLUME (uL)", gt=0)

    class Config:
        strict = True
        coerce = True


class OligosOrderSchema(pa.SchemaModel):
    Plate: Series[str] = pa.Field()
    Well_Position: Series[str] = pa.Field(alias="Well Position")
    Name: Series[str] = pa.Field()
    Sequence: Series[str] = pa.Field(is_dna_sequence=())
    Length: Series[int] = pa.Field(gt=0)

    class Config:
        strict = True
        coerce = True


class TemplatesPlateSchema(pa.SchemaModel):
    PLATE_ID: Series[str] = pa.Field(alias="PLATE ID")
    PLATE_WELL: Series[str] = pa.Field(alias="PLATE WELL")
    LIQUID_TYPE: Series[str] = pa.Field(alias="LIQUID TYPE")
    VOLUME: Series[int] = pa.Field(alias="VOLUME (uL)", gt=0)

    class Config:
        strict = True
        coerce = True


class EchoInstructionsSchema(pa.SchemaModel):
    Source_Plate_Name: Series[str] = pa.Field(alias="Source Plate Name")
    Source_Well: Series[str] = pa.Field(alias="Source Well")
    Destination_Plate_Name: Series[str] = pa.Field(
        alias="Destination Plate Name"
    )
    Destination_Well: Series[str] = pa.Field(alias="Destination Well")
    Transfer_Volume: Series[int] = pa.Field(alias="Transfer Volume", ge=0)

    class Config:
        strict = True
        coerce = True


class PCRInstructionsSchema(pa.SchemaModel):
    REACTION_NUMBER: Series[int] = pa.Field(ge=0)
    TEMPLATE_NAME: Series[str] = pa.Field()
    TEMPLATE_PLATE: Series[str] = pa.Field()
    TEMPLATE_WELL: Series[str] = pa.Field()
    TEMPLATE_VOLUME: Series[int] = pa.Field(ge=0)
    PRIMER1_NAME: Series[str] = pa.Field()
    PRIMER1_PLATE: Series[str] = pa.Field()
    PRIMER1_WELL: Series[str] = pa.Field()
    PRIMER1_VOLUME: Series[int] = pa.Field(ge=0)
    PRIMER2_NAME: Series[str] = pa.Field()
    PRIMER2_PLATE: Series[str] = pa.Field()
    PRIMER2_WELL: Series[str] = pa.Field()
    PRIMER2_VOLUME: Series[int] = pa.Field(ge=0)
    Mean_Oligo_Tm: Series[float] = pa.Field(alias="Mean Oligo Tm", gt=0)
    Mean_Oligo_Tm_NEB: Series[float] = pa.Field(
        alias="Mean Oligo Tm (NEB)", gt=0
    )
    OUTPUT_PLATE: Series[str] = pa.Field()
    OUTPUT_WELL: Series[str] = pa.Field()
    OPTIMAL_ANNEALING_TEMP: Series[float] = pa.Field(gt=0)
    THERMOCYCLER_BLOCK: Series[int] = pa.Field(ge=0)
    THERMOCYCLER_ZONE: Series[int] = pa.Field(ge=0)
    THERMOCYCLER_ZONE_ANNEALING_TEMP: Series[float] = pa.Field(gt=0)
    EXPECTED_SIZE: Series[int] = pa.Field(gt=0)

    class Config:
        strict = True
        coerce = True


class PCRWorksheetSchema(PCRInstructionsSchema):
    PARTS_SOURCE_PLATE: Series[str] = pa.Field()
    PARTS_WELL: Series[str] = pa.Field()
    ZAG_PLATE: Series[str] = pa.Field()
    ZAG_WELL: Series[str] = pa.Field()


class PCRThermocyclerSchema(pa.SchemaModel):
    BLOCK_ID: Series[str] = pa.Field(alias="BLOCK ID")
    BLOCK_ZONE: Series[str] = pa.Field(alias="BLOCK ZONE")
    BLOCK_ZONE_ANNEALING_TEMP: Series[str] = pa.Field()
    BLOCK_NAME: Series[str] = pa.Field()
    PLATE_LONGEST_PCR: Series[int] = pa.Field(gt=0)
    PLATE_EXTENSION_TIME: Series[str] = pa.Field()

    class Config:
        strict = True
        coerce = True


class DigestsPlateSchema(pa.SchemaModel):
    REACTION_NUMBER: Series[int] = pa.Field(ge=0)
    SEQUENCE_SOURCE: Series[str] = pa.Field()
    SEQUENCE_LENGTH: Series[int] = pa.Field(gt=0)
    DIGEST_SOURCE_PLATE: Series[str] = pa.Field()
    DIGEST_SOURCE_WELL: Series[str] = pa.Field()

    class Config:
        strict = True
        coerce = True


class DigestsWorksheetSchema(DigestsPlateSchema):
    PARTS_SOURCE_PLATE: Series[str] = pa.Field()
    PARTS_WELL: Series[str] = pa.Field()
    PART_TYPE: Series[str] = pa.Field(isin=["digest"])

    class Config:
        strict = True
        coerce = True


class PartsPlateSchema(pa.SchemaModel):
    PART_PLATE: Series[str] = pa.Field()
    PART_WELL: Series[str] = pa.Field()
    PART_ID: Series[int] = pa.Field(ge=0)
    PART_NAME: Series[str] = pa.Field()
    PART_LENGTH: Series[int] = pa.Field(gt=0)
    PART_TYPE: Series[str] = pa.Field(isin=["digest", "pcr"])
    SOURCE_ID: Series[int] = pa.Field()
    SOURCE_PLATE: Series[str] = pa.Field()
    SOURCE_WELL: Series[str] = pa.Field()

    class Config:
        strict = True
        coerce = True


class PartsWorksheetSchema(PartsPlateSchema):
    QUANT_PLATE: Series[str] = pa.Field()
    QUANT_WELL: Series[str] = pa.Field()
    QUANT_VOLUME: Series[int] = pa.Field(gt=0)
    CONCENTRATION: Series[float] = pa.Field(alias="Conc (ng/uL)", gt=0)


class ConstructWorksheetSchema(pa.SchemaModel):
    j5_construct_id: Series[int] = pa.Field(ge=0)
    name: Series[str] = pa.Field()
    parts: Series[str] = pa.Field()
    assembly_method: Series[str] = pa.Field(
        isin=["SLIC/Gibson/CPEC", "Golden-gate"]
    )
    src_plate: Series[str] = pa.Field()
    src_well: Series[str] = pa.Field()

    class Config:
        strict = True
        coerce = True


class PlatingInstructionsSchema(ConstructWorksheetSchema):
    QPLATE: Series[str] = pa.Field()
    QWELL: Series[str] = pa.Field()


class MasterJ5Digests(pa.SchemaModel):
    ID_Number: Series[int] = pa.Field(alias="ID Number", ge=0, unique=True)
    Sequence_Source: Series[str] = pa.Field(
        alias="Sequence Source", unique=True
    )
    Length: Series[int] = pa.Field(gt=0)
    Sequence: Series[str] = pa.Field(is_dna_sequence=())

    class Config:
        strict = True
        coerce = True


class MasterJ5Oligos(pa.SchemaModel):
    ID_Number: Series[int] = pa.Field(alias="ID Number", ge=0, unique=True)
    Name: Series[str] = pa.Field(unique=True)
    Length: Series[int] = pa.Field(gt=0)
    Tm: Series[int] = pa.Field(gt=0)
    Tm3: Series[float] = pa.Field(alias="Tm (3' only)", gt=0)
    Cost: Series[float] = pa.Field(ge=0)
    Sequence: Series[str] = pa.Field(is_dna_sequence=())
    Sequence3: Series[str] = pa.Field(
        alias="Sequence (3' only)", is_dna_sequence=()
    )

    class Config:
        strict = True
        coerce = True


class MasterJ5Synthesis(pa.SchemaModel):
    ID_Number: Series[int] = pa.Field(alias="ID Number", ge=0, unique=True)
    Name: Series[str] = pa.Field(unique=True)
    Length: Series[int] = pa.Field(gt=0)
    Cost: Series[float] = pa.Field(ge=0)
    Sequence: Series[str] = pa.Field(is_dna_sequence=())

    class Config:
        strict = True
        coerce = True


class MasterJ5PartSources(pa.SchemaModel):
    ID_Number: Series[int] = pa.Field(alias="ID Number", ge=0, unique=True)
    Name: Series[str] = pa.Field(unique=True)
    Source_Plasmid: Series[str] = pa.Field(alias="Source Plasmid")
    Reverse_Complement: Series[bool] = pa.Field(alias="Reverse Complement")
    Start: Series[int] = pa.Field(alias="Start (bp)", ge=1)
    End: Series[int] = pa.Field(alias="End (bp)")
    Size: Series[int] = pa.Field(alias="Size (bp)")
    Sequence: Series[str] = pa.Field(is_dna_sequence=())
    AA_Sequence: Series[str] = pa.Field(is_aa_sequence=())

    class Config:
        strict = True
        coerce = True


class MasterJ5PCRs(pa.SchemaModel):
    ID_Number: Series[int] = pa.Field(alias="ID Number", ge=0, unique=True)
    Primary_Template: Series[str] = pa.Field(alias="Primary Template")
    Alternate_Template: Series[str] = pa.Field(
        alias="Alternate Template", nullable=True
    )
    forward_primer_id: Series[int] = pa.Field(ge=0)
    forward_primer_name: Series[str] = pa.Field()
    reverse_primer_id: Series[int] = pa.Field(ge=0)
    reverse_primer_name: Series[str] = pa.Field()
    Note: Series[str] = pa.Field()
    Mean_Oligo_Tm: Series[float] = pa.Field(alias="Mean Oligo Tm", gt=0)
    Delta_Oligo_Tm: Series[float] = pa.Field(alias="Delta Oligo Tm", gt=0)
    Mean_Oligo_Tm3: Series[float] = pa.Field(
        alias="Mean Oligo Tm (3' only)", gt=0
    )
    Delta_Oligo_Tm3: Series[float] = pa.Field(
        alias="Delta Oligo Tm (3' only)", gt=0
    )
    Length: Series[int] = pa.Field(gt=0)
    Sequence: Series[str] = pa.Field(is_dna_sequence=())

    class Config:
        strict = True
        coerce = True


class MasterJ5Parts(pa.SchemaModel):
    ID_Number: Series[int] = pa.Field(alias="ID Number", ge=0, unique=True)
    Method: Series[str] = pa.Field(
        isin=["SLIC/Gibson/CPEC", "Golden-gate"]
    )
    Type: Series[str] = pa.Field(
        isin=["PCR", "SOE", "Digest Linearized", "Direct Synthesis/PCR"]
    )
    Type_ID_Number: Series[int] = pa.Field(alias="Type ID Number", ge=0)
    Name: Series[str] = pa.Field(alias="Part(s)")

    # Gibson Specific Columns
    Relative_Overlap_Position: Optional[Series[pd.Int64Dtype]] = pa.Field(
        alias="Relative Overlap Position", nullable=True
    )
    Extra_5_CPEC_bps: Optional[Series[pd.Int64Dtype]] = pa.Field(
        alias="Extra 5' CPEC bps", nullable=True
    )
    Extra_3_CPEC_bps: Optional[Series[pd.Int64Dtype]] = pa.Field(
        alias="Extra 3' CPEC bps", nullable=True
    )
    CPEC_Tm_Next: Optional[Series[float]] = pa.Field(
        alias="CPEC Tm Next", nullable=True
    )
    Overlap_with_Next_bps: Optional[Series[pd.Int64Dtype]] = pa.Field(
        alias="Overlap with Next (bps)",
        ge=0,
        nullable=True,
    )
    Overlap_with_Next: Optional[Series[str]] = pa.Field(
        alias="Overlap with Next", nullable=True
    )
    # TODO: tell Nathan about typo
    Overlap_with_Next_Reverse_Complement: Optional[Series[str]] = pa.Field(
        alias="Overlap with Next Reverse Complemenet",
        nullable=True,
    )

    # Golden-date Specific Columns
    Overhang_with_Previous: Optional[Series[str]] = pa.Field(
        alias="Overhang with Previous", nullable=True
    )
    Overhang_with_Next: Optional[Series[str]] = pa.Field(
        alias="Overhang with Next", nullable=True
    )
    Relative_Overhang_Position: Optional[Series[pd.Int64Dtype]] = pa.Field(
        alias="Relative Overhang Position", nullable=True
    )

    # Common to both methods
    Sequence_Length: Series[int] = pa.Field(alias="Sequence Length", gt=0)
    Sequence: Series[str] = pa.Field(is_dna_sequence=())

    class Config:
        strict = True
        coerce = True


class AssemblyPartsSchema(MasterJ5Parts):
    SOURCE_LOCATIONS: Series[str] = pa.Field()
    PART_TYPE: Series[str] = pa.Field(isin=["pcr", "digest"])
    FIRST_PART_SOURCE_PLATE: Series[str] = pa.Field()
    FIRST_PART_WELL: Series[str] = pa.Field()


class MasterJ5Assemblies(pa.SchemaModel):
    Number: Series[int] = pa.Field(ge=0, unique=True)
    Name: Series[str] = pa.Field(unique=True)
    Assembly_Method: Series[str] = pa.Field(
        alias="Assembly Method", isin=["SLIC/Gibson/CPEC", "Golden-gate"]
    )
    Part_Name: Series[str] = pa.Field(
        alias="Part\(s\)\..+",  # noqa: ignore W605
        regex=True,
        nullable=True,
    )
    Part_ID: Series[pd.Int64Dtype] = pa.Field(
        alias="Assembly Piece ID Number\..+",  # noqa: ignore W605
        regex=True,
        nullable=True,
    )

    class Config:
        strict = True
        coerce = True


class MasterJ5SkinnyAssemblies(pa.SchemaModel):
    Number: Series[int] = pa.Field(ge=0)
    Name: Series[str] = pa.Field()
    Assembly_Method: Series[str] = pa.Field(
        alias="Assembly Method", isin=["SLIC/Gibson/CPEC", "Golden-gate"]
    )
    Part_Name: Series[str] = pa.Field(alias="Part Name")
    Part_ID: Series[int] = pa.Field(alias="Part ID", ge=0)
    Part_Order: Series[int] = pa.Field(alias="Part Order", ge=0)

    class Config:
        strict = True
        coerce = True


class AssemblyVolumeSchema(pa.SchemaModel):
    PART_ID: Series[int] = pa.Field(ge=0, unique=True)
    PART_NAME: Series[str] = pa.Field()
    TYPE: Series[str] = pa.Field(
        isin=["PCR", "SOE", "Digest Linearized", "Direct Synthesis/PCR"]
    )
    TYPE_ID: Series[int] = pa.Field(ge=0)
    NUMBER_OF_USES: Series[int] = pa.Field(ge=0)
    VOLUME_REQUIRED: Series[float] = pa.Field(
        alias="VOLUME_REQUIRED_(uL)", ge=0
    )

    class Config:
        strict = True
        coerce = True


class AssemblyVolumeVerifiedSchema(AssemblyVolumeSchema):
    NUMBER_OF_RXNS_PERFORMED: Series[int] = pa.Field(gt=0)
    VOLUME_OBTAINED: Series[float] = pa.Field(
        alias="VOLUME_OBTAINED_(uL)", ge=0
    )
    ENOUGH_VOLUME: Series[bool] = pa.Field()
    SOURCE_WELLS: Series[str] = pa.Field()


class AssemblyWorksheetSchema(MasterJ5SkinnyAssemblies):
    ID_NUMBER: Series[int] = pa.Field(alias="ID Number")
    Source_Plate: Series[str] = pa.Field(alias="Source Plate")
    Source_Well: Series[str] = pa.Field(alias="Source Well")
    SOURCE_LOCATIONS: Series[str] = pa.Field()
    Destination_Plate: Series[str] = pa.Field(alias="Destination Plate")
    Destination_Well: Series[str] = pa.Field(alias="Destination Well")
    Parts_Summary: Series[str] = pa.Field(alias="Parts Summary")


class EquimolarAssemblyWorksheetSchema(
    AssemblyWorksheetSchema, PartsWorksheetSchema
):
    MOLAR_CONCENTRATION: Series[float] = pa.Field(alias="Conc (fmol/uL)")
    EQUIMOLAR_VOLUME: Series[float] = pa.Field()
    fmol_used: Series[float] = pa.Field()
    Transfer_Volume: Series[int] = pa.Field(alias="Transfer Volume")

    class Config:
        strict = True
        coerce = True


class BenchlingPlasmidSequences(pa.SchemaModel):
    Name: Series[str] = pa.Field(unique=True)
    Bases: Series[str] = pa.Field(is_dna_sequence=())
    Type: Series[str] = pa.Field(isin=["cloning", "expression"])

    class Config:
        strict = True
        coerce = True


class BenchlingAASequences(pa.SchemaModel):
    Name: Series[str] = pa.Field(unique=True)
    Bases: Series[str] = pa.Field(is_aa_sequence=())
    Type: Series[str] = pa.Field(
        isin=[
            "AA",
            "Affinity tag",
            "Comm domain",
            "Domain",
            "Fatty Acyl ACP ligase (FAAL)",
            "Fatty acyl coA ligase (FACL)",
            "Fluorescent reporter",
            "Interdomain linker",
            "Module",
            "NPCP",
            "Phosphopantetheinyl transferase (PPTase)",
            "Protease site",
            "Thioesterase (TE)",
        ]
    )


class BenchlingGeneSequences(pa.SchemaModel):
    Name: Series[str] = pa.Field(unique=True)
    Bases: Series[str] = pa.Field(is_dna_sequence=())


pandera_schema = Type[pa.SchemaModel]

VALIDATION_SCHEMAS: Dict[str, pandera_schema] = {
    "registryplasmid": RegistryPlasmidSchema,
    "peaktable": PeakTableSchema,
    "registryworksheet": RegistryWorksheetSchema,
    "synthsplate": SynthsPlateSchema,
    "oligosplate": OligosPlateSchema,
    "oligosorder": OligosOrderSchema,
    "templatesplate": TemplatesPlateSchema,
    "echoinstructions": EchoInstructionsSchema,
    "pcrinstructions": PCRInstructionsSchema,
    "pcrthermocycler": PCRThermocyclerSchema,
    "pcrworksheet": PCRWorksheetSchema,
    "digestsplate": DigestsPlateSchema,
    "digestsworksheet": DigestsWorksheetSchema,
    "partsplate": PartsPlateSchema,
    "partsworksheet": PartsWorksheetSchema,
    "constructworksheet": ConstructWorksheetSchema,
    "masterj5digests": MasterJ5Digests,
    "masterj5synthesis": MasterJ5Synthesis,
    "masterj5oligos": MasterJ5Oligos,
    "masterj5pcrs": MasterJ5PCRs,
    "masterj5parts": MasterJ5Parts,
    "masterj5assemblies": MasterJ5Assemblies,
    "masterj5skinnyassemblies": MasterJ5SkinnyAssemblies,
    "assemblyvolume": AssemblyVolumeSchema,
}
