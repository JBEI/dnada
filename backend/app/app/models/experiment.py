from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models import *  # noqa


class Experiment(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    # Owner
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="experiments")
    # Children
    designs = relationship(
        "Design",
        back_populates="experiment",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    workflows = relationship(
        "Workflow",
        back_populates="experiment",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    resultzips = relationship(
        "ResultZip",
        back_populates="experiment",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
