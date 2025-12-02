from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}')>"