# Extrator Bitget

This project is an extractor for Bitget data, likely involving API interactions to fetch and process information from the Bitget exchange. It appears to be structured as a FastAPI application with AWS Lambda functions for various tasks.

## Project Structure

- `bitget-layer/`: Contains Python dependencies and the Bitget API client.
- `coordinator/`: Likely a Lambda function responsible for coordinating data extraction tasks.
- `fastapi_app/`: The main FastAPI application.
- `fetch_orders/`: Another Lambda function, possibly for fetching order-related data.
- `json_extract/`: This folder contains examples of downloaded JSON data.

## Getting Started

To get started with this project, you need to install the dependencies. The dependencies are managed in a central `requirements.txt` file. The `requirements.txt` files in the subdirectories reference the central one.

### Prerequisites

This project requires the AWS Serverless Application Model (SAM) CLI. Please ensure it is installed and configured in your environment.

### Installation

To install the dependencies for a specific function, navigate to the function's directory and run the following command:

```bash
pip install -r requirements.txt
```

For example, to install the dependencies for the `fetch_orders` function, you would run:

```bash
cd fetch_orders
pip install -r requirements.txt
```
