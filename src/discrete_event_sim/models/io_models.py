from typing import List, Optional

from pydantic import BaseModel

from .process_models import ProcessInput, ProcessOutput
from .queue_models import QueueInput, QueueStateOutput
from .resource_models import BasicResource, ResouceOutput
from .sim_models import SimInfo


class DesInputModel(BaseModel):
    processes: List[ProcessInput]
    queues: List[QueueInput]
    resources: Optional[List[BasicResource]]
    sim_def: SimInfo


class DesResponseModel(BaseModel):
    process_output: List[ProcessOutput]
    queue_output: List[QueueStateOutput]
    resource_output: List[ResouceOutput]
    sim_def: SimInfo
