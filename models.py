from sqlalchemy import Column, Integer, String, Float
from database import Base

class DraftIndie(Base):
    __tablename__ = "draft_indie"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    
    # Crisp Inputs
    bug_density = Column(Float)
    fps = Column(Float)
    wishlist = Column(Integer)
    remaining_budget = Column(Float)
    
    # Fuzzy Outputs
    score = Column(Float)
    status = Column(String)
