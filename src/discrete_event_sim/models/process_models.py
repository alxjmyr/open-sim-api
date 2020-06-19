from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel


class ProcessInputQueue(BaseModel):
    name: str
    rate: Union[int, float]


class ProcessObject(BaseModel):
    name: str
    duration: int
    rate: float
    input_queues: Optional[List[ProcessInputQueue]]
    output_queue: str
    required_resource: Optional[str]


class ProcessOutput(BaseModel):
    name: str
    process_start: int
    process_end: int
    input_queue: Optional[List[ProcessInputQueue]]
    output_queue: Optional[str]
    rate: float
    process_value: float
    configured_rate: float
    configured_duration: int
    uuid: UUID
