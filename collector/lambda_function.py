import os
import json
import boto3

s3 = boto3.client("s3")


def collect_all_orders(master_json):
    grouped_orders = {}

    for task in master_json.get("tasks", []):
        bucket = task["bucket"]
        key = task["s3Key"]

        if task.get("orders_count", 0) == 0:
            continue

        response = s3.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8")

        try:
            data = json.loads(content)
            if "orders" in data:
                for order in data["orders"]:
                    symbol = order.get("symbol", "UNKNOWN")
                    if symbol not in grouped_orders:
                        grouped_orders[symbol] = {"orders": [], "orders_count": 0}
                    grouped_orders[symbol]["orders"].append(order)
                    grouped_orders[symbol]["orders_count"] += 1
        except json.JSONDecodeError:
            continue

    total_orders = sum(v["orders_count"] for v in grouped_orders.values())
    return {"symbols": grouped_orders, "total_orders": total_orders}


def lambda_handler(event, context):
    bucket = os.environ["S3_BUCKET"]
    product_type = event.get("productType")
    tasks = event.get("tasks", [])

    if not product_type:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "productType is required"})
        }

    output_key = f"orders-history/{product_type}/{product_type}_orders.json"

    try:
        result = collect_all_orders({"tasks": tasks})

        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json.dumps(result, indent=2),
            ContentType="application/json"
        )

        return {
            "statusCode": 200,
            "s3Key": output_key,
            "bucket": bucket,
            "total_orders": result["total_orders"]
        }

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
