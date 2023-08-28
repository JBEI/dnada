from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Workflow(Base):
    id = Column(Integer, primary_key=True, index=True)
    created_time = Column(String, index=True)
    # Owner
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="workflows")
    # Experiment
    experiment_id = Column(
        Integer,
        ForeignKey("experiment.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    experiment = relationship("Experiment", back_populates="workflows")
    # One to one relationship with condensed design
    # which is a Design with condensed = True
    design_id = Column(
        Integer,
        ForeignKey("design.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    design = relationship("Design", back_populates="workflow")
    # One to one relationship with result zip
    # Which contains raw zip file
    resultzip_id = Column(
        Integer,
        ForeignKey("resultzip.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    resultzip = relationship("ResultZip", back_populates="workflow")
    # Children
    workflowsteps = relationship(
        "WorkflowStep",
        back_populates="workflow",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    plates = relationship(
        "Plate",
        back_populates="workflow",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    instructions = relationship(
        "Instruction",
        back_populates="workflow",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    # runs = relationship(
    #    "Run",
    #    back_populates="workflow",
    #    passive_deletes=True,
    #    cascade="all,delete-orphan",
    # )
