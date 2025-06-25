from utils import get_all_metrics, get_residuals, check_residual_white_noise
import numpy as np
import streamlit as st

# Page setup
st.set_page_config(page_title="Stock Forecasting Dashboard", layout="wide")
# Metrics for Prophet
# Define actual_prophet and prophet_forecast['yhat'] with your actual data
# Example dummy data for demonstration; replace with your real data
actual_prophet = np.linspace(180, 200, 30)
prophet_forecast = {'yhat': actual_prophet + np.random.normal(0, 3, 30)}

metrics = get_all_metrics(actual_prophet, prophet_forecast['yhat'])
residuals = get_residuals(actual_prophet, prophet_forecast['yhat'])
p_value = check_residual_white_noise(residuals)

st.write("Prophet R² Score:", round(metrics['R2'], 3))
st.write("Residuals are random?" , "✅ Yes" if p_value > 0.05 else "❌ No")





# app.py
# Streamlit app for stock forecasting dashboard
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import plotly.graph_objects as go



# Dummy preloaded values — replace these with actual variables from your notebook
# You must import actual_forecast and actuals for each model
model_names = ["Prophet", "ARIMA", "SARIMA", "LSTM"]

# Example: Use your actual and predicted values from models
# Replace these with your real predictions and actuals (last 30 days)
actual_prophet = np.linspace(180, 200, 30)
predicted_prophet = actual_prophet + np.random.normal(0, 3, 30)
actual_arima = np.linspace(180, 200, 30)
predicted_arima = actual_arima + np.random.normal(0, 4, 30)
predicted_sarima = actual_arima + np.random.normal(0, 5, 30)
actual_lstm = np.linspace(180, 200, 30)
predicted_lstm = actual_lstm + np.random.normal(0, 2, 30)


# Now dynamically compute all metrics using utils.py
prophet_metrics = get_all_metrics(actual_prophet, predicted_prophet)
arima_metrics = get_all_metrics(actual_arima, predicted_arima)
sarima_metrics = get_all_metrics(actual_arima, predicted_sarima)
lstm_metrics = get_all_metrics(actual_lstm, predicted_lstm)
results = {
    "Model": ["Prophet", "ARIMA", "SARIMA", "LSTM"],
    "MAE": [prophet_metrics["MAE"], arima_metrics["MAE"], sarima_metrics["MAE"], lstm_metrics["MAE"]],
    "RMSE": [prophet_metrics["RMSE"], arima_metrics["RMSE"], sarima_metrics["RMSE"], lstm_metrics["RMSE"]],
    "MAPE": [prophet_metrics["MAPE"], arima_metrics["MAPE"], sarima_metrics["MAPE"], lstm_metrics["MAPE"]],
    "R2": [prophet_metrics["R2"], arima_metrics["R2"], sarima_metrics["R2"], lstm_metrics["R2"]]
}
df_results = pd.DataFrame(results)

# Dummy forecast lines — replace with real outputs later
# Use 30 dummy values to simulate
actual_values = np.linspace(180, 200, 30)
forecast_dict = {
    "Prophet": actual_values + np.random.normal(0, 3, 30),
    "ARIMA": actual_values + np.random.normal(0, 4, 30),
    "SARIMA": actual_values + np.random.normal(0, 5, 30),
    "LSTM": actual_values + np.random.normal(0, 2, 30),
}

# Navigation
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Overview", "📊 Model Comparison", "📈 Forecast Visuals", "📉 Residuals"])

# -------------------------------
with tab1:
    st.title("📈 Time Series Stock Forecasting Dashboard")
    st.markdown("""
    Welcome to the advanced multi-model dashboard. This project compares four time series models:
    - **ARIMA**
    - **SARIMA**
    - **Prophet**
    - **LSTM**

    The goal is to evaluate their performance on stock price forecasting (last 30 days).

    Navigate through the tabs to explore visual comparisons, metrics, and model behavior.
    """)

# -------------------------------
with tab2:
    st.header("📊 Model Comparison Table")
    st.dataframe(df_results.style.highlight_max(axis=0, color="lightgreen"))

    st.subheader("📉 Error Metric Comparison")

    metric = st.selectbox("Select metric to compare", ["MAE", "RMSE", "MAPE", "R2"])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=model_names, y=df_results[metric], marker_color='indigo'))
    fig.update_layout(title=f"{metric} Comparison", xaxis_title="Model", yaxis_title=metric)
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
with tab3:
    st.header("📈 Forecast vs Actual")

    model_choice = st.selectbox("Select Model", model_names)
    pred = forecast_dict[model_choice]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(y=actual_values, mode='lines+markers', name='Actual', line=dict(color='orange')))
    fig2.add_trace(go.Scatter(y=pred, mode='lines+markers', name='Forecast', line=dict(color='green')))
    fig2.update_layout(title=f"{model_choice} Forecast vs Actual", xaxis_title="Day", yaxis_title="Price")
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
with tab4:
    st.header("📉 Residual Plot (Forecast Error)")
    model_choice = st.selectbox("Select Model for Residuals", model_names, key="residual_model")
    residuals = actual_values - forecast_dict[model_choice]

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(y=residuals, mode='lines+markers', name='Residuals'))
    fig3.add_hline(y=0, line_dash="dash", line_color="black")
    fig3.update_layout(title=f"{model_choice} Residuals (Actual - Forecast)", xaxis_title="Day", yaxis_title="Error")
    st.plotly_chart(fig3, use_container_width=True)
