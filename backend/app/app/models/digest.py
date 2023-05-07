from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Digest(Base):
    id = Column(Integer, primary_key=True, index=True)
    j5_digest_id = Column(Integer, index=True)
    source = Column(String, index=True)
    length = Column(Integer)
    sequence = Column(String)
    # Owner it belongs to
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="digests")
    # Part digest belongs to
    part_id = Column(
        Integer,
        ForeignKey("part.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    part = relationship("Part", back_populates="digest")
    # Wells digest is in
    digestwells = relationship(
        "DigestWell",
        back_populates="content",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
