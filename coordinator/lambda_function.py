import json
import boto3
import os
from datetime import datetime, timedelta

sfn_client = boto3.client("stepfunctions", region_name="us-east-1")
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

def generate_daily_tasks(productType, symbols):
    tasks = []
    now = datetime.utcnow()
    for symbol in symbols:
        tasks.append({
            "symbol": symbol,
            "productType": productType
        })
    return tasks

def lambda_handler(event, context):
    try:
        productType = event.get("productType")
        symbols = event.get("symbols", [])
        
        if not productType:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing productType in payload"})}
        
        if not symbols:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing symbols list in payload"})}

        tasks = generate_daily_tasks(productType, symbols)

        input_data = {
            "productType": productType,
            "tasks": tasks
        }

        response = sfn_client.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(input_data)
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Execution started for {len(symbols)} symbols.",
                "executionArn": response["executionArn"]
            })
        }

    except Exception as e:
        print(f"Error starting Step Function: {e}")
        return {"statusCode": 500, "body": str(e)}
