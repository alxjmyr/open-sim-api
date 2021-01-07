from simpy import Environment

from src.discrete_event_sim.des_resources import BasicResource


# tests for basic resources
def test_basic_resource():
    resource = BasicResource(
            env=Environment(),
            capacity=30,
            name="test_resource"
    )

    assert resource.name == "test_resource"
    assert type(resource.name) == str

    assert resource.capacity == 30
    assert type(resource.capacity) == int

    assert resource.queue == []
    assert resource.count == 0
    assert resource.users == []
