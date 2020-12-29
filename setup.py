from setuptools import find_packages, setup

dependancies = [
    'fastapi[all]==0.63.0',
    'simpy==4.0.1',
    'uvicorn >= 0.13.0',
    'numpy==1.19.4'
]

setup(
        name="OpenSim",
        version="0.1.0",
        description="JSON composable simulation as a service API for creating / running DES and other simulations",
        packages=find_packages(),
        install_requires=dependancies,
        author="Alex Meyer",
        author_email="alex@alxmyr.com",
        maintainer="Alex Meyer",
        maintainer_email="alex@alxmyr.com",
        url="https://github.com/alexjmeyer92/open-sim-api",
        license='MIT',

)
