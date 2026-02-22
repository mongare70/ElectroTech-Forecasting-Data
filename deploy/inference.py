from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
import pickle
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Union
from dotenv import load_dotenv
import os
import requests
from io import BytesIO

load_dotenv()

app = FastAPI(title="ElectroTech API")

WEEKLY_MODEL = None
MONTHLY_MODEL = None
QUARTERLY_MODEL = None

FEATURE_SCHEMA = None

@app.on_event("startup")
def load_artifacts():
    global WEEKLY_MODEL, MONTHLY_MODEL, QUARTERLY_MODEL, FEATURE_SCHEMA
    
    # Load schema file
    # Try multiple possible paths
    schema_paths = [
        Path("model/sarimax_schema.json"),
        Path("../model/sarimax_schema.json"),
        Path(__file__).parent.parent / "model" / "sarimax_schema.json"
    ]
    
    schema_loaded = False
    for schema_path in schema_paths:
        if schema_path.exists():
            try:
                with open(schema_path, 'r') as f:
                    FEATURE_SCHEMA = json.load(f)
                print(f"✓ Schema loaded from: {schema_path.absolute()}")
                schema_loaded = True
                break
            except Exception as e:
                print(f"Error loading schema from {schema_path}: {str(e)}")
    
    if not schema_loaded:
        print("⚠ Warning: Schema file not found. Please ensure sarimax_schema.json exists.")


    
    # Try loading models from local files first (from .env paths)
    weekly_model_path = os.getenv("WEEKLY_MODEL_PATH")
    monthly_model_path = os.getenv("MONTHLY_MODEL_PATH")
    quarterly_model_path = os.getenv("QUARTERLY_MODEL_PATH")


    # Load weekly model
    if weekly_model_path:
        weekly_path = Path(weekly_model_path)
        print(weekly_path)
        if weekly_path.exists():
            try:
                with open(weekly_path, 'rb') as f:
                    WEEKLY_MODEL = pickle.load(f)
                print(f"✓ Weekly model loaded from: {weekly_path.absolute()}")
            except Exception as e:
                print(f"⚠ Error loading weekly model from {weekly_path}: {str(e)}")
        else:
            print(f"⚠ Weekly model path not found: {weekly_path.absolute()}")

    # Load monthly model
    if monthly_model_path:
        monthly_path = Path(monthly_model_path)
        if monthly_path.exists():
            try:
                with open(monthly_path, 'rb') as f:
                    MONTHLY_MODEL = pickle.load(f)
                print(f"✓ Monthly model loaded from: {monthly_path.absolute()}")
            except Exception as e:
                print(f"⚠ Error loading monthly model from {monthly_path}: {str(e)}")
        else:
            print(f"⚠ Monthly model path not found: {monthly_path.absolute()}")


    # Load quarterly model
    if quarterly_model_path:
        quarterly_path = Path(quarterly_model_path)
        if quarterly_path.exists():
            try:
                with open(quarterly_path, 'rb') as f:
                    QUARTERLY_MODEL = pickle.load(f)
                print(f"✓ Quarterly model loaded from: {quarterly_path.absolute()}")
            except Exception as e:
                print(f"⚠ Error loading quarterly model from {quarterly_path}: {str(e)}")
        else:
            print(f"⚠ Quarterly model path not found: {quarterly_path.absolute()}")

    
    # If models not loaded from local files, try downloading from Hugging Face
    if WEEKLY_MODEL is None or MONTHLY_MODEL is None or QUARTERLY_MODEL is None:
        weekly_hf_url = os.getenv("WEEKLY_MODEL_HUGGINGFACE_URL")
        monthly_hf_url = os.getenv("MONTHLY_MODEL_HUGGINGFACE_URL")
        quarterly_hf_url = os.getenv("QUARTERLY_MODEL_HUGGINGFACE_URL")

        if weekly_hf_url and WEEKLY_MODEL is None:
            try:
                print(f"Attempting to download weekly model from Hugging Face...")
                response = requests.get(weekly_hf_url, timeout=60)
                response.raise_for_status()
                WEEKLY_MODEL = pickle.load(BytesIO(response.content))
                print("✓ Weekly model downloaded from Hugging Face")
            except Exception as e:
                print(f"⚠ Error downloading weekly model from Hugging Face: {str(e)}")

        if monthly_hf_url and MONTHLY_MODEL is None:
            try:
                print(f"Attempting to download monthly model from Hugging Face...")
                response = requests.get(monthly_hf_url, timeout=60)
                response.raise_for_status()
                MONTHLY_MODEL = pickle.load(BytesIO(response.content))
                print("✓ Monthly model downloaded from Hugging Face")
            except Exception as e:
                print(f"⚠ Error downloading monthly model from Hugging Face: {str(e)}")
        
        if quarterly_hf_url and QUARTERLY_MODEL is None:
            try:
                print(f"Attempting to download quarterly model from Hugging Face...")
                response = requests.get(quarterly_hf_url, timeout=60)
                response.raise_for_status()
                QUARTERLY_MODEL = pickle.load(BytesIO(response.content))
                print("✓ Quarterly model downloaded from Hugging Face")
            except Exception as e:
                print(f"⚠ Error downloading quarterly model from Hugging Face: {str(e)}")
    
    # Final check
    if WEEKLY_MODEL is None:
        print("✗ ERROR: Weekly model could not be loaded. Please check your configuration.")
    if MONTHLY_MODEL is None:
        print("✗ ERROR: Monthly model could not be loaded. Please check your configuration.")
    if QUARTERLY_MODEL is None:
        print("✗ ERROR: Quarterly model could not be loaded. Please check your configuration.")
    if FEATURE_SCHEMA is None:
        print("✗ ERROR: Feature schema could not be loaded. Please check your configuration.")


