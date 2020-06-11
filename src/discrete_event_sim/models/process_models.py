from typing import Optional

from pydantic import BaseModel


class ProcessObject(BaseModel):
    name: str
    duration: int
    rate: float
    input_queue: Optional[str]
    output_queue: str
