import os
import json
import boto3
import uuid
from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException
from collections import defaultdict

s3 = boto3.client('s3')

def fetch_order_history(api, params):
    all_data = []
    next_params = params.copy()


    while True:
        try:
            response = api.get("/api/v2/mix/order/orders-history", next_params)
            data = response.get('data', {}).get('entrustedList') or []
            end_id = response.get('data', {}).get('endId')
            if not data:
                break

            all_data.extend(data)

            if not end_id or end_id == "0":
                break

            next_params = next_params.copy()
            next_params["idLessThan"] = end_id

        except BitgetAPIException as e:
            print(f"Bitget API Exception for params {next_params}: {e}. Returning collected data.")
            break

    return all_data

def group_and_sort_by_symbol(data):
    grouped = defaultdict(list)
    for item in data:
        grouped[item["symbol"]].append(item)
    grouped_sorted = {
        symbol: sorted(items, key=lambda x: int(x["cTime"]), reverse=True)
        for symbol, items in grouped.items()
    }
    return grouped_sorted


def lambda_handler(event, context):
    apiKey = os.environ["API_KEY"]
    secretKey = os.environ["API_SECRET"]
    passphrase = os.environ["PASSPHRASE"]
    bucket = os.environ["S3_BUCKET"]

    productType = event.get("productType")
    if not productType:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "productType es obligatorio"})
        }

    optional_keys = [
        "symbol",
        "startTime",
        "endTime",
        "orderId",
        "clientOid",
        "idLessThan",
        "orderSource",
        "limit"
    ]

    params = {"productType": productType}
    for key in optional_keys:
        value = event.get(key)
        if value is not None:
            params[key] = value

    print(f"Fetching orders with params: {params}")

    bitget_client = BitgetApi(apiKey, secretKey, passphrase)
    try:
        response_data = fetch_order_history(bitget_client, params)
        
        if not response_data:
            print(f"No orders found for {params['symbol']} in the given time range.")
        
        sorted_response = group_and_sort_by_symbol(response_data)
        
        
        key = (
            f"orders-history/{productType}/{params['symbol']}.json"
        )

        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(sorted_response, indent=2)
        )

        return {
            "statusCode": 200,
            "s3Key": key,
            "bucket": bucket,
            "recordCount": len(sorted_response)
        }

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e
