from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.associations import plate_to_instruction_association


class Instruction(Base):
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    trial = Column(Integer)
    data = Column(String)
    # Owner
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="instructions")
    # Workflow
    workflow_id = Column(
        Integer,
        ForeignKey("workflow.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    workflow = relationship("Workflow", back_populates="instructions")
    # Associated plates
    plates = relationship(
        "Plate",
        secondary=plate_to_instruction_association,
        back_populates="instructions",
    )
    # Associated runs
    runs = relationship(
        "Run",
        back_populates="instruction",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
