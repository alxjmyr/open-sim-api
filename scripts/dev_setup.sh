#!/bin/bash

# installs core requirements
pip install -e . &&
  # installs development only requirements
  pip install -r ./dev_requirements.txt

# make scripts executeable
chmod +x ./scripts/*.sh
