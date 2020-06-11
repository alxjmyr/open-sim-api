from typing import Dict, Generator

from simpy import Environment
from simpy.resources.container import Container

from src.api_logger import logger
from .models.io_models import DesInputModel
from .models.process_models import ProcessObject


class DiscreteEventEnvironment(object):
    def __init__(self, simulation_input: DesInputModel):
        self.sim_def = simulation_input.sim_def
        self.queue_input = simulation_input.queues
        self.process_input = simulation_input.processes
        self.simpy_env = Environment()
        self.queue_dict: Dict[str, Container] = {}

    def env_create_queues(self) -> None:

        for queue in self.queue_input:
            self.queue_dict[queue.name] = Container(env=self.simpy_env,
                                                    capacity=queue.capacity,
                                                    init=queue.inital_value)

    def process_wrapper(self, env: Environment, process_def: ProcessObject) -> Generator:
        while True:
            logger.info('{process} || {time}'.format(process=process_def.name, time=env.now))
            # get necessary amount from input queue
            if process_def.input_queue:
                self.queue_dict[process_def.input_queue].get(process_def.rate)

            yield env.timeout(process_def.duration)

            self.queue_dict[process_def.output_queue].put(process_def.rate)

    def env_add_processes(self) -> None:
        for process in self.process_input:
            self.simpy_env.process(self.process_wrapper(env=self.simpy_env, process_def=process))

    def run_environment(self) -> None:
        logger.info("Creating environment processes")
        self.env_add_processes()

        logger.info("Running Simulation Environment for {n} epochs".format(n=self.sim_def.epochs))
        self.simpy_env.run(until=self.sim_def.epochs)
