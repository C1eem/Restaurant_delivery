from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True  # вместо orm_mode в Pydantic v2

class TimestampSchema(BaseSchema):
    created_at: Optional[datetime] = None