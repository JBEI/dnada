from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dnada.db.base_class import Base
from dnada.models import *  # noqa


class ResultZip(Base):
    id = Column(Integer, primary_key=True, index=True)
    data = Column(String)
    # Owner
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="resultzips")
    # Experiment
    experiment_id = Column(
        Integer,
        ForeignKey("experiment.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    experiment = relationship("Experiment", back_populates="resultzips")
    # Workflow
    workflow = relationship("Workflow", uselist=False, back_populates="resultzip")
