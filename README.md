# Bitget Data Extractor

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/siiluis)

This project is a scalable serverless application designed to extract historical order data from the Bitget exchange. It leverages **FastAPI** as the entry point and orchestrates data fetching using **AWS Step Functions** and **AWS Lambda**.

## 🚀 Features

- **Serverless Architecture:** Built with AWS SAM (Serverless Application Model).
- **Orchestration:** Uses AWS Step Functions to manage parallel data fetching tasks.
- **REST API:** FastAPI interface to trigger extractions and monitor health.
- **Data Storage:** Automatically saves extracted data to AWS S3.
- **Scalable:** Designed to handle large volumes of data by splitting tasks.

## 📂 Project Structure

- **`fastapi_app/`**: The main API entry point.
- **`coordinator/`**: Lambda function that generates extraction tasks for the Step Function.
- **`fetch_orders/`**: Lambda function that interacts with Bitget API to fetch order history.
- **`collector/`**: Lambda function that aggregates results (optional).
- **`bitget-layer/`**: Shared Lambda Layer containing common dependencies and the Bitget API client.
- **`template.yaml`**: AWS SAM template defining infrastructure as code.

## 🛠️ Prerequisites

- **Python 3.12+**
- **AWS CLI** configured with appropriate permissions.
- **AWS SAM CLI** for deployment.
- **Bitget API Keys** (Key, Secret, Passphrase).

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/siiluis007/extrator-bitget.git
   cd extrator-bitget
   ```

2. **Install Dependencies:**
   Each function has its own `requirements.txt`. For local development, you can create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r fastapi_app/requirements.txt
   ```

## 🚀 Deployment

1. **Build the application:**
   ```bash
   sam build
   ```

2. **Deploy to AWS:**
   ```bash
   sam deploy --guided
   ```
   Follow the prompts to configure your stack name and API keys.

## 🔗 API Usage

Once deployed, you can interact with the API:

- **Health Check:** `GET /health`
- **Start Extraction:** `POST /extract-orders/`
  ```json
  {
    "productType": "USDT-FUTURES",
    "symbols": ["BTCUSDT", "ETHUSDT"]
  }
  ```

## 🧡 Support

If you find this project useful, consider supporting its development!

<a href="https://buymeacoffee.com/siiluis" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="45" alt="Buy Me A Coffee">
</a>
