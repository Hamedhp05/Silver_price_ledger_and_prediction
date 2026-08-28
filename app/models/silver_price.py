from sqlalchemy import Column,String,Integer,DateTime,Numeric,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class PriceModel(Base):
    __tablename__ = "silver_prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)  
    price = Column(Numeric(15, 0), nullable=False)
    currency = Column(String, default="IRT" , nullable=False)
    fetched_at = Column(DateTime , nullable= False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


    source = relationship("SourceModel", back_populates="prices")