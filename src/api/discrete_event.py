from fastapi import APIRouter

from src.discrete_event_sim.des_sim_environment import DiscreteEventEnvironment
from src.discrete_event_sim.models.io_models import DesInputModel, DesResponseModel

router: APIRouter = APIRouter()


@router.post("/run-simulation", status_code=201, response_model=DesResponseModel)
def run_discrete_event_simulation(sim_inputs: DesInputModel) -> DesResponseModel:
    """
    when posting to the /discrete-event/run-simulation endpoint the open-sim-api will take
    the JSON body provided in the request and will attempt to run a discrete event simulation
    composed based on that input.

    If successful it will return 201 along with a response body with the output of the simulation. If the input
    provided in the request body is not of the expected structure it will return with 422 (validation error) along with
    indication of where the validation error occurred.
    """
    sim_env = DiscreteEventEnvironment(simulation_input=sim_inputs)
    sim_env.run_environment()

    output = DesResponseModel(
            process_output=sim_env.process_output,
            queue_output=sim_env.queue_output,
            sim_def=sim_env.sim_def
    )
    return output
