import os
from huggingface_hub import HfApi
from dotenv import load_dotenv

load_dotenv()
api = HfApi(token=os.getenv("HF_token"))

try:
    api.upload_file(
        path_or_fileobj="../model/annual_sarimax_model.pkl",
        path_in_repo="annual_sarimax_model.pkl",
        repo_id="mongare70/ElectroTech-Sales-Volume-model",
        repo_type="model",
    )

    api.upload_file(
        path_or_fileobj="../model/monthly_sarimax_model.pkl",
        path_in_repo="monthly_sarimax_model.pkl",
        repo_id="mongare70/ElectroTech-Sales-Volume-model",
        repo_type="model",
    )

    api.upload_file(
        path_or_fileobj="../model/quarterly_sarimax_model.pkl",
        path_in_repo="quarterly_sarimax_model.pkl",
        repo_id="mongare70/ElectroTech-Sales-Volume-model",
        repo_type="model",
    )

    api.upload_file(
        path_or_fileobj="../model/weekly_sarimax_model.pkl",
        path_in_repo="weekly_sarimax_model.pkl",
        repo_id="mongare70/ElectroTech-Sales-Volume-model",
        repo_type="model",
    )
except Exception as e:
    print(f"Upload failed: {str(e)}")
