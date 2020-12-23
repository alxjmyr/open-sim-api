from pydantic import BaseModel


# @todo consider renaming to basic resource input to better separate input models from models used internally by the simulation
class BasicResource(BaseModel):
    name: str
    capacity: int
