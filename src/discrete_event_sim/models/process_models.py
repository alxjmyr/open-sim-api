from copy import deepcopy
from typing import Any, Callable, Dict, Generator, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, validator
from simpy import Environment

from src.api_logger import logger
from src.discrete_event_sim.des_queues import ContinuousQueue
from src.discrete_event_sim.des_resources import BasicResource


class RateDurationModel(BaseModel):
    type: str
    static_value: Optional[Union[int, float]]
    expression = ""
    kwargs: Optional[Dict[str, Union[int, float]]]
    expression_callable: Optional[Callable[[Union[int, float]], Union[int, float]]]

    @validator('type')
    def queue_type_validator(cls, type: str) -> str:
        assert type in ['static', 'expression']
        return type


class ProcessQueue(BaseModel):
    name: str
    rate: RateDurationModel

    def get_rate(self, now: float) -> Union[int, float]:
        """
        For an instance of ProcessQueue get_rate() will calculate and return the
        production rate for that process queue
        :return: int or flot indicating production rate
        """
        if self.rate.type == "static":
            rate = self.rate.static_value
        elif self.rate.type == "expression":
            kwargs = deepcopy(self.rate.kwargs)
            kwargs['now'] = now
            rate = self.rate.expression_callable(**kwargs)
        else:
            rate = 0

        return rate


class QueueSelectionModel(BaseModel):
    # @todo should also be able to process queues in sequence / priority (i.e. queue 1 then when nothing available due 2, etc)
    type = "all"
    expression = ""
    kwargs: Dict[str, Any] = {}
    expression_callable: Optional[Callable[[Any], Union[int, float]]]

    @validator('type')
    def queue_type_validator(cls, type: str) -> str:
        assert type in ['all', 'sequential', 'expression']
        return type


class InterruptSchedule(BaseModel):
    start_time: int
    stop_time: int
    in_progress = False


class InterruptArgsModel(BaseModel):
    interruptable = False
    start_time: int
    stop_time: int
    interrupt_schedule: Optional[List[InterruptSchedule]]

    # @fixme figure out why this was needed to make everything work
    class Config:
        arbitrary_types_allowed = True


class ProcessInput(BaseModel):
    name: str
    duration: int
    schedule_params: Optional[InterruptArgsModel]
    input_queue_selection: Optional[QueueSelectionModel]
    input_queues: Optional[List[ProcessQueue]]
    output_queue_selection: QueueSelectionModel
    output_queues: List[ProcessQueue]
    required_resource: Optional[str]


class ProcessOutput(BaseModel):
    name: str
    process_start: int
    process_end: int
    input_queue: Optional[List[ProcessQueue]]
    output_queue: List[ProcessQueue]
    process_rate: float
    configured_rate: float
    configured_duration: int
    process_duration: int
    uuid: UUID


