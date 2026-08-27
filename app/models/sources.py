from sqlalchemy import Column,String,Integer,Boolean,Enum as SQLEnum
from enum import Enum as pyEnum
from sqlalchemy.orm import relationship
from app.database.base import Base


class SourceType(pyEnum):
    API = "API"
    SCRAPER = "SCRAPER"

class SourceModel(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(SourceType),nullable=False)
    enabled = Column(Boolean, default=True)
    

    prices = relationship("PriceModel", back_populates="source")