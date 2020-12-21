from typing import Union

from simpy import Container, Environment


class ContinuousQueue(Container):
    def __init__(self, env: Environment, capacity: Union[int, float], init: Union[int, float], name: str,
                 queue_type: str):
        if capacity == -1:
            super.__init__(env, init=init)
        else:
            super().__init__(env, capacity=capacity, init=init)
        self.name = name
        self.queue_type = queue_type
