from cmath import inf as cinf
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
        self.process_dict: Dict[str, ProcessObject] = {}
        self.process_output: List[ProcessOutput] = []
        self.queue_output: List[QueueStateOutput] = []
        self.append_process_output = self.process_output.append
        self.append_queue_output = self.queue_output.append

    def env_init_queues(self) -> None:

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

    def env_init_resources(self) -> None:
        if self.resource_input:
            for resource in self.resource_input:
                new_resource = BasicResource(
                        env=self.simpy_env,
                        capacity=resource.capacity,
                        name=resource.name
                )
                self.resource_dict[resource.name] = new_resource

    def check_queue_state(self, env: Environment) -> Generator:
        while True:
            for name, queue in self.queue_dict.items():
                if queue.capacity == cinf:
                    capacity = -1
                else:
                    capacity = queue.capacity

                queue_state = QueueStateOutput(
                        name=name,
                        capacity=capacity,
                        current_value=queue.level,
                        queue_type='continuous',
                        sim_epoch=env.now,
                        uuid=uuid4()
                )

                self.append_queue_output(queue_state)
            yield env.timeout(1)

    def process_manager(self, ):
        """
        The process manager uses the interrupt args from the simulation inputs to reschedule & or pause processes
        """
        while True:
            now = self.simpy_env.now
            for k, v in self.process_dict.items():
                schedule_params = v.schedule_params
                # update scheduled flag
                if not schedule_params or schedule_params.interruptable is False:
                    v.is_scheduled = True
                    v.is_paused = False
                else:
                    if schedule_params.start_time <= now <= schedule_params.stop_time:
                        v.is_scheduled = True
                    elif now > schedule_params.stop_time:
                        v.is_scheduled = False
                # update paused flag
                if schedule_params:
                    if schedule_params.interrupt_schedule:
                        for idx, interrupt in enumerate(schedule_params.interrupt_schedule):
                            if interrupt.stop_time < now:
                                v.is_paused = False
                                schedule_params.interrupt_schedule.pop(idx)
                            elif interrupt.start_time <= now <= interrupt.stop_time:
                                v.is_paused = True
                                interrupt.in_progress = True
            yield self.simpy_env.timeout(1)

    def env_setup_processes(self) -> None:
        for process in self.process_input:
            # create process objects
            new_process = ProcessObject(name=process.name,
                                        duration=process.duration,
                                        schedule_params=process.schedule_params,
                                        input_queue_selection=process.input_queue_selection,
                                        input_queues=process.input_queues,
                                        output_queue_selection=process.output_queue_selection,
                                        output_queues=process.output_queues,
                                        required_resource=process.required_resource,
                                        env=self.simpy_env,
                                        env_queue_dict=self.queue_dict,
                                        env_resource_dict=self.resource_dict,
                                        process_outputs=self.process_output,
                                        is_scheduled=False,
                                        is_paused=False)
            if new_process.input_queues:
                for input_queue in new_process.input_queues:
                    if input_queue.rate.type == "expression":
                        # @todo figure out a way to deal with expression and logic injection that is cleaner and more secure than using lambda functions
                        input_queue.rate.expression_callable = eval(input_queue.rate.expression)
                if new_process.input_queue_selection.type == "expression":
                    # @todo figure out a way to deal with expression and logic injection that is cleaner and more secure than using lambda functions
                    new_process.input_queue_selection.expression_callable = eval(
                            new_process.input_queue_selection.expression)
            # setup outputs
            if new_process.output_queues:
                for output in new_process.output_queues:
                    if output.rate.type == "expression":
                        # @todo figure out a way to deal with expression and logic injection that is cleaner and more secure than using lambda functions
                        output.rate.expression_callable = eval(output.rate.expression)
                if new_process.output_queue_selection.type == "expression":
                    # @todo figure out a way to deal with expression and logic injection that is cleaner and more secure than using lambda functions
                    new_process.output_queue_selection.expression_callable = eval(
                            new_process.output_queue_selection.expression)

            self.process_dict[new_process.name] = new_process

            if new_process.required_resource:
                self.simpy_env.process(
                        new_process.execute_resource_constrained()
                )
            else:
                self.simpy_env.process(
                        new_process.execute()
                )

    def run_environment(self) -> None:
        logger.info("Creating environment queues")
        self.env_init_queues()

        logger.info("Creating environment resources")
        self.env_init_resources()

        logger.info("Creating environment processes")
        self.env_setup_processes()

        logger.info("Creating Process Manager")
        self.simpy_env.process(self.process_manager())

        logger.info("Setting up queue state logger")
        self.simpy_env.process(self.check_queue_state(env=self.simpy_env))

        logger.info("Running Simulation Environment for {n} epochs".format(n=self.sim_def.epochs))
        self.simpy_env.run(until=self.sim_def.epochs)
