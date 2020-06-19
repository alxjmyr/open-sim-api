from simpy import Environment, Resource


class BasicResource(Resource):
    def __init__(self, env: Environment, capacity: int, name: str):
        super().__init__(env, capacity=capacity)
        self.name = name
