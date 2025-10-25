#!/bin/bash

PROJECT_ID=$CAPY_PROJECT_ID
SERVICE_ACCOUNT=$CAPY_SERVICE_ACCOUNT
PROJECT_NUMBER=$CAPY_PROJECT_NUMBER
REGION=$CAPY_SERVER_REGION
POOL_ID="githubci"
POOL_NAME="GitHubCI"
LOCATION="global"
PROVIDER_ID="github-provider"
PROVIDER_NAME="GitHub Provider"
REPO="maximbilan/capymind-session"
PRINCIPAL_SET="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/$LOCATION/workloadIdentityPools/$POOL_ID/attribute.repository/$REPO"

# Bind the Workload Identity User role to the service account for the principal set
gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT \
  --project=$PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member=$PRINCIPAL_SET