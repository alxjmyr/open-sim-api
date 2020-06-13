# Open Sim
Open sim aims to create a viable simulation as a service platform that enables low code and no code development, deployment, and execution of simulation models.

## Model Offerings
Currently supports discrete event simulations but there are opportunities to build support for system dynamics and agent based simulations in the future.


## Discrete Event Simulation
Open sim can create and run discrete event simulations using a `JSON` body in a request to compose the simulation structure and environment.
At its core open sim approaches this by defining queues and processes. Queues serve as holding areas and processes move either discrete objects or continuous volumes between those queues. Currently 
Open Sim only supports continuous queues and processes (i.e. moving 3 units or 3.75 units of something between queues with defined processes). In the future the intent is to support more complex
object interactions where processes and queues can mode discrete objects (these might represent items or individual boxes for example).

The current discrete event models also do not currently support using resources or constraints to modify process behavior and processes cannot directly interact. The intent would be to build these capabilities out
long term to provide more fully featured simulation building capabilities.


### DES Example
This is a basic example that can be run by making a post request to a running instance of the open sim service. This example defines two processes `Pick` and `Ship` which model a 
warehouse picking product and shipping it. It defines two queues `shipped` and `ship_staging` which define the handoff points between the two processes. 
When the simulation runs it gives a view of products flowing between these queues as the processes run. The response will give a view of each processes activity (with begin and end times for each action) as well as an
iteration by iteration log of the queue states as the simulation runs.

Example POST Request: `http://localhost:8000/discrete-event/run-simulation`

```
{
    "processes": [
        {
            "name": "Pick",
            "duration": 1,
            "rate": 1,
            "output_queue": "ship_staging"
        },
        {
            "name": "Ship",
            "duration": 1,
            "rate": 3,
            "input_queue": "ship_staging",
            "output_queue": "shipped"
        }
    ],
    "queues": [
        {
            "name": "shipped",
            "capacity": 10000,
            "inital_value": 0,
            "queue_type": "continuous"
        },
        {
            "name": "ship_staging",
            "capacity": 200,
            "inital_value": 30,
            "queue_type": "continuous"
        }
    ],
    "sim_def": {
        "name": "Basic Warehouse Sim",
        "epochs": 50,
        "epoch_unit": "seconds"
    }
}
```