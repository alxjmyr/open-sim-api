from simpy import Environment, Resource


# @todo add tracking attrs to Resources (i.e. last acquired by, last used time, etc that can be reported out)
# @todo add resource state observer in the simulation environment
class BasicResource(Resource):
    def __init__(self, env: Environment, capacity: int, name: str):
        super().__init__(env, capacity=capacity)
        self.name = name
