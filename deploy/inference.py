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

MONTHLY_MODEL = None
QUARTERLY_MODEL = None
ANNUAL_MODEL = None

FEATURE_SCHEMA = None

@app.on_event("startup")
def load_artifacts():
    global MONTHLY_MODEL, QUARTERLY_MODEL, ANNUAL_MODEL, FEATURE_SCHEMA
    
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
    monthly_model_path = os.getenv("MONTHLY_MODEL_PATH")
    quarterly_model_path = os.getenv("QUARTERLY_MODEL_PATH")
    annual_model_path = os.getenv("ANNUAL_MODEL_PATH")


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


    # Load annual model
    if annual_model_path:
        annual_path = Path(annual_model_path)
        if annual_path.exists():
            try:
                with open(annual_path, 'rb') as f:
                    ANNUAL_MODEL = pickle.load(f)
                print(f"✓ Annual model loaded from: {annual_path.absolute()}")
            except Exception as e:
                print(f"⚠ Error loading annual model from {annual_path}: {str(e)}")
        else:
            print(f"⚠ Annual model path not found: {annual_path.absolute()}")

    
    # If models not loaded from local files, try downloading from Hugging Face
    if MONTHLY_MODEL is None or QUARTERLY_MODEL is None or ANNUAL_MODEL is None:
        monthly_hf_url = os.getenv("MONTHLY_MODEL_HUGGINGFACE_URL")
        quarterly_hf_url = os.getenv("QUARTERLY_MODEL_HUGGINGFACE_URL")
        annual_hf_url = os.getenv("ANNUAL_MODEL_HUGGINGFACE_URL")

        
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

        if annual_hf_url and ANNUAL_MODEL is None:
            try:
                print(f"Attempting to download annual model from Hugging Face...")
                response = requests.get(annual_hf_url, timeout=60)
                response.raise_for_status()
                ANNUAL_MODEL = pickle.load(BytesIO(response.content))
                print("✓ Annual model downloaded from Hugging Face")
            except Exception as e:
                print(f"⚠ Error downloading annual model from Hugging Face: {str(e)}")
    
    # Final check
    if MONTHLY_MODEL is None:
        print("✗ ERROR: Monthly model could not be loaded. Please check your configuration.")
    if QUARTERLY_MODEL is None:
        print("✗ ERROR: Quarterly model could not be loaded. Please check your configuration.")
    if ANNUAL_MODEL is None:
        print("✗ ERROR: Annual model could not be loaded. Please check your configuration.")
    if FEATURE_SCHEMA is None:
        print("✗ ERROR: Feature schema could not be loaded. Please check your configuration.")


class PredictRequest(BaseModel):
    steps: int = Field(default=1, ge=1, description="Number of time steps to forecast")
    date: str = Field(default="2025-12-08", description="Start date of predictions in YYYY-MM-DD format")
    lag: str = Field(default="Y", description="Type of lag to use: 'M' for monthly or 'Q' for quarterly or 'Y' for annually")
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
        """Validate that lag is either 'M' or 'Q' or 'Y'"""
        if v not in ['M', 'Q', 'Y']:
            raise ValueError(f"Invalid lag type: '{v}'. Must be 'M' for monthly or 'Q' for quarterly or 'Y' for annually.")
        return v


@app.post("/predict")
def predict(request: PredictRequest):
    """Make predictions with automatic feature reindexing"""
    
    # Check if models are loaded
    if MONTHLY_MODEL is None or QUARTERLY_MODEL is None or ANNUAL_MODEL is None:
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

        if request.lag == "M":
            model = MONTHLY_MODEL
        elif request.lag == "Q":
            model = QUARTERLY_MODEL
        elif request.lag == "Y":
            model = ANNUAL_MODEL
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid lag type. Please use 'M' for monthly 'Q' for quartely or 'Y' for annually."
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
    uvicorn.run(app, host="0.0.0.0", port=8000)