#!/usr/bin/env bash

# Setup a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install required packages
pip install google-adk==1.16.0
pip install google-cloud-firestore