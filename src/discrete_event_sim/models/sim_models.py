from pydantic import BaseModel


class SimInfo(BaseModel):
    name: str
    epochs: int
    time_unit: str
