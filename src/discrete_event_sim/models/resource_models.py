from uuid import UUID

from pydantic import BaseModel


# @todo consider renaming to basic resource input to better separate input models from models used internally by the simulation
class BasicResource(BaseModel):
    name: str
    capacity: int


class ResouceOutput(BaseModel):
    name: str
    sim_epoch: int
    capacity: int
    current_utilization: int
    processes_in_queue: int
    uuid: UUID
