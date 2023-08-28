from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dnada.db.base_class import Base
from dnada.models import *  # noqa


class Well(Base):
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)
    volume = Column(Float)
    well_type = Column(String, nullable=False)
    # Owner it belongs to
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="wells")
    # Parent plate
    plate_id = Column(
        Integer,
        ForeignKey("plate.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    plate = relationship("Plate", back_populates="wells")
    __mapper_args__ = {"polymorphic_on": well_type}


class OligoWell(Well):
    __tablename__ = "oligowell"
    __mapper_args__ = {"polymorphic_identity": "oligo"}
    id = Column(Integer, ForeignKey("well.id"), primary_key=True, index=True)
    # Contents
    content_id = Column(
        Integer,
        ForeignKey("oligo.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    content = relationship("Oligo", back_populates="oligowells")


class OligoOrder96Well(Well):
    __tablename__ = "oligoorder96well"
    __mapper_args__ = {"polymorphic_identity": "oligoorder96"}
    id = Column(Integer, ForeignKey("well.id"), primary_key=True, index=True)
    # Contents
    content_id = Column(
        Integer,
        ForeignKey("oligo.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    content = relationship("Oligo", back_populates="oligoorder96wells")


class DigestWell(Well):
    __tablename__ = "digestwell"
    __mapper_args__ = {"polymorphic_identity": "digest"}
    id = Column(Integer, ForeignKey("well.id"), primary_key=True, index=True)
    # Contents
    content_id = Column(
        Integer,
        ForeignKey("digest.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    content = relationship("Digest", back_populates="digestwells")


class SynthWell(Well):
    __tablename__ = "synthwell"
    __mapper_args__ = {"polymorphic_identity": "synth"}
    id = Column(Integer, ForeignKey("well.id"), primary_key=True, index=True)
    # Contents
    content_id = Column(
        Integer,
        ForeignKey("synth.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    content = relationship("Synth", back_populates="synthwells")


class PCRWell(Well):
    __tablename__ = "pcrwell"
    __mapper_args__ = {"polymorphic_identity": "pcr"}
    id = Column(Integer, ForeignKey("well.id"), primary_key=True, index=True)
    # Contents
    content_id = Column(
        Integer,
        ForeignKey("pcr.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    content = relationship("PCR", back_populates="pcrwells")
    # Results with pcr as sample
    results = relationship(
        "PCRResult",
        back_populates="sample",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )


class TemplateWell(Well):
    __tablename__ = "templatewell"
    __mapper_args__ = {"polymorphic_identity": "template"}
    id = Column(Integer, ForeignKey("well.id"), primary_key=True, index=True)
    # Contents
    content_id = Column(
        Integer,
        ForeignKey("template.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    content = relationship("Template", back_populates="templatewells")


class PartWell(Well):
    __tablename__ = "partwell"
    __mapper_args__ = {"polymorphic_identity": "part"}
    id = Column(Integer, ForeignKey("well.id"), primary_key=True, index=True)
    # Contents
    content_id = Column(
        Integer,
        ForeignKey("part.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    content = relationship("Part", back_populates="partwells")


# class AssemblyWell(Well):
#     __tablename__ = "assemblywell"
#     __mapper_args__ = {"polymorphic_identity": "assembly"}
#     id = Column(
#         Integer, ForeignKey("well.id"), primary_key=True, index=True
#     )
#     # Contents
#     content_id = Column(
#         Integer,
#         ForeignKey("assembly.id", ondelete="CASCADE", onupdate="CASCADE"),
#     )
#     content = relationship("Assembly", back_populates="assemblywells")
#     # Results with assembly as sample
#     results = relationship(
#         "AssemblyResult",
#         back_populates="sample",
#         passive_deletes=True,
#         cascade="all,delete-orphan",
#     )
