#!/bin/bash


#get root folder
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
PROJECT_ROOT="$SCRIPT_DIR/.."

#export project details
export PROJECT_ID=halogen-sol-452703-b5
export REGION=us-west1
export CONNECTION_NAME=halogen-sol-452703-b5:us-west2:guestbook-db

#build the container using Dockerfile in root folder and deploy it to Google Cloud Run
gcloud builds submit "$PROJECT_ROOT" \
    --tag gcr.io/$PROJECT_ID/guestbook-app \
    --project $PROJECT_ID

gcloud run deploy guestbook-app \
    --image gcr.io/$PROJECT_ID/guestbook-app \
    --platform managed \
    --region $REGION \
    --add-cloudsql-instances $CONNECTION_NAME \
    --allow-unauthenticated \
    --project $PROJECT_ID
