from pydantic import BaseModel

class add_attributes(BaseModel):
    data: dict 

class get_attributes(BaseModel):
    id: int
    category_id: int
    data: dict
    added_date: float
