from pydantic import BaseModel

class add_asset(BaseModel):
    name: str
    description: str
    is_active: bool
    category_id: int