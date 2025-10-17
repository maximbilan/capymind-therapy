#!/bin/bash

FUNCTIONS=("therapysession")
RUNTIME="python312"
MEMORY="1GB"
TIMEOUT=60 # 1 minute

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

for FUNC_NAME in "${FUNCTIONS[@]}"; do
    echo "Deploying function: $FUNC_NAME"

    gcloud functions deploy $FUNC_NAME \
        --runtime $RUNTIME \
        --trigger-http \
        --allow-unauthenticated \
        --entry-point $FUNC_NAME \
        --project $CAPY_PROJECT_ID \
        --gen2 \
        --region $CAPY_SERVER_REGION \
        --set-env-vars $ENV_VARS \
        --set-secrets $SECRETS \
        --memory $MEMORY \
        --timeout $TIMEOUT

    # Print the deployment status
    if [ $? -eq 0 ]; then
        echo "Function $FUNC_NAME deployed successfully."
    else
        echo "Failed to deploy function $FUNC_NAME."
        exit 1
    fi
done