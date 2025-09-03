from fastapi import FastAPI, Query
import boto3
import os
import json
from mangum import Mangum
from pydantic import BaseModel
from typing import List

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

lambda_client = boto3.client("lambda")
COORDINATOR_LAMBDA_ARN = os.environ["COORDINATOR_LAMBDA_ARN"]

class HistoryRequest(BaseModel):
    productType: str
    symbols: List[str]

@app.get("/health")
def root():
    return {"messages": "API is healthy"}

@app.post("/extract-orders/")
async def extract_orders(request: HistoryRequest):
    response = lambda_client.invoke(
        FunctionName=COORDINATOR_LAMBDA_ARN,
        InvocationType="RequestResponse",
        Payload=request.json()
    )
    return {"executionArn": "response['executionArn']"}


handler = Mangum(app)
