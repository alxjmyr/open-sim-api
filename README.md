# Open Sim

Open sim aims to create a viable simulation as a service platform that enables low code and no code development,
deployment, and execution of simulation models.

## Model Offerings

Currently, supports discrete event simulations but there are opportunities to build support for system dynamics and
agent based simulations in the future.

## Running Open Sim

You can run the open sim project quickly using the provided docker file. Just run `docker build -t opensim .` from the
root of the project. Then run `docker run -p 5000:80 -i opensim:latest`
to run the newly built docker image. The `docker run` flags can be adjusted to run in detached more or using different
ports as needed.

## Getting Started

[Check out the docs in the Wiki](https://github.com/alexjmeyer92/open-sim-api/wiki/Getting-Started)

## Service Documentation and examples

API documentation based on the open API spec is available at `/docs` on a running instance of Open Sim Api.

Example inputs for various simulations can be found in `/sim_json_examples/discrete_event_examples`.
