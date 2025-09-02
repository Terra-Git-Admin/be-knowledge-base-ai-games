#!/bin/bash

# Cloud Run Deployment Script for Bash
# This script builds and deploys the FastAPI application to Google Cloud Run

set -e

# Default values
SERVICE_NAME="be-knowledge-base-ai-games"
REGION="us-central1"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_green() {
    echo -e "${GREEN}$1${NC}"
}

print_red() {
    echo -e "${RED}$1${NC}"
}

print_yellow() {
    echo -e "${YELLOW}$1${NC}"
}

# Check if project ID is provided
if [ -z "$1" ]; then
    print_red "Usage: $0 <PROJECT_ID> [SERVICE_NAME] [REGION]"
    print_red "Example: $0 my-gcp-project"
    exit 1
fi

PROJECT_ID="$1"
if [ ! -z "$2" ]; then
    SERVICE_NAME="$2"
fi
if [ ! -z "$3" ]; then
    REGION="$3"
fi

IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

print_green "Starting deployment to Google Cloud Run..."
print_yellow "Project ID: $PROJECT_ID"
print_yellow "Service Name: $SERVICE_NAME"
print_yellow "Region: $REGION"
print_yellow "Image Name: $IMAGE_NAME"

# Check if gcloud is installed
print_green "Checking gcloud installation..."
if ! command -v gcloud &> /dev/null; then
    print_red "gcloud CLI is not installed or not in PATH"
    exit 1
fi

# Set the project
print_green "Setting project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

# Enable required APIs
print_green "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build the container image
print_green "Building container image..."
gcloud builds submit --tag "$IMAGE_NAME" .

# Deploy to Cloud Run
print_green "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_NAME" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

# Get the service URL
print_green "Getting service URL..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --format "value(status.url)")

print_green ""
print_green "=== DEPLOYMENT SUCCESSFUL ==="
print_green "Service URL: $SERVICE_URL"
print_green ""
print_green "You can now access your API at: $SERVICE_URL"
print_green "API Documentation: $SERVICE_URL/docs"
print_green ""