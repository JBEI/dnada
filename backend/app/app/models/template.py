from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Template(Base):
    id = Column(Integer, primary_key=True, index=True)
    j5_template_id = Column(Integer, index=True)
    name = Column(String, index=True)
    # Owner it belongs to
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    owner = relationship("User", back_populates="templates")
    # Design template belongs to
    design_id = Column(
        Integer,
        ForeignKey("design.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    design = relationship("Design", back_populates="templates")
    # PCRs template belongs to
    pcrs = relationship(
        "PCR",
        back_populates="template",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
    # Optional synth child
    synth_id = Column(
        Integer,
        ForeignKey("synth.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    synth = relationship("Synth", uselist=False, back_populates="template")
    # Wells that template is in
    templatewells = relationship(
        "TemplateWell",
        back_populates="content",
        passive_deletes=True,
        cascade="all,delete-orphan",
    )
