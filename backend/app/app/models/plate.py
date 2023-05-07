from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.associations import plate_to_instruction_association


class Plate(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    size = Column(Integer)
    raw_data = Column(String)
    plate_type = Column(String, nullable=False)
    # Owner it belongs to
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="plates")
    # Workflow plate belongs to
    workflow_id = Column(
        Integer,
        ForeignKey("workflow.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    workflow = relationship("Workflow", back_populates="plates")
    # Associated instructions
    instructions = relationship(
        "Instruction",
        secondary=plate_to_instruction_association,
        back_populates="plates",
    )
    # children wells
    wells = relationship(
        "Well",
        back_populates="plate",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
