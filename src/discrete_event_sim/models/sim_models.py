from pydantic import BaseModel


class SimInfo(BaseModel):
    name: str
    iterations: int
    time_unit: str
