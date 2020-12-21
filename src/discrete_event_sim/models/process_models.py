from typing import Any, Callable, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, validator


class RateDurationModel(BaseModel):
    type: str
    static_value: Optional[Union[int, float]]
    expression = ""
    kwargs: Optional[Dict[str, Union[int, float]]]
    expression_callable: Optional[Callable[[Any], Union[int, float]]]

    @validator('type')
    def queue_type_validator(cls, type: str) -> str:
        assert type in ['static', 'expression']
        return type


class ProcessQueue(BaseModel):
    name: str
    rate: RateDurationModel


class ProcessObject(BaseModel):
    name: str
    duration: int
    input_queues: Optional[List[ProcessQueue]]
    output_queues: List[ProcessQueue]
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
