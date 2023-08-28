from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RawDesign(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    data = Column(JSON)
    # Owner
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="rawdesigns")
    # Design
    design_id = Column(
        Integer,
        ForeignKey("design.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    design = relationship("Design", uselist=False, back_populates="rawdesign")
