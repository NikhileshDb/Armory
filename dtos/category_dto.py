from pydantic import BaseModel

class add_category(BaseModel):
    name: str
    description: str
    is_active: bool