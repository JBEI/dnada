from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    # Children:
    experiments = relationship(
        "Experiment",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    designs = relationship(
        "Design",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    rawdesigns = relationship(
        "RawDesign",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    constructs = relationship(
        "Construct",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    assemblys = relationship(
        "Assembly",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    parts = relationship(
        "Part",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    pcrs = relationship(
        "PCR",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    digests = relationship(
        "Digest",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    oligos = relationship(
        "Oligo",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    synths = relationship(
        "Synth",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    templates = relationship(
        "Template",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    workflows = relationship(
        "Workflow",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    workflowsteps = relationship(
        "WorkflowStep",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    instructions = relationship(
        "Instruction",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    resultzips = relationship(
        "ResultZip",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    plates = relationship(
        "Plate",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    wells = relationship(
        "Well",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    runs = relationship(
        "Run",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    results = relationship(
        "Result",
        back_populates="owner",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
