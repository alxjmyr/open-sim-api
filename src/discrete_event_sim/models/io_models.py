from typing import List

from pydantic import BaseModel

from .process_models import ProcessObject
from .queue_models import QueueInput
from .sim_models import SimInfo


class DesInputModel(BaseModel):
    processes: List[ProcessObject]
    queues: List[QueueInput]
    sim_def: SimInfo


class DesResponseModel(BaseModel):
    message: str
