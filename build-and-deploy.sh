export PROJECT_ID=halogen-sol-452703-b5
export REGION=us-west1
export CONNECTION_NAME=halogen-sol-452703-b5:us-west2:guestbook-db

gcloud builds submit \
    --tag gcr.io/$PROJECT_ID/guestbook-app \
    --project $PROJECT_ID

gcloud run deploy guestbook-app \
    --image gcr.io/$PROJECT_ID/guestbook-app \
    --platform managed \
    --region $REGION \
    --add-cloudsql-instances $CONNECTION_NAME \
    --allow-unauthenticated \
    --project $PROJECT_ID
