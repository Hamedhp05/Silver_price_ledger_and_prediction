from sqlalchemy import Column,String,Integer,DateTime,Numeric,func
from app.database.base import Base

class PredictionModel(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer,primary_key = True , autoincrement = True)
    predicted_price = Column(Numeric(15, 0), nullable=False)
    model = Column(String , nullable = False)
    predicted_at = Column(DateTime , server_default = func.now())