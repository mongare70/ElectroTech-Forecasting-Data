import streamlit as st
import requests
import pandas as pd
from datetime import date
import plotly.express as px
import os
from dotenv import load_dotenv


load_dotenv()
API_URL = os.getenv("API_URL")

if not API_URL:
    raise ValueError("API_URL environment variable is not set")


st.set_page_config(
    page_title="ElectroTech Forecast",
    page_icon="💻",
    layout="wide"
)

st.markdown(
    """
    <style>
        .main { padding-top: 1rem; }
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            height: 3rem;
            font-size: 1.1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

## Sidebar
st.sidebar.title("⚙ Settings")

steps = st.sidebar.slider("Forecast horizon", 1, 30, 7)
start_date = st.sidebar.date_input("Forecast start date", value=date.today())

st.sidebar.markdown("---")
st.sidebar.caption("ElectroTech Analytics © 2025")

st.title("💻 ElectroTech Sales Volume Forecast")
st.markdown(
    "Predict sales volume using historical sales trends and pricing data."
)

# Tabs
tab_weekly, tab_monthly, tab_quarterly = st.tabs(
    ["📅 Weekly Forecast", "📅 Monthly Forecast", "📆 Quarterly Forecast"]
)

# Shared Payload builder
def build_payload(
    lag_type,
    category,
    season,
    sales_lag30,
    sales_lag7,
    sales_lag1,
    price_lag30,
    price_lag7,
    price_lag1,
    price_current,
):
    # Schema keys:
    # "Sales_Volume_lag30", "Sales_Volume_lag7", "Sales_Volume_lag1"
    # "Price_lag30", "Price_lag7", "Price_lag1", "Price"
    # "Category_...", "Season_..."
    
    return {
        "steps": int(steps),
        "date": start_date.isoformat(),
        "lag": lag_type,
        "features": {
            f"Category_{category}": 1,
            f"Season_{season}": 1,
            
            "Sales_Volume_lag30": sales_lag30,
            "Sales_Volume_lag7": sales_lag7,
            "Sales_Volume_lag1": sales_lag1,
            
            "Price_lag30": price_lag30,
            "Price_lag7": price_lag7,
            "Price_lag1": price_lag1,
            "Price": price_current,
        },
    }


def forecast_form(form_key):
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", ["Accessories", "Laptop", "Smartphone", "Tablet"], key=f"{form_key}_cat")
    with col2:
        season = st.selectbox("Season", ["Fall", "Spring", "Winter", "Summer"], key=f"{form_key}_season")

    st.markdown("### 📊 Historical Sales Volume")
    
    s1, s2, s3 = st.columns(3)
    with s1:
        sales_lag1 = st.number_input(f"Sales Volume (Lag 1)", 0, value=100, step=1, key=f"{form_key}_sales_1")
    with s2:
        sales_lag7 = st.number_input(f"Sales Volume (Lag 7)", 0, value=110, step=1, key=f"{form_key}_sales_7")
    with s3:
        sales_lag30 = st.number_input(f"Sales Volume (Lag 30)", 0, value=120, step=1, key=f"{form_key}_sales_30")

    st.markdown("### 🏷️ Historical & Current Price")
    
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        price_lag1 = st.number_input(f"Price (Lag 1)", 0.0, value=227.0, step=1.0, key=f"{form_key}_price_1")
    with p2:
        price_lag7 = st.number_input(f"Price (Lag 7)", 0.0, value=227.0, step=1.0, key=f"{form_key}_price_7")
    with p3:
        price_lag30 = st.number_input(f"Price (Lag 30)", 0.0, value=227.0, step=1.0, key=f"{form_key}_price_30")
    with p4:
        price_current = st.number_input(f"Price (Current)", 0.0, value=227.0, step=1.0, key=f"{form_key}_price_curr")

    return (
        category, season,
        sales_lag30, sales_lag7, sales_lag1,
        price_lag30, price_lag7, price_lag1, price_current
    )

# Weekly
with tab_weekly:
    with st.form("weekly_form"):
        st.markdown("### 📅 Weekly Forecast")
        data_w = forecast_form("weekly")
        submitted_weekly = st.form_submit_button("🚀 Run Weekly Forecast")

# Monthly
with tab_monthly:
    with st.form("monthly_form"):
        data = forecast_form("monthly")
        submitted_monthly = st.form_submit_button("🚀 Run Monthly Forecast")

# Quarterly
with tab_quarterly:
    with st.form("quarterly_form"):
        data_q = forecast_form("quarterly")
        submitted_quarterly = st.form_submit_button("🚀 Run Quarterly Forecast")

# Submission Handler
if submitted_weekly or submitted_monthly or submitted_quarterly:

    if submitted_weekly:
        payload = build_payload("W", *data_w)
        freq = "W"
    elif submitted_monthly:
        payload = build_payload("M", *data)
        freq = "M"
    elif submitted_quarterly:
        payload = build_payload("Q", *data_q)
        freq = "Q"

    with st.spinner("Generating forecast…"):
        try:
            response = requests.post(f"{API_URL}predict", json=payload)

            if response.status_code != 200:
                st.error(f"Error {response.status_code}: {response.text}")
            else:
                result = response.json()
                preds = result.get("predictions", [])

                if not preds:
                    st.warning("No forecast returned.")
                else:
                    dates = pd.date_range(start=start_date, periods=len(preds), freq=freq)
                    df = pd.DataFrame({"Date": dates, "Sales Volume Forecast": preds})

                    fig = px.line(
                        df,
                        x="Date",
                        y="Sales Volume Forecast",
                        markers=True,
                        title="Sales Volume Forecast"
                    )

                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df, use_container_width=True)
                    
                    if "missing_features" in result and result["missing_features"]:
                        st.info(f"Note: {len(result['missing_features'])} features were auto-filled with 0: {result['missing_features']}")
                        
        except Exception as e:
            st.error(f"Failed to connect to API: {str(e)}")