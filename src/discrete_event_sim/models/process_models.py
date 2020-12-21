from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel


class ProcessQueue(BaseModel):
    name: str
    rate: Union[int, float]


class ProcessObject(BaseModel):
    name: str
    duration: int
    input_queues: Optional[List[ProcessQueue]]
    output_queue: List[ProcessQueue]
    required_resource: Optional[str]


class ProcessOutput(BaseModel):
    name: str
    process_start: int
    process_end: int
    input_queue: Optional[List[ProcessQueue]]
    output_queue: ProcessQueue
    process_value: float
    configured_rate: float
    configured_duration: int
    uuid: UUID
