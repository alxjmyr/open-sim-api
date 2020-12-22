from setuptools import find_packages, setup

dependancies = [
    'fastapi[all]==0.63.0',
    'simpy==4.0.1',
    'uvicorn >= 0.13.0',
    'numpy==1.19.4'
]

setup(
        name="OpenSim",
        version="0.1.0a",
        packages=find_packages(),
        install_requires=dependancies,
        author="Alex Meyer",
        author_email="alex.j.meyer15@gmail.com",
        url="https://github.com/alexjmeyer92/open-sim-api",
)
