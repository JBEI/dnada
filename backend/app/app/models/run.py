from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Run(Base):
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    instrument = Column(String)
    raw_data = Column(String)
    run_type = Column(String, nullable=False)
    # Owner it belongs to
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="runs")
    # Workflow run belongs to
    # workflow_id = Column(
    #    Integer,
    #    ForeignKey("workflow.id", ondelete="CASCADE", onupdate="CASCADE"),
    # )
    # workflow = relationship("Workflow", back_populates="runs")
    # Instruction run belongs to
    instruction_id = Column(
        Integer,
        ForeignKey(
            "instruction.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
    )
    instruction = relationship("Instruction", back_populates="runs")
    # Children results
    results = relationship(
        "Result",
        back_populates="run",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
