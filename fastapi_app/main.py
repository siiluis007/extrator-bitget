from fastapi import FastAPI, Query
import boto3
import os
import json
from mangum import Mangum
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Bitget API",
    description="FastAPI con Lambda Coordinadora y Step Functions para obtener historial de órdenes",
    version="1.0.0",
    openapi_url="/Prod/openapi.json",
    docs_url="/Prod/docs",
    contact={
        "name": "Luis Sarmiento",
        "email": "tuemail@dominio.com",
    },
    license_info={
        "name": "MIT License",
    },
)

lambda_client = boto3.client("lambda")
COORDINATOR_LAMBDA_ARN = os.environ["COORDINATOR_LAMBDA_ARN"]

class HistoryRequest(BaseModel):
    productType: str
    symbols: List[str]

@app.get("/")
def root():
    return {"message": "FastAPI + Lambda + Step Functions"}

@app.get("/orders")
def get_orders(productType: str = Query(..., description="Tipo de producto, por ejemplo 'usdt-futures'")):
    payload = {"productType": productType}

    response = lambda_client.invoke(
        FunctionName=COORDINATOR_LAMBDA_ARN,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    result = json.loads(response["Payload"].read())
    return result


@app.post("/get-history")
def get_history(req: HistoryRequest):
    response = lambda_client.invoke(
        FunctionName=COORDINATOR_LAMBDA_ARN,
        InvocationType="RequestResponse",
        Payload=req.json(),
    )
    result = json.loads(response["Payload"].read())
    return result

handler = Mangum(app)
