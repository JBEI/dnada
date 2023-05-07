from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Part(Base):
    id = Column(Integer, primary_key=True, index=True)
    j5_part_id = Column(Integer, index=True)
    name = Column(String, index=True)
    part_type = Column(String)
    type_id = Column(Integer)
    relative_overlap = Column(Integer)
    extra_5p_bps = Column(Integer)
    extra_3p_bps = Column(Integer)
    overlap_with_next = Column(String)
    overlap_with_next_rc = Column(String)
    sequence_length = Column(Integer)
    sequence = Column(String)
    # Owner
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="parts")
    # Design part belongs to
    design_id = Column(
        Integer,
        ForeignKey("design.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    design = relationship("Design", back_populates="parts")
    # Assembly part belongs to
    # Note: part -> assembly is one -> many relationship
    # Because assembly is skinnified
    # Each row in assembly represents a single bin in an assembly rxn
    assemblys = relationship(
        "Assembly",
        back_populates="part",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    # Children
    pcr = relationship(
        "PCR",
        uselist=False,
        back_populates="part",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    digest = relationship(
        "Digest",
        uselist=False,
        back_populates="part",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    # Wells that part is in
    partwells = relationship(
        "PartWell",
        back_populates="content",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
