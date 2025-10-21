#!/bin/bash

# Deploy the application
adk deploy cloud_run \
  --project=$CAPY_PROJECT_ID \
  --region=$CAPY_SERVER_REGION \
  --service_name=capymind-agent \
  --app_name=capymind_agent \
  --with_ui \
capymind_agent