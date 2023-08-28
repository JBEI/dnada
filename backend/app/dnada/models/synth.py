from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dnada.db.base_class import Base


class Synth(Base):
    id = Column(Integer, primary_key=True, index=True)
    j5_synth_id = Column(Integer, index=True)
    name = Column(String, index=True)
    length = Column(Integer)
    cost = Column(Float)
    sequence = Column(String)
    # Owner it belongs to
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="synths")
    # Design synth belongs to
    design_id = Column(
        Integer,
        ForeignKey("design.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    design = relationship("Design", back_populates="synths")
    # Parent Template
    template = relationship(
        "Template",
        uselist=False,
        back_populates="synth",
        passive_deletes=True,
    )
    # Wells that synth is in
    synthwells = relationship(
        "SynthWell",
        back_populates="content",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
