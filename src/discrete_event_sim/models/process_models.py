from copy import deepcopy
from typing import Callable, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, validator


class RateDurationModel(BaseModel):
    type: str
    static_value: Optional[Union[int, float]]
    expression = ""
    kwargs: Optional[Dict[str, Union[int, float]]]
    expression_callable: Optional[Callable[[Union[int, float]], Union[int, float]]]

    @validator('type')
    def queue_type_validator(cls, type: str) -> str:
        assert type in ['static', 'expression']
        return type


class ProcessQueue(BaseModel):
    name: str
    rate: RateDurationModel

    def get_rate(self, now: int) -> Union[int, float]:
        """
        For an instance of ProcessQueue get_rate() will calculate and return the
        production rate for that process queue
        :return: int or flot indicating production rate
        """
        if self.rate.type == "static":
            rate = self.rate.static_value
        elif self.rate.type == "expression":
            kwargs = deepcopy(self.rate.kwargs)
            kwargs['now'] = now
            rate = self.rate.expression_callable(**kwargs)

        return rate


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
    process_rate: float
    configured_rate: float
    configured_duration: int
    uuid: UUID
