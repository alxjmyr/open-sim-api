from typing import Dict, Generator, List
from uuid import uuid4

from simpy import Environment

from src.api_logger import logger
from .des_queues import ContinuousQueue
from .des_resources import BasicResource
from .models.io_models import DesInputModel
from .models.process_models import ProcessObject, ProcessOutput
from .models.queue_models import QueueStateOutput


class DiscreteEventEnvironment(object):
    def __init__(self, simulation_input: DesInputModel):
        self.sim_def = simulation_input.sim_def
        self.queue_input = simulation_input.queues
        self.process_input = simulation_input.processes
        self.resource_input = simulation_input.resources
        self.simpy_env = Environment()
        self.queue_dict: Dict[str, ContinuousQueue] = {}
        self.resource_dict: Dict[str, BasicResource] = {}
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

    def env_establish_resources(self) -> None:
        if self.resource_input:
            for resource in self.resource_input:
                new_resource = BasicResource(
                        env=self.simpy_env,
                        capacity=resource.capacity,
                        name=resource.name
                )
                self.resource_dict[resource.name] = new_resource

    def _check_queue_state(self, env: Environment) -> Generator:
        while True:
            for name, queue in self.queue_dict.items():
                queue_state = QueueStateOutput(
                        name=name,
                        capacity=queue.capacity,
                        current_value=queue.level,
                        queue_type='continuous',
                        sim_epoch=env.now,
                        uuid=uuid4()
                )

                self.append_queue_output(queue_state)
            yield env.timeout(1)

    def _process_wrapper(self, env: Environment, process_def: ProcessObject) -> Generator:
        while True:
            logger.debug('{process} || {time}'.format(process=process_def.name, time=env.now))
            # get necessary amount from input queue
            process_start = env.now
            if process_def.input_queues:
                for queue in process_def.input_queues:
                    yield self.queue_dict[queue.name].get(queue.rate)

            yield env.timeout(process_def.duration)

            yield self.queue_dict[process_def.output_queue].put(process_def.rate)
            process_end = env.now

            process_output = ProcessOutput(
                    name=process_def.name,
                    process_start=process_start,
                    process_end=process_end,
                    input_queue=process_def.input_queues,
                    output_queue=process_def.output_queue,
                    rate=process_def.rate,
                    process_value=process_def.rate,
                    configured_rate=process_def.rate,
                    configured_duration=process_def.duration,
                    uuid=uuid4()
            )
            self.append_process_output(process_output)

    def _resource_constrained_process_wrapper(self, env: Environment, process_def: ProcessObject) -> Generator:
        while True:
            logger.debug('{process} || {time}'.format(process=process_def.name, time=env.now))

            process_start = env.now

            if process_def.input_queues:
                for queue in process_def.input_queues:
                    yield self.queue_dict[queue.name].get(queue.rate)

            if process_def.required_resource:
                logger.debug('{process} acquiring {resource} || {time}'.format(process=process_def.name,
                                                                               resource=process_def.required_resource,
                                                                               time=env.now))
                with self.resource_dict[process_def.required_resource].request() as request:
                    yield request

                    logger.debug('{process} has {resource} executing process || {time}'.format(process=process_def.name,
                                                                                               resource=process_def.required_resource,
                                                                                               time=env.now))
                    yield env.timeout(process_def.duration)

            yield self.queue_dict[process_def.output_queue].put(process_def.rate)
            process_end = env.now

            process_output = ProcessOutput(
                    name=process_def.name,
                    process_start=process_start,
                    process_end=process_end,
                    input_queue=process_def.input_queues,
                    output_queue=process_def.output_queue,
                    rate=process_def.rate,
                    process_value=process_def.rate,
                    configured_rate=process_def.rate,
                    configured_duration=process_def.duration,
                    uuid=uuid4()
            )
            self.append_process_output(process_output)

    def env_add_processes(self) -> None:
        for process in self.process_input:
            if process.required_resource:
                self.simpy_env.process(
                        self._resource_constrained_process_wrapper(env=self.simpy_env, process_def=process)
                )
            else:
                self.simpy_env.process(self._process_wrapper(env=self.simpy_env, process_def=process))

    def run_environment(self) -> None:
        logger.info("Creating environment queues")
        self.env_establish_queues()

        logger.info("Creating environment resources")
        self.env_establish_resources()

        logger.info("Creating environment processes")
        self.env_add_processes()

        logger.info("Setting up queue state logger")
        self.simpy_env.process(self._check_queue_state(env=self.simpy_env))

        logger.info("Running Simulation Environment for {n} epochs".format(n=self.sim_def.iterations))
        self.simpy_env.run(until=self.sim_def.iterations)
