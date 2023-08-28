from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dnada.db.base_class import Base


class Assembly(Base):
    id = Column(Integer, primary_key=True, index=True)
    j5_assembly_id = Column(Integer, index=True)
    name = Column(String, index=True)
    assembly_method = Column(String)
    bin = Column(Integer)
    # Owner
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="assemblys")
    # Design
    design_id = Column(
        Integer,
        ForeignKey("design.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    design = relationship("Design", back_populates="assemblys")
    # Construct
    construct_id = Column(
        Integer,
        ForeignKey("construct.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    construct = relationship("Construct", back_populates="assemblys")
    # Children
    # Note assembly -> part is many -> one
    # This is because assembly is now skinnified:
    # Each row in assembly represents a single bin in an assembly rxn
    part_id = Column(
        Integer,
        ForeignKey("part.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    part = relationship("Part", back_populates="assemblys")
