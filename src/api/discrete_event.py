from fastapi import APIRouter

from src.discrete_event_sim.des_sim_environment import DiscreteEventEnvironment
from src.discrete_event_sim.models.io_models import DesInputModel, DesResponseModel

router: APIRouter = APIRouter()


@router.post("/run-simulation", response_model=DesResponseModel)
def run_de_simulation(sim_inputs: DesInputModel) -> DesResponseModel:
    sim_env = DiscreteEventEnvironment(simulation_input=sim_inputs)
    sim_env.run_environment()

    output = DesResponseModel(
            process_output=sim_env.process_output,
            queue_output=sim_env.queue_output,
            sim_def=sim_env.sim_def
    )
    return output
