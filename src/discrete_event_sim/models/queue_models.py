from typing import Union
from uuid import UUID

from pydantic import BaseModel, validator


class QueueInput(BaseModel):
    name: str
    capacity: Union[int, float]  # capacity of -1 will set queue capacity to infinity
    inital_value: Union[int, float]
    queue_type: str

    @validator('queue_type')
    def queue_type_validator(cls, queue_type: str) -> str:
        assert queue_type in ['continuous']
        return queue_type


class QueueStateOutput(BaseModel):
    name: str
    capacity: Union[int, float]
    current_value: Union[int, float]
    queue_type: str
    sim_epoch: int
    uuid: UUID

    @validator('queue_type')
    def queue_type_validator(cls, queue_type: str) -> str:
        assert queue_type in ['continuous']
        return queue_type
