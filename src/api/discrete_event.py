from typing import Dict

from fastapi import APIRouter

from src.discrete_event_sim.des_sim_environment import DiscreteEventEnvironment
from src.discrete_event_sim.models.io_models import DesInputModel, DesResponseModel

router: APIRouter = APIRouter()


@router.post("/run-simulation", response_model=DesResponseModel)
def run_de_simulation(input: DesInputModel) -> Dict:
    sim_env = DiscreteEventEnvironment(simulation_input=input)
    sim_env.run_environment()

    response_value = {
        "message": "Discrete Event Simulation Completed Successfully after {n} epochs".format(n=input.sim_def.epochs)
    }
    return response_value
