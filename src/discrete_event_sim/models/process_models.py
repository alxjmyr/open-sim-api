from typing import Optional

from pydantic import BaseModel


class ProcessObject(BaseModel):
    name: str
    duration: int
    rate: float
    input_queue: Optional[str]
    output_queue: str


class ProcessOutput(BaseModel):
    name: str
    process_start: int
    process_end: int
    input_queue: Optional[str]
    output_queue: Optional[str]
    process_value: float
    configured_rate: float
    configured_duration: int
