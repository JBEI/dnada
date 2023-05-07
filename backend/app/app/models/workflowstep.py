from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class WorkflowStep(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    number = Column(Integer)
    title = Column(String)
    status = Column(String)
    # Owner
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="workflowsteps")
    # Workflow
    workflow_id = Column(
        Integer,
        ForeignKey("workflow.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    workflow = relationship("Workflow", back_populates="workflowsteps")