class ProcessObject(BaseModel):
    name: str
    duration: int
    schedule_params: Optional[InterruptArgsModel]
    input_queue_selection: Optional[QueueSelectionModel]
    input_queues: Optional[List[ProcessQueue]]
    output_queue_selection: QueueSelectionModel
    output_queues: List[ProcessQueue]
    required_resource: Optional[str]
    is_scheduled: bool = True
    is_paused: bool = False
    env: Environment
    env_queue_dict: Dict[str, ContinuousQueue]
    env_resource_dict: Dict[str, BasicResource]
    process_outputs: List[ProcessOutput]
    current_input_queues: Optional[List[ProcessQueue]]
    current_task = False
    current_duration = 0

    # @fixme figure out why this was needed to make everything work
    class Config:
        arbitrary_types_allowed = True

    def _get_queue_list(self, queue_set: str, now: float, input_selection: int = 0) -> List[
        ProcessQueue]:
        """
        determines using queue selection params which queues will be used in the
        execution of the process

        if kwargs contains a queue reference it can be used to reference the state of simulation
        queues when the get_queue_list function is called

        :param now: current epoch of the simulation
        :param queue_set: options are input or output
        :return: list of ProcessQueue objects that have been selected to be processed by the current execution of the process
        """
        if queue_set == "input":
            if self.input_queue_selection.type == "all":
                return deepcopy(self.input_queues)
            elif self.input_queue_selection.type == "expression":
                queues = deepcopy(self.input_queues)
                kwargs = deepcopy(self.input_queue_selection.kwargs)
                kwargs["queue_reference"] = self.env_queue_dict
                kwargs["now"] = now
                index = self.input_queue_selection.expression_callable(**kwargs)
                return [queues[index]]

        elif queue_set == "output":
            if self.output_queue_selection.type == "all":
                return deepcopy(self.output_queues)
            elif self.output_queue_selection.type == "expression":
                queues = deepcopy(self.output_queues)
                kwargs = deepcopy(self.output_queue_selection.kwargs)
                kwargs["queue_reference"] = self.env_queue_dict
                kwargs["now"] = now
                kwargs["input_selection"] = input_selection
                index = self.output_queue_selection.expression_callable(**kwargs)
                return [queues[index]]

    def process_input(self, ) -> Generator:
        """
        process input will execute at the begining of the process to update the simulation environment based on the
        input references / data provided in the process object
        """
        self.current_input_queues = None
        if self.input_queues:
            self.current_input_queues = self._get_queue_list(queue_set="input",
                                                             now=self.env.now)
            for queue in self.current_input_queues:
                # calculate input rate
                input_rate = queue.get_rate(now=self.env.now)

                yield self.env_queue_dict[queue.name].get(input_rate)

    def execute(self, ) -> Generator:
        """
        Executes the process in a standard configuration using the above process input / output methods
        This is created as a simpy process
        """
        while True:
            logger.debug('{process} || {time}'.format(process=self.name, time=self.env.now))
            if not self.is_scheduled and not self.current_task:
                yield self.env.timeout(1)
            else:
                if self.is_paused:
                    yield self.env.timeout(1)
                elif not self.is_paused and self.current_duration == 0:
                    # process the first minute of the process execution
                    self.current_task = True
                    process_start = self.env.now

                    # @todo figure out why input processing needed to be moved up out of a separate function to update queues correctly
                    # it potentially could be because the call to self.process_input() didn't have a yield for the generator it returns?
                    self.current_input_queues = None
                    if self.input_queues:
                        self.current_input_queues = self._get_queue_list(queue_set="input",
                                                                         now=self.env.now)
                        for queue in self.current_input_queues:
                            # calculate input rate
                            input_rate = queue.get_rate(now=self.env.now)

                            yield self.env_queue_dict[queue.name].get(input_rate)

                    self.current_duration += 1
                    yield self.env.timeout(1)
                elif self.current_duration < self.duration:
                    self.current_duration += 1
                    yield self.env.timeout(1)

                if self.current_duration == self.duration:
                    output_queue_list = self._get_queue_list(queue_set="output",
                                                             now=self.env.now)
                    for queue in output_queue_list:
                        # calculate output rate
                        output_rate = queue.get_rate(now=self.env.now)

                        yield self.env_queue_dict[queue.name].put(output_rate)

                        output_end = self.env.now

                        process_output = ProcessOutput(
                                name=self.name,
                                process_start=process_start,
                                process_end=output_end,
                                input_queue=deepcopy(self.current_input_queues),
                                output_queue=[queue],
                                process_rate=output_rate,
                                configured_rate=output_rate,
                                configured_duration=self.duration,
                                process_duration=output_end - process_start,
                                uuid=uuid4()
                        )
                        self.process_outputs.append(process_output)
                        self.current_task = False
                        self.current_duration = 0

    def execute_resource_constrained(self, ) -> Generator:
        """
        Executes the process using a resource constrained configuration
        Similar to the execute method above this is created / used as a simpy process
        """
        while True:
            if not self.is_scheduled and not self.current_task:
                yield self.env.timeout(1)
            else:
                if self.is_paused and not self.current_task:
                    yield self.env.timeout(1)
                elif not self.is_paused and self.current_duration == 0:
                    self.current_task = True
                    process_start = self.env.now

                    self.current_input_queues = None
                    if self.input_queues:
                        self.current_input_queues = self._get_queue_list(queue_set="input",
                                                                         now=self.env.now)
                        for queue in self.current_input_queues:
                            # calculate input rate
                            input_rate = queue.get_rate(now=self.env.now)

                            yield self.env_queue_dict[queue.name].get(input_rate)

                    with self.env_resource_dict[self.required_resource].request() as request:
                        yield request
                        logger.debug('{process} has {resource} executing process || {time}'.format(process=self.name,
                                                                                                   resource=self.required_resource,
                                                                                                   time=self.env.now))
                        self.current_duration += self.duration
                        yield self.env.timeout(self.duration)

            if self.current_duration == self.duration:

                output_queue_list = self._get_queue_list(queue_set="output",
                                                         now=self.env.now)
                for queue in output_queue_list:
                    # calculate output rate
                    output_rate = queue.get_rate(now=self.env.now)

                    yield self.env_queue_dict[queue.name].put(output_rate)

                    output_end = self.env.now

                    process_output = ProcessOutput(
                            name=self.name,
                            process_start=process_start,
                            process_end=output_end,
                            input_queue=deepcopy(self.current_input_queues),
                            output_queue=[queue],
                            process_rate=output_rate,
                            configured_rate=output_rate,
                            configured_duration=self.duration,
                            process_duration=output_end - process_start,
                            uuid=uuid4()
                    )
                    self.process_outputs.append(process_output)
                    self.current_duration = 0
                    self.current_task = False
