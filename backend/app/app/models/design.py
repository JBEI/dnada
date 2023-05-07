from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

from .workflow import Workflow  # noqa


class Design(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    zip_file_name = Column(String, index=True)
    description = Column(String)
    condensed = Column(Boolean)
    # Owner
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="designs")
    # Experiment
    experiment_id = Column(
        Integer,
        ForeignKey(
            "experiment.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
    )
    experiment = relationship("Experiment", back_populates="designs")
    # Children
    constructs = relationship(
        "Construct",
        back_populates="design",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    assemblys = relationship(
        "Assembly",
        back_populates="design",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    oligos = relationship(
        "Oligo",
        back_populates="design",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    synths = relationship(
        "Synth",
        back_populates="design",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    parts = relationship(
        "Part",
        back_populates="design",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    templates = relationship(
        "Template",
        back_populates="design",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    rawdesign = relationship(
        "RawDesign",
        back_populates="design",
        uselist=False,
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    # Workflow, one to one optional relationship
    # Will only have workflow if condensed == True
    workflow = relationship(
        "Workflow",
        uselist=False,
        back_populates="design",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
