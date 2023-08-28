from sqlalchemy import Column, Integer, String

from dnada.db.base_class import Base


class Banner(Base):
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
