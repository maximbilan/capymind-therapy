#!/usr/bin/env bash

python3 -m venv .venv
source .venv/bin/activate
pip install google-adk
pip install google-cloud-firestore