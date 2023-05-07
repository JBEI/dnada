from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Construct(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    genbank = Column(String)
    j5_construct_id = Column(Integer)
    assembly_method = Column(String)
    jbx = Column(String)
    # Owner
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="constructs")
    # Design
    design_id = Column(
        Integer,
        ForeignKey("design.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    design = relationship("Design", back_populates="constructs")
    # Children
    # Note construct -> assembly is one -> many
    # This is because assembly is now skinnified:
    # Each row in assembly represents a single bin in an assembly rxn
    assemblys = relationship(
        "Assembly",
        back_populates="construct",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    assemblyresults = relationship(
        "AssemblyResult",
        back_populates="sample",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    sequencingresults = relationship(
        "SequencingResult",
        back_populates="sample",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
