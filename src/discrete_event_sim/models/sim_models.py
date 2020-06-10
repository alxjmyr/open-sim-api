from pydantic import BaseModel


class SimInfo(BaseModel):
    name: str
    epochs: int
    epoch_unit: str
