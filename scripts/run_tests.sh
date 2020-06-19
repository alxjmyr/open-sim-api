#!/bin/bash

python -m pytest --verbose --cov=src --cov=tests --cov-report=term-missing tests
