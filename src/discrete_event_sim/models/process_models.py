from pydantic import BaseModel


class ProcessObject(BaseModel):
    name: str
    duration: int
