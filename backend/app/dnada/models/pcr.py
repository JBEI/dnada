from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dnada.db.base_class import Base


class PCR(Base):
    id = Column(Integer, primary_key=True, index=True)
    j5_pcr_id = Column(Integer, index=True)
    note = Column(String)
    mean_oligo_temp = Column(Float)
    delta_oligo_temp = Column(Float)
    mean_oligo_temp_3p = Column(Float)
    delta_oligo_temp_3p = Column(Float)
    length = Column(Integer)
    sequence = Column(String)
    # Owner pcr belongs to
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="pcrs")
    # Part pcr belongs to
    part_id = Column(
        Integer,
        ForeignKey("part.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    part = relationship("Part", back_populates="pcr")
    # Template
    template_id = Column(
        Integer,
        ForeignKey("template.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    template = relationship("Template", back_populates="pcrs")
    # Children
    forward_oligo_id = Column(
        Integer,
        ForeignKey("oligo.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    forward_oligo = relationship(
        "Oligo", back_populates="pcrs_f", foreign_keys=[forward_oligo_id]
    )
    reverse_oligo_id = Column(
        Integer,
        ForeignKey("oligo.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    reverse_oligo = relationship(
        "Oligo", back_populates="pcrs_r", foreign_keys=[reverse_oligo_id]
    )
    # oligos = relationship(
    #    "Oligo", secondary=pcr_to_oligo_association, back_populates="pcrs"
    # )
    # Wells that pcr is in
    pcrwells = relationship(
        "PCRWell",
        back_populates="content",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
