from typing import Union

from pydantic import BaseModel, validator


class QueueInput(BaseModel):
    name: str
    capacity: Union[int, float]
    inital_value: Union[int, float]
    queue_type: str

    @validator('queue_type')
    def queue_type_validator(cls, queue_type: str) -> str:
        assert queue_type in ['continuous']
        return queue_type
