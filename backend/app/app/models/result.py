from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Result(Base):
    id = Column(Integer, primary_key=True, index=True)
    result_type = Column(String, nullable=False)
    # Owner it belongs to
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="results")
    # Parent run
    run_id = Column(
        Integer,
        ForeignKey("run.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    run = relationship("Run", back_populates="results")
    __mapper_args__ = {"polymorphic_on": result_type}


class PCRResult(Result):
    __tablename__ = "pcrresult"
    __mapper_args__ = {"polymorphic_identity": "pcr"}
    id = Column(
        Integer, ForeignKey("result.id"), primary_key=True, index=True
    )
    polymerase = Column(String)
    good = Column(Boolean)
    # Sample
    sample_id = Column(
        Integer,
        ForeignKey("pcrwell.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    sample = relationship("PCRWell", back_populates="results")


class AssemblyResult(Result):
    __tablename__ = "assemblyresult"
    __mapper_args__ = {"polymorphic_identity": "assembly"}
    id = Column(
        Integer, ForeignKey("result.id"), primary_key=True, index=True
    )
    colonies = Column(Boolean)
    # Sample
    sample_id = Column(
        Integer,
        ForeignKey("construct.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    sample = relationship("Construct", back_populates="assemblyresults")


class SequencingResult(Result):
    __tablename__ = "sequencingresult"
    __mapper_args__ = {"polymorphic_identity": "sequencing"}
    id = Column(
        Integer, ForeignKey("result.id"), primary_key=True, index=True
    )
    sequencing = Column(Boolean)
    # Sample
    sample_id = Column(
        Integer,
        ForeignKey("construct.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    sample = relationship("Construct", back_populates="sequencingresults")