class PredictRequest(BaseModel):
    steps: int = Field(default=1, ge=1, description="Number of time steps to forecast")
    date: str = Field(default="2025-12-08", description="Start date of predictions in YYYY-MM-DD format")
    lag: str = Field(default="W", description="Type of lag to use: 'W' for weekly or 'M' for monthly or 'Q' for quarterly")
    features: Dict[str, Union[int, float]] = Field(
        ..., 
        description="Dictionary of feature names and their values"
    )
    
    @validator('date')
    def validate_date(cls, v):
        """Validate that the date string is in a valid format"""
        if not v or v.lower() == "string" or v.strip() == "":
            raise ValueError("Date field cannot be empty or 'string'. Please provide a valid date in YYYY-MM-DD format (e.g., 2025-12-08).")
        
        try:
            parsed_date = pd.to_datetime(v)
            # Return the date in ISO format to ensure consistency
            return parsed_date.strftime('%Y-%m-%d')
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid date format: '{v}'. Expected format: YYYY-MM-DD (e.g., 2025-12-08). Original error: {str(e)}")
    
    @validator('lag')
    def validate_lag(cls, v):
        """Validate that lag is either 'W' or'M' or 'Q'"""
        if v not in ['W', 'M', 'Q']:
            raise ValueError(f"Invalid lag type: '{v}'. Must be 'M' for monthly or 'Q' for quarterly.")
        return v


@app.post("/predict")
def predict(request: PredictRequest):
    """Make predictions with automatic feature reindexing"""
    
    # Check if models are loaded
    if WEEKLY_MODEL is None or MONTHLY_MODEL is None or QUARTERLY_MODEL is None:
        raise HTTPException(
            status_code=503, 
            detail="Models not loaded. Please check your configuration and ensure model files are accessible."
        )
    
    if FEATURE_SCHEMA is None:
        raise HTTPException(
            status_code=503, 
            detail="Schema not loaded. Please check if sarimax_schema.json exists in the model directory."
        )

    try:
        # Parse the date (already validated by Pydantic, but ensure it's parsed correctly)
        try:
            start_date = pd.to_datetime(request.date)
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format: '{request.date}'. Please provide a date in YYYY-MM-DD format (e.g., 2025-12-08). Error: {str(e)}"
            )

        # Validate and create date range
        try:
            future_index = pd.date_range(start=start_date, periods=request.steps, freq=request.lag)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date range parameters. Steps: {request.steps}, Lag: {request.lag}. Error: {str(e)}"
            )

        exog_df = pd.DataFrame(
            [request.features] * request.steps,
            index=future_index
        )

        exog_df = exog_df.reindex(columns=FEATURE_SCHEMA, fill_value=0)

        if request.lag == "W":
            model = WEEKLY_MODEL
        elif request.lag == "M":
            model = MONTHLY_MODEL
        elif request.lag == "Q":
            model = QUARTERLY_MODEL
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid lag type. Please use 'W' for weekly or 'M' for monthly 'Q' for quartely."
            )
        forecast = model.forecast(steps=request.steps, exog=exog_df)

        predictions = [max(0, round(pred)) for pred in forecast.tolist()]

        missing_features = [
            f for f in FEATURE_SCHEMA
            if f not in request.features.keys()
        ]

        print(predictions)

        return {
            "predictions": predictions,
            "steps": request.steps,
            "features_used": list(exog_df.columns),
            "features_provided": list(request.features.keys()),
            "missing_features": missing_features,
            "note": f"{len(missing_features)} features were auto-filled with 0"
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Handle value errors (e.g., date parsing issues)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        # Handle all other exceptions
        error_type = type(e).__name__
        error_msg = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error ({error_type}): {error_msg}"
        )


if __name__ == "__main__":
    import uvicorn

    print("\nFastAPI running:")
    print("• Bound to: http://0.0.0.0:8000  (Docker / network)")
    print("• Open in browser: http://127.0.0.1:8000")
    print("• Docs: http://127.0.0.1:8000/docs\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)