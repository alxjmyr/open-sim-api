from typing import Dict, Generator, List

from simpy import Environment
from simpy.resources.container import Container

from src.api_logger import logger
from .des_queues import ContinuousQueue
from .models.io_models import DesInputModel
from .models.process_models import ProcessObject, ProcessOutput
from .models.queue_models import QueueStateOutput


class DiscreteEventEnvironment(object):
    def __init__(self, simulation_input: DesInputModel):
        self.sim_def = simulation_input.sim_def
        self.queue_input = simulation_input.queues
        self.process_input = simulation_input.processes
        self.simpy_env = Environment()
        self.queue_dict: Dict[str, Container] = {}
        self.process_output: List[ProcessOutput] = []
        self.queue_output: List[QueueStateOutput] = []

        self.append_process_output = self.process_output.append
        self.append_queue_output = self.queue_output.append

    def env_establish_queues(self) -> None:

        for queue in self.queue_input:

            if queue.queue_type == 'continuous':
                new_queue = ContinuousQueue(
                        env=self.simpy_env,
                        capacity=queue.capacity,
                        init=queue.inital_value,
                        name=queue.name,
                        queue_type=queue.queue_type
                )

                self.queue_dict[queue.name] = new_queue

    def _check_queue_state(self, env: Environment) -> Generator:
        while True:
            for name, queue in self.queue_dict.items():
                queue_state = QueueStateOutput(
                        name=name,
                        capacity=queue.capacity,
                        current_value=queue.level,
                        queue_type='continuous',
                        sim_epoch=env.now
                )

                self.append_queue_output(queue_state)
            yield env.timeout(1)

    def process_wrapper(self, env: Environment, process_def: ProcessObject) -> Generator:
        while True:
            logger.debug('{process} || {time}'.format(process=process_def.name, time=env.now))
            # get necessary amount from input queue
            process_start = env.now
            if process_def.input_queue:
                yield self.queue_dict[process_def.input_queue].get(process_def.rate)

            yield env.timeout(process_def.duration)

            yield self.queue_dict[process_def.output_queue].put(process_def.rate)
            process_end = env.now

            process_output = ProcessOutput(
                    name=process_def.name,
                    process_start=process_start,
                    process_end=process_end,
                    input_queue=process_def.input_queue,
                    output_queue=process_def.output_queue,
                    process_value=process_def.rate,
                    configured_rate=process_def.rate,
                    configured_duration=process_def.duration
            )
            self.append_process_output(process_output)

    def env_add_processes(self) -> None:
        for process in self.process_input:
            self.simpy_env.process(self.process_wrapper(env=self.simpy_env, process_def=process))

    def run_environment(self) -> None:
        logger.info("Creating environment queues")
        self.env_establish_queues()
        logger.info("Creating environment processes")
        self.env_add_processes()

        logger.info("Setting up queue state logger")
        self.simpy_env.process(self._check_queue_state(env=self.simpy_env))

        logger.info("Running Simulation Environment for {n} epochs".format(n=self.sim_def.iterations))
        self.simpy_env.run(until=self.sim_def.iterations)
