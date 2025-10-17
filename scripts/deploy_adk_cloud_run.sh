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

gcloud run deploy capymind-agent \
  --source . \
  --region $CAPY_SERVER_REGION \
  --project $CAPY_PROJECT_ID \
  --allow-unauthenticated \
  --set-env-vars $ENV_VARS \
  --set-secrets $SECRETS \
  