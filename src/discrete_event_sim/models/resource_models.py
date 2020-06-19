from pydantic import BaseModel


class BasicResource(BaseModel):
    name: str
    capacity: int
