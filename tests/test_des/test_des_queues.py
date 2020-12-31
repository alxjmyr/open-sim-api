from cmath import inf
from uuid import UUID, uuid4

import pytest
from pydantic.error_wrappers import ValidationError
from simpy import Environment

from src.discrete_event_sim.des_queues import ContinuousQueue
from src.discrete_event_sim.models import queue_models


# tests for queue data models
def test_queue_input():
    """
    Test for the queue input data model
    :return:
    """
    test_queue = queue_models.QueueInput(
            name="test_queue",
            capacity=10,
            inital_value=8,
            queue_type="continuous"
    )

    assert type(test_queue.name) == str
    assert test_queue.name == "test_queue"

    assert type(test_queue.capacity) == int
    assert test_queue.capacity == 10

    assert type(test_queue.inital_value) == int
    assert test_queue.inital_value == 8

    assert type(test_queue.queue_type) == str
    assert test_queue.queue_type == "continuous"


def test_queue_output():
    """
    test for the queue output data model
    :return:
    """
    test_output = queue_models.QueueStateOutput(
            name="test_output",
            capacity=10.5,
            current_value=3,
            queue_type="continuous",
            sim_epoch=10,
            uuid=uuid4()
    )

    assert type(test_output.name) == str
    assert test_output.name == "test_output"

    assert type(test_output.capacity) == int
    assert test_output.capacity == 10

    assert type(test_output.current_value) == int
    assert test_output.current_value == 3

    assert type(test_output.queue_type) == str
    assert test_output.queue_type == "continuous"

    assert type(test_output.sim_epoch) == int
    assert test_output.sim_epoch == 10

    assert type(test_output.uuid) == UUID


def test_queue_input_validation():
    """
    test that queue input model validation with pydantic is behaving correctly
    :return:
    """
    with pytest.raises(ValidationError):
        queue_models.QueueInput(
                name="test_queue",
                capacity=10,
                inital_value=8,
                queue_type="cool_stuff"
        )


def test_queue_output_validation():
    with pytest.raises(ValidationError):
        queue_models.QueueStateOutput(
                name="test_output",
                capacity=10.5,
                current_value=3,
                queue_type="whoop",
                sim_epoch=10,
                uuid=uuid4()
        )


# tests for queue objects
def test_continuous_queue():
    """
    test to validate functionality for the continuous queue object
    :return:
    """
    test_queue = ContinuousQueue(
            name="stuff",
            capacity=10,
            env=Environment(),
            init=2,
            queue_type="continuous"
    )

    assert test_queue.capacity == 10
    assert type(test_queue.capacity) == int

    assert test_queue.level == 2

    test_queue.get(1)

    assert test_queue.level == 1

    test_queue.put(7)

    assert test_queue.level == 8


def test_infinite_continuous_queue():
    """
    test a continuous queue with infinite capacity
    :return:
    """
    test_queue = ContinuousQueue(
            name="stuff",
            capacity=-1,
            env=Environment(),
            init=2,
            queue_type="continuous"
    )

    assert test_queue.capacity == inf
    assert type(test_queue.capacity) == float

    assert test_queue.level == 2

    test_queue.get(1)

    assert test_queue.level == 1

    test_queue.put(7)

    assert test_queue.level == 8


def test_queue_init():
    """
    test the the init value of the queue will raise a ValueError if a negative value is passed
    :return:
    """
    with pytest.raises(ValueError):
        ContinuousQueue(
                name="stuff",
                capacity=-1,
                env=Environment(),
                init=-3,
                queue_type="continuous"
        )
