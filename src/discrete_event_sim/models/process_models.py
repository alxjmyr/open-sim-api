from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, validator

from src.discrete_event_sim.des_queues import ContinuousQueue


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
    type = "all"
    expression = ""
    kwargs: Dict[str, Any] = {}
    expression_callable: Optional[Callable[[Any], Union[int, float]]]

    @validator('type')
    def queue_type_validator(cls, type: str) -> str:
        assert type in ['all', 'expression']
        return type


class InterruptArgsModel(BaseModel):
    start_time: int = 0
    stop_time: int = 0


class ProcessObject(BaseModel):
    # @todo figure out how to make processes interruptable (i.e. start time, stop time, or paused periods)
    """This might require separating process inputs from an internal process model that can have attributes like
    Paused, active, scheduled etc"""
    name: str
    duration: int
    interruptable: bool = False
    interrupt_args: Optional[InterruptArgsModel]
    input_queue_selection: Optional[QueueSelectionModel]
    input_queues: Optional[List[ProcessQueue]]
    output_queue_selection: QueueSelectionModel
    output_queues: List[ProcessQueue]
    required_resource: Optional[str]

    def get_queue_list(self, queue_set: str, env_queue_dict: Dict[str, ContinuousQueue], now: float) -> List[
        ProcessQueue]:
        """
        determines using queue selection params which queues will be used in the
        execution of the process

        if kwargs contains a queue reference it can be used to reference the state of simulation
        queues when the get_queue_list function is called

        :param now: current epoch of the simulation
        :param env_queue_dict: sim environments queue dict for reference in queue selection expression
        :param queue_set: options are input or output
        :return: list of ProcessQueue objects that have been selected to be processed by the current execution of the process
        """
        if queue_set == "input":
            if self.input_queue_selection.type == "all":
                return deepcopy(self.input_queues)
            elif self.input_queue_selection.type == "expression":
                queues = deepcopy(self.input_queues)
                kwargs = deepcopy(self.input_queue_selection.kwargs)
                kwargs["queue_reference"] = env_queue_dict
                kwargs["now"] = now
                index = self.input_queue_selection.expression_callable(**kwargs)
                return [queues[index]]

        elif queue_set == "output":
            if self.output_queue_selection.type == "all":
                return deepcopy(self.output_queues)
            elif self.output_queue_selection.type == "expression":
                queues = deepcopy(self.output_queues)
                kwargs = deepcopy(self.output_queue_selection.kwargs)
                index = self.output_queue_selection.expression_callable(**kwargs)
                return [queues[index]]


class ProcessOutput(BaseModel):
    name: str
    process_start: int
    process_end: int
    input_queue: Optional[List[ProcessQueue]]
    output_queue: List[ProcessQueue]
    process_rate: float
    configured_rate: float
    configured_duration: int
    uuid: UUID
