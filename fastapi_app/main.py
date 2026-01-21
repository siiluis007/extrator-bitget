import os
import boto3
import json
import logging
from fastapi import FastAPI, HTTPException, status
from mangum import Mangum
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI(
    title="Bitget API",
    description="API for fetching historical data using AWS Lambda and Step Functions",
    version="1.0.0",
    license_info={
        "name": "MIT License",
    },
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize AWS Client
lambda_client = boto3.client("lambda")

# Environment Variables
COORDINATOR_LAMBDA_ARN = os.environ.get("COORDINATOR_LAMBDA_ARN")

# --- Models ---

class HistoryRequest(BaseModel):
    productType: str = Field(
        ..., 
        description="Type of product (e.g., USDT-FUTURES, SPOT)",
        example="USDT-FUTURES"
    )
    symbols: List[str] = Field(
        ..., 
        description="List of trading pairs to fetch",
        example=["BTCUSDT", "ETHUSDT"]
    )

class HealthCheckResponse(BaseModel):
    status: str
    message: str

class ExtractionResponse(BaseModel):
    message: str
    execution_arn: str
    details: Dict[str, Any]

# --- Endpoints ---

@app.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    tags=["Health"]
)
def health_check():
    """
    Simple health check endpoint to verify the API is running.
    """
    return {
        "status": "healthy",
        "message": "API is operational"
    }

@app.post(
    "/extract-orders/",
    response_model=ExtractionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Extraction"]
)
async def extract_orders(request: HistoryRequest):
    """
    Triggers the data extraction process via AWS Lambda Coordinator.
    
    - **productType**: The market type (e.g., USDT-FUTURES).
    - **symbols**: A list of symbols to extract data for.
    """
    if not COORDINATOR_LAMBDA_ARN:
        logger.error("COORDINATOR_LAMBDA_ARN environment variable is not set.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: Coordinator ARN missing."
        )

    try:
        logger.info(f"Invoking Coordinator Lambda for {request.productType} - {request.symbols}")
        
        response = lambda_client.invoke(
            FunctionName=COORDINATOR_LAMBDA_ARN,
            InvocationType="RequestResponse", # Wait for initial confirmation
            Payload=request.model_dump_json()
        )
        
        response_payload = json.load(response['Payload'])
        
        if response.get('FunctionError'):
            logger.error(f"Coordinator Lambda failed: {response_payload}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Coordinator failed: {response_payload}"
            )

        return {
            "message": "Extraction process started successfully.",
            "execution_arn": response_payload.get("executionArn", "N/A"),
            "details": response_payload
        }

    except Exception as e:
        logger.exception("Failed to invoke coordinator lambda")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Mangum Handler for AWS Lambda
handler = Mangum(app)
