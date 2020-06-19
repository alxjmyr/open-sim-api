from setuptools import find_packages, setup

dependancies = [
    'fastapi[all]==0.55.1',
    'simpy==4.0.1',
    'uvicorn==0.11.5'
]

setup(
        name="OpenSim",
        version="0.1.0alpha",
        packages=find_packages(),
        install_requires=dependancies,
        author="Alex Meyer",
        author_email="alex.j.meyer15@gmail.com",
        url="https://github.com/alexjmeyer92/open-sim-api",
)
