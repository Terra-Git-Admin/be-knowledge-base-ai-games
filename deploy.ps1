# Cloud Run Deployment Script for PowerShell
# This script builds and deploys the FastAPI application to Google Cloud Run

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "be-knowledge-base-ai-games",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false)]
    [string]$ImageName = "gcr.io/$ProjectId/$ServiceName"
)

# Colors for output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"

Write-Host "Starting deployment to Google Cloud Run..." -ForegroundColor $Green
Write-Host "Project ID: $ProjectId" -ForegroundColor $Yellow
Write-Host "Service Name: $ServiceName" -ForegroundColor $Yellow
Write-Host "Region: $Region" -ForegroundColor $Yellow
Write-Host "Image Name: $ImageName" -ForegroundColor $Yellow

try {
    # Check if gcloud is installed
    Write-Host "Checking gcloud installation..." -ForegroundColor $Green
    gcloud version
    if ($LASTEXITCODE -ne 0) {
        throw "gcloud CLI is not installed or not in PATH"
    }

    # Set the project
    Write-Host "Setting project to $ProjectId..." -ForegroundColor $Green
    gcloud config set project $ProjectId
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to set project"
    }

    # Enable required APIs
    Write-Host "Enabling required APIs..." -ForegroundColor $Green
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com

    # Build the container image
    Write-Host "Building container image..." -ForegroundColor $Green
    gcloud builds submit --tag $ImageName .
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to build container image"
    }

    # Deploy to Cloud Run
    Write-Host "Deploying to Cloud Run..." -ForegroundColor $Green
    gcloud run deploy $ServiceName `
        --image $ImageName `
        --platform managed `
        --region $Region `
        --allow-unauthenticated `
        --port 8080 `
        --memory 512Mi `
        --cpu 1 `
        --max-instances 10 `
        --set-env-vars "GOOGLE_CLOUD_PROJECT=$ProjectId"
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to deploy to Cloud Run"
    }

    # Get the service URL
    Write-Host "Getting service URL..." -ForegroundColor $Green
    $serviceUrl = gcloud run services describe $ServiceName --platform managed --region $Region --format "value(status.url)"
    
    Write-Host "" -ForegroundColor $Green
    Write-Host "=== DEPLOYMENT SUCCESSFUL ===" -ForegroundColor $Green
    Write-Host "Service URL: $serviceUrl" -ForegroundColor $Green
    Write-Host "" -ForegroundColor $Green
    Write-Host "You can now access your API at: $serviceUrl" -ForegroundColor $Green
    Write-Host "API Documentation: $serviceUrl/docs" -ForegroundColor $Green
    
} catch {
    Write-Host "" -ForegroundColor $Red
    Write-Host "=== DEPLOYMENT FAILED ===" -ForegroundColor $Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor $Red
    Write-Host "" -ForegroundColor $Red
    exit 1
}