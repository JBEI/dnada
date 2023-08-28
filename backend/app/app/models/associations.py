from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base_class import Base

pcr_to_oligo_association = Table(
    "pcr_to_oligo",
    Base.metadata,
    Column(
        "pcr_id",
        Integer,
        ForeignKey("pcr.id", ondelete="CASCADE", onupdate="CASCADE"),
    ),
    Column(
        "oligo_id",
        Integer,
        ForeignKey("oligo.id", ondelete="CASCADE", onupdate="CASCADE"),
    ),
)

plate_to_instruction_association = Table(
    "plate_to_instruction",
    Base.metadata,
    Column(
        "plate_id",
        Integer,
        ForeignKey("plate.id", ondelete="CASCADE", onupdate="CASCADE"),
    ),
    Column(
        "instruction_id",
        Integer,
        ForeignKey("instruction.id", ondelete="CASCADE", onupdate="CASCADE"),
    ),
)
