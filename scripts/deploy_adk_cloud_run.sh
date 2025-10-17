#!/bin/bash

# Set environment variables
ENV_PARAMS=("CAPY_PROJECT_ID=$CAPY_PROJECT_ID" "CAPY_SERVER_REGION=$CAPY_SERVER_REGION" "CLOUD=true")
ENV_VARS=""
for PARAM in "${ENV_PARAMS[@]}"; do
  ENV_VARS+="$PARAM,"
done
ENV_VARS=${ENV_VARS%,}

# Set the secret environment variables
SECRET_PARAMS=("GOOGLE_API_KEY=gemini_api_key")
SECRETS=""
for PARAM in "${SECRET_PARAMS[@]}"; do
  SECRETS+="$PARAM:latest,"
done
SECRETS=${SECRETS%,}

adk deploy cloud_run \
  --project=$CAPY_PROJECT_ID \
  --region=$CAPY_SERVER_REGION \
  --service_name=capymind \
  --app_name=capymind_agent \
  --with_ui \
capymind_agent