from typing import List

from pydantic import BaseModel

from .process_models import ProcessObject, ProcessOutput
from .queue_models import QueueInput, QueueStateOutput
from .sim_models import SimInfo


class DesInputModel(BaseModel):
    processes: List[ProcessObject]
    queues: List[QueueInput]
    sim_def: SimInfo


class DesResponseModel(BaseModel):
    process_output: List[ProcessOutput]
    queue_output: List[QueueStateOutput]
    sim_def: SimInfo
