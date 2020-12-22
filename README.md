# Open Sim

Open sim aims to create a viable simulation as a service platform that enables low code and no code development,
deployment, and execution of simulation models.

## Running Open Sim

You can run the open sim project quickly using the provided docker file. Just run `docker build -t opensim .` from the
root of the project. Then run `docker run -p 5000:80 -i opensim:latest`
to run the newly built docker image. The `docker run` flags can be adjusted to run in detached more or using different
ports as needed.

## Model Offerings

Currently, supports discrete event simulations but there are opportunities to build support for system dynamics and
agent based simulations in the future.

## Service Documentation and examples

API documentation based on the open API spec is available at `/docs` on a running instance of Open Sim Api.

Example inputs for various simulations can be found in `/sim_json_examples/discrete_event_examples`.

## Discrete Event Simulation

Open sim can create and run discrete event simulations using a `JSON` body in a `POST` request to compose the simulation
structure and environment. At its core open sim does this by defining queues and processes. Queues serve as holding
areas and processes move either discrete objects or continuous volumes between those queues. Currently, Open Sim only
supports continuous queues and processes (i.e. moving 3 units or 3.75 units of something between queues with defined
processes). In the future the intent is to support more complex object interactions where processes and queues can move
discrete objects (these might represent items or individual containers for example).

Open sim also supports applying resource constraints on processes. These can optionally be defined through a `resources`
object in the input `JSON` if defined an optional key for `required_resource` can be applied to a process to require
that process to access a resource before it the process is executed. This can be used to model things like limited
availability of equipment in a warehouse (i.e. a freight mover process must acquire access to a forklift before moving
freight). There is an example of defining these resources in the `sim_json_examples` directory.

Finally, at present processes can not interact directly. They can only acquire resources, and move volumes between
queues. The intent would be to build these and other capabilities out long term to provide more fully featured
simulation capabilities.

### DES Example

Below is a basic example that can be run by making a post request to a running instance of the open sim service.
Additional, example inputs are available in the `sim_json_examples/` directory. This example defines two
processes `Pick` and `Ship` which model a warehouse picking product and shipping it. It defines two
queues `ship_staging` and `shipped` which define the hand off points between the two processes. When the simulation runs
it gives a view of products flowing between these queues as the processes run. The response will give a view of each
processes' activity (with begin and end times for each action) as well as an iteration by iteration log of the queue
states as the simulation runs.

Example POST Request: `http://localhost:8000/discrete-event/run-simulation`

```
{
  "processes": [
    {
      "name": "Pick",
      "duration": 1,
      "output_queue_selection": {
        "type": "all"
      },
      "output_queues": [
        {
          "name": "ship_staging",
          "rate": {
            "type": "static",
            "static_value": 3
          }
        }
      ]
    },
    {
      "name": "Ship",
      "duration": 1,
      "input_queue_selection": {
        "type": "all"
      },
      "input_queues": [
        {
          "name": "ship_staging",
          "rate": {
            "type": "static",
            "static_value": 3
          }
        }
      ],
      "output_queue_selection": {
        "type": "all"
      },
      "output_queues": [
        {
          "name": "shipped",
          "rate": {
            "type": "static",
            "static_value": 3
          }
        }
      ]
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
    "name": "Pick and Ship Simulation",
    "epochs": 100,
    "time_unit": "seconds"
  }
}
```