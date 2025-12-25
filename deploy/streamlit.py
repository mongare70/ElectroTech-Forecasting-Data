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

st.set_page_config(page_title="ElectroTech Forecast", page_icon="💻", layout="wide")

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

st.sidebar.title("⚙ Settings")
st.sidebar.markdown("Configure forecasting options.")

steps = st.sidebar.slider("Forecast horizon (Months)", 1, 30, 7)
start_date = st.sidebar.date_input("Forecast start date", value=date.today())

st.sidebar.markdown("---")
st.sidebar.caption("ElectroTech Analytics © 2025")

st.title("💻 ElectroTech Sales Volume Forecast")
st.markdown(
    "Predict sales volume using operational context, category or season features."
)

# Create tabs for Monthly, Quarterly, and Weekly lags
tab_monthly, tab_quarterly, tab_annually = st.tabs(["📅 Monthly Lag", "📆 Quarterly Lag", "📆 Annual Lag"])


# Monthly Lag Tab
with tab_monthly:
    st.markdown("### 🔧 Input Data")
    
    with st.form("prediction_form_monthly", border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            category_monthly = st.selectbox(
                "Category",
                [
                    "Accessories",
                    "Laptop",
                    "Smartphone",
                    "Tablet",
                ],
                key="category_monthly"
            )
        with col2:
            season_monthly = st.selectbox("Season", ["Fall", "Spring", "Winter", "Summer"], key="season_monthly")
        with col3:
            product_specification_2_monthly = st.selectbox("Product Specification", ["High-Resolution", "Lightweight", "Long-Battery-Life"])

        st.markdown("### 🧮 Operational Indicators (Lagged Features)")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            competitor_activity_score_monthly = st.number_input(
                "Competitor Activity Score (last month)",
                value=0.60,
                step=0.01,
                key="competitor_activity_score_monthly"
            )
        with c2:
            consumer_confidence_index_monthly = st.number_input(
                "Consumer Confidence Index (last month)",
                value=0.60,
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                key="consumer_confidence_index_monthly"
            )
        with c3:
            market_trend_index_monthly = st.number_input(
                "Market Trend Index (last month)",
                value=0.60,
                step=0.01,
                key="market_trend_index_monthly"
            )
        with c4:
            price_monthly = st.number_input(
                "Price (£, last month)", value=227.0, step=1.0, key="price_monthly"
            )

        st.markdown("### 🛏 Actual Values")

        colA, colB, colC, colD = st.columns(4)
        with colA:
            market_trend_index_monthly_actual = st.number_input("Market Trend Index", value=0.60,
                step=0.01, key="market_trend_index_monthly_actual")
        with colB:
            competitor_activity_score_monthly_actual = st.number_input("Competitor Activity Score", value=0.60,
                step=0.01, key="competitor_activity_score_monthly_actual")
        with colC:
            consumer_confidence_index_monthly_actual = st.number_input("Consumer Confidence index", value=0.60,
                min_value=0.0,
                max_value=1.0,
                step=0.01, key="consumer_confidence_index_monthly_actual")
        with colD:
            price_monthly_actual= st.number_input(
                "Price", value=227.0, step=1.0, key="price_monthly_actual"
            )


        st.markdown("---")

        submitted_monthly = st.form_submit_button("🚀 Run Forecast")

# Quarterly Lag Tab
with tab_quarterly:
    st.markdown("### 🔧 Input Data")
    
    with st.form("prediction_form_quarterly", border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            category_quarterly = st.selectbox(
                "Category",
                [
                    "Accessories",
                    "Laptop",
                    "Smartphone",
                    "Tablet",
                ],
                key="category_quarterly"
            )
        with col2:
            season_quarterly = st.selectbox("Season", ["Fall", "Spring", "Winter", "Summer"], key="season_quarterly")
        with col3:
            product_specification_2_quarterly = st.selectbox("Product Specification", ["High-Resolution", "Lightweight", "Long-Battery-Life"])

        st.markdown("### 🧮 Operational Indicators (Lagged Features)")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            competitor_activity_score_quarterly = st.number_input(
                "Competitor Activity Score (last month)",
                value=0.60,
                step=0.01,
                key="competitor_activity_score_quarterly"
            )
        with c2:
            consumer_confidence_index_quarterly = st.number_input(
                "Consumer Confidence Index (last month)",
                value=0.60,
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                key="consumer_confidence_index_quarterly"
            )
        with c3:
            market_trend_index_quarterly = st.number_input(
                "Market Trend Index (last month)",
                value=0.60,
                step=0.01,
                key="market_trend_index_quarterly"
            )
        with c4:
            price_quarterly = st.number_input(
                "Price (£, last month)", value=227.0, step=1.0, key="price_quarterly"
            )

        st.markdown("### 🛏 Actual Values")

        colA, colB, colC, colD = st.columns(4)
        with colA:
            market_trend_index_quarterly_actual = st.number_input("Market Trend Index", value=0.60,
                step=0.01, key="market_trend_index_quarterly_actual")
        with colB:
            competitor_activity_score_quarterly_actual = st.number_input("Competitor Activity Score", value=0.60,
                step=0.01, key="competitor_activity_score_quarterly_actual")
        with colC:
            consumer_confidence_index_quarterly_actual = st.number_input("Consumer Confidence index", value=0.60,
                min_value=0.0,
                max_value=1.0,
                step=0.01, key="consumer_confidence_index_quarterly_actual")
        with colD:
            price_quarterly_actual= st.number_input(
                "Price", value=227.0, step=1.0, key="price_quarterly_actual"
            )


        st.markdown("---")

        submitted_quarterly = st.form_submit_button("🚀 Run Forecast")

# Annual Lag Tab
with tab_annually:
    st.markdown("### 🔧 Input Data")
    
    with st.form("prediction_form_annually", border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            category_annually = st.selectbox(
                "Category",
                [
                    "Accessories",
                    "Laptop",
                    "Smartphone",
                    "Tablet",
                ],
                key="category_annually"
            )
        with col2:
            season_annually = st.selectbox("Season", ["Fall", "Spring", "Winter", "Summer"], key="season_annually")
        with col3:
            product_specification_2_annually = st.selectbox("Product Specification", ["High-Resolution", "Lightweight", "Long-Battery-Life"])

        st.markdown("### 🧮 Operational Indicators (Lagged Features)")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            competitor_activity_score_annually = st.number_input(
                "Competitor Activity Score (last month)",
                value=0.60,
                step=0.01,
                key="competitor_activity_score_annually"
            )
        with c2:
            consumer_confidence_index_annually = st.number_input(
                "Consumer Confidence Index (last month)",
                value=0.60,
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                key="consumer_confidence_index_annually"
            )
        with c3:
            market_trend_index_annually = st.number_input(
                "Market Trend Index (last month)",
                value=0.60,
                step=0.01,
                key="market_trend_index_annually"
            )
        with c4:
            price_annually = st.number_input(
                "Price (£, last month)", value=227.0, step=1.0, key="price_annually"
            )

        st.markdown("### 🛏 Actual Values")

        colA, colB, colC, colD = st.columns(4)
        with colA:
            market_trend_index_annually_actual = st.number_input("Market Trend Index", value=0.60,
                step=0.01, key="market_trend_index_annually_actual")
        with colB:
            competitor_activity_score_annually_actual = st.number_input("Competitor Activity Score", value=0.60,
                step=0.01, key="competitor_activity_score_annually_actual")
        with colC:
            consumer_confidence_index_annually_actual = st.number_input("Consumer Confidence index", value=0.60,
                min_value=0.0,
                max_value=1.0,
                step=0.01, key="consumer_confidence_index_annually_actual")
        with colD:
            price_annually_actual= st.number_input(
                "Price", value=227.0, step=1.0, key="price_annually_actual"
            )


        st.markdown("---")

        submitted_annually = st.form_submit_button("🚀 Run Forecast")

if submitted_monthly:
    # Monthly lag processing
    lag_type = "M"
    lag_suffix = "lag30"

    payload = {
        "steps": int(steps),
        "date": start_date.isoformat(),
        "lag": lag_type,
        "features": {
            f"Category_{category_monthly}": 1,
            f"Season_{season_monthly}": 1,
            f"Product_Specification_2_{product_specification_2_monthly}": 1,
            f"Competitor_Activity_Score_{lag_suffix}": competitor_activity_score_monthly,
            f"Consumer_Confidence_Index_{lag_suffix}": consumer_confidence_index_monthly,
            f"Market_Trend_Index_{lag_suffix}": market_trend_index_monthly,
            f"Price_{lag_suffix}": price_monthly,
            "Market_Trend_Index": market_trend_index_monthly_actual,
            "Competitor_Activity_Score": competitor_activity_score_monthly_actual,
            "Consumer_Confidence_Index": consumer_confidence_index_monthly_actual,
            "Price": price_monthly_actual
        },
    }
    
elif submitted_quarterly:
    # Quarterly lag processing
    lag_type = "Q"
    lag_suffix = "lag30"

    payload = {
        "steps": int(steps),
        "date": start_date.isoformat(),
        "lag": lag_type,
        "features": {
            f"Category_{category_quarterly}": 1,
            f"Season_{season_quarterly}": 1,
            f"Product_Specification_2_{product_specification_2_quarterly}": 1,
            f"Competitor_Activity_Score_{lag_suffix}": competitor_activity_score_quarterly,
            f"Consumer_Confidence_Index_{lag_suffix}": consumer_confidence_index_quarterly,
            f"Market_Trend_Index_{lag_suffix}": market_trend_index_quarterly,
            f"Price_{lag_suffix}": price_quarterly,
            "Market_Trend_Index": market_trend_index_quarterly_actual,
            "Competitor_Activity_Score": competitor_activity_score_quarterly_actual,
            "Consumer_Confidence_Index": consumer_confidence_index_quarterly_actual,
            "Price": price_quarterly_actual
        },
    }

elif submitted_annually:
    # Annual lag processing
    lag_type = "Y"
    lag_suffix = "lag30"

    payload = {
        "steps": int(steps),
        "date": start_date.isoformat(),
        "lag": lag_type,
        "features": {
            f"Category_{category_annually}": 1,
            f"Season_{season_annually}": 1,
            f"Product_Specification_2_{product_specification_2_annually}": 1,
            f"Competitor_Activity_Score_{lag_suffix}": competitor_activity_score_annually,
            f"Consumer_Confidence_Index_{lag_suffix}": consumer_confidence_index_annually,
            f"Market_Trend_Index_{lag_suffix}": market_trend_index_annually,
            f"Price_{lag_suffix}": price_annually,
            "Market_Trend_Index": market_trend_index_annually_actual,
            "Competitor_Activity_Score": competitor_activity_score_annually_actual,
            "Consumer_Confidence_Index": consumer_confidence_index_annually_actual,
            "Price": price_annually_actual
        },
    }


if submitted_monthly or submitted_quarterly or submitted_annually:

    with st.spinner("Generating forecast…"):
        try:
            response = requests.post(f"{API_URL}predict", json=payload)

            if response.status_code == 200:
                result = response.json()
                forecast_values = result.get("predictions", [])

                st.success("Forecast generated successfully! ✅")
                st.markdown(f"## 📊 Forecast: **")

                if forecast_values:
                    # Use appropriate frequency based on lag type
                    freq = lag_type if lag_type in ["M", "Q", "Y"] else "Y"
                    dates = pd.date_range(
                        start=start_date, periods=len(forecast_values), freq=freq
                    )

                    df = pd.DataFrame(
                        {
                            "Date": dates,
                            "Sales Volume forecast": forecast_values,
                        }
                    )

                    if len(forecast_values) == 1:
                        st.markdown("## 🧮 Predicted Sales Volume for Selected Day")
                        st.markdown(
                            f"""
                            <div style="
                                background-color:#f0f2f6;
                                padding:30px;
                                border-radius:10px;
                                text-align:center;
                                margin-bottom:20px;
                            ">
                                <h1 style="font-size:64px; margin:0;">{forecast_values[0]}</h1>
                                <p style="font-size:20px; margin-top:10px;">
                                    Sales Volume forecast for <b>{dates[0].strftime("%Y-%m-%d")}</b>
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown("### 📈 Multi-day Forecast Overview")

                        fig = px.line(
                            df,
                            x="Date",
                            y="Sales Volume forecast",
                            markers=True,
                            title="Sales Volume Forecast Over Time",
                        )

                        fig.update_layout(
                            xaxis_title="Date",
                            yaxis_title="Forecasted Sales Volume",
                            template="plotly_white",
                            paper_bgcolor="white",
                            plot_bgcolor="white",
                            height=450,
                            hovermode="x unified",
                        )

                        st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(df, use_container_width=True)

                else:
                    st.warning("No forecast data returned from the API.")

            else:
                st.error(f"API error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"Request failed: {e}")
