from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dnada.db.base_class import Base


class Oligo(Base):
    id = Column(Integer, primary_key=True, index=True)
    j5_oligo_id = Column(Integer, index=True)
    name = Column(String, index=True)
    length = Column(Integer)
    tm = Column(Float)
    tm_3p = Column(Float)
    cost = Column(Float)
    sequence = Column(String)
    sequence_3p = Column(String)
    # Owner it belongs to
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="oligos")
    # Design oligo belongs to
    design_id = Column(
        Integer,
        ForeignKey("design.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    design = relationship("Design", back_populates="oligos")
    # PCRs oligo belongs to
    pcrs_f = relationship(
        "PCR",
        back_populates="forward_oligo",
        foreign_keys="PCR.forward_oligo_id",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    pcrs_r = relationship(
        "PCR",
        back_populates="reverse_oligo",
        foreign_keys="PCR.reverse_oligo_id",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    # pcrs = relationship(
    #    "PCR", secondary=pcr_to_oligo_association, back_populates="oligos"
    # )
    # Wells that oligo is in
    oligowells = relationship(
        "OligoWell",
        back_populates="content",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    oligoorder96wells = relationship(
        "OligoOrder96Well",
        back_populates="content",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
