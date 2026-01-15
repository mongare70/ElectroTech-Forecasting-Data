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

# ✅ Lag selector (schema compliant)
lag_option = st.sidebar.selectbox(
    "Lagged feature reference",
    ["Yesterday", "Last week", "Last month"]
)

LAG_MAP = {
    "Yesterday": "lag1",
    "Last week": "lag7",
    "Last month": "lag30",
}

lag_suffix = LAG_MAP[lag_option]

st.sidebar.markdown("---")
st.sidebar.caption("ElectroTech Analytics © 2025")

st.title("💻 ElectroTech Sales Volume Forecast")
st.markdown(
    "Predict sales volume using operational context, category or seasonal features."
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
    product_spec,
    competitor_lag,
    confidence_lag,
    trend_lag,
    price_lag,
    sales_lag,
    competitor_actual,
    confidence_actual,
    trend_actual,
    price_actual,
    sales_current,
):
    return {
        "steps": int(steps),
        "date": start_date.isoformat(),
        "lag": lag_type,
        "features": {
            f"Category_{category}": 1,
            f"Season_{season}": 1,
            f"Product_Specification_2_{product_spec}": 1,

            # ✅ Lagged features (schema correct)
            f"Competitor_Activity_Score_{lag_suffix}": competitor_lag,
            f"Consumer_Confidence_Index_{lag_suffix}": confidence_lag,
            f"Market_Trend_Index_{lag_suffix}": trend_lag,
            f"Price_{lag_suffix}": price_lag,
            f"Sales_Volume_{lag_suffix}": sales_lag,

            # ✅ Current features
            "Competitor_Activity_Score": competitor_actual,
            "Consumer_Confidence_Index": confidence_actual,
            "Market_Trend_Index": trend_actual,
            "Price": price_actual,
            "Total_Amount": price_actual * sales_current,
        },
    }


def forecast_form(form_key):
    col1, col2, col3 = st.columns(3)
    with col1:
        category = st.selectbox("Category", ["Accessories", "Laptop", "Smartphone", "Tablet"], key=f"{form_key}_cat")
    with col2:
        season = st.selectbox("Season", ["Fall", "Spring", "Winter", "Summer"], key=f"{form_key}_season")
    with col3:
        product = st.selectbox(
            "Product Specification",
            ["High-Resolution", "Lightweight", "Long-Battery-Life"],
            key=f"{form_key}_prod"
        )

    st.markdown("### 🧮 Lagged Operational Indicators")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        comp_lag = st.number_input(f"Competitor Activity Score ({lag_option})", 0.0, 1.0, 0.6, 0.01)
    with c2:
        conf_lag = st.number_input(f"Consumer Confidence Index ({lag_option})", 0.0, 1.0, 0.6, 0.01)
    with c3:
        trend_lag = st.number_input(f"Market Trend Index ({lag_option})", 0.0, 1.0, 0.6, 0.01)
    with c4:
        price_lag = st.number_input(f"Price (£, {lag_option})", 0.0, value=227.0, step=1.0)

    st.markdown("### 📊 Historical Sales Data")
    sales_lag = st.number_input(f"Sales Volume ({lag_option})", 0, value=100, step=1, key=f"{form_key}_sales_lag")
    
    st.markdown("### 📈 Current Sales Data")
    sales_current = st.number_input("Sales Volume (current)", 0, value=100, step=1, key=f"{form_key}_sales_current")

    st.markdown("### 🛏 Current Values")

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        trend_actual = st.number_input("Market Trend Index (current)", 0.0, 1.0, 0.6, 0.01)
    with a2:
        comp_actual = st.number_input("Competitor Activity Score (current)", 0.0, 1.0, 0.6, 0.01)
    with a3:
        conf_actual = st.number_input("Consumer Confidence Index (current)", 0.0, 1.0, 0.6, 0.01)
    with a4:
        price_actual = st.number_input("Price (£, current)", 0.0, value=227.0, step=1.0)

    return (
        category, season, product,
        comp_lag, conf_lag, trend_lag, price_lag, sales_lag,
        comp_actual, conf_actual, trend_actual, price_actual, sales_current
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
        response = requests.post(f"{API_URL}predict", json=payload)

        if response.status_code != 200:
            st.error(response.text)
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