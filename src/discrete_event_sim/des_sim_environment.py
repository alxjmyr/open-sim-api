from typing import Generator, List

import simpy

from src.api_logger import logger
from .models.process_models import ProcessObject
from .models.sim_models import SimInfo


class DiscreteEventEnvironment(object):
    def __init__(self, processes: List[ProcessObject], sim_def: SimInfo):
        self.env = simpy.Environment()
        self.processes = processes
        self.sim_def = sim_def

    def process_wrapper(self, env: simpy.Environment, name: str, timeout: int) -> Generator:
        while True:
            logger.info('{process} || {time}'.format(process=name, time=env.now))
            yield env.timeout(timeout)

    def env_add_processes(self) -> None:
        for v in self.processes:
            self.env.process(self.process_wrapper(env=self.env, name=v.name, timeout=v.duration))

    def run_environment(self) -> None:
        logger.info("Creating environment processes")
        self.env_add_processes()

        logger.info("Running Simulation Environment for {n} epochs".format(n=self.sim_def.epochs))
        self.env.run(until=self.sim_def.epochs)
