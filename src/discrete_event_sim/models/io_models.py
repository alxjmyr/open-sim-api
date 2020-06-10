from typing import List

from pydantic import BaseModel

from .process_models import ProcessObject
from .sim_models import SimInfo


class DesInputModel(BaseModel):
    processes: List[ProcessObject]
    sim_def: SimInfo


class DesResponseModel(BaseModel):
    message: str
