from cmath import inf
from typing import Union

from simpy import Container, Environment


# @todo consider adding tracking attrs (i.e. last updated by, last get time, last put time etc)
class ContinuousQueue(Container):
    def __init__(self, env: Environment, capacity: Union[int, float], init: Union[int, float], name: str,
                 queue_type: str):
        if capacity == -1:
            super().__init__(env, capacity=inf, init=init)
        else:
            super().__init__(env, capacity=capacity, init=init)
        self.name = name
        self.queue_type = queue_type
