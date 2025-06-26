import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(page_title="📈 Tesla Forecast Dashboard", layout="wide")
st.title("🚗 Tesla Stock Price - 30 Days Forecast Comparison Dashboard")

# Load data from multiple forecast models
def load_data(model_name):
    file_path = f"forecast_data/{model_name}_forecast.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, parse_dates=["Date"])
        df['Model'] = model_name
        return df
    else:
        return pd.DataFrame()

# List of all models used
model_list = ["Actual", "ARIMA", "SARIMA", "Prophet", "LSTM", "BiLSTM"]
data_frames = [load_data(model) for model in model_list]
data = pd.concat(data_frames, ignore_index=True)

# Preprocessing
if data.empty:
    st.error("No forecast data files found in 'forecast_data/' directory.")
    st.stop()

# Drop rows with missing prices and convert types
data['Price'] = pd.to_numeric(data['Price'], errors='coerce')
data.dropna(subset=["Price"], inplace=True)
data.set_index("Date", inplace=True)
data.sort_index(inplace=True)

# Sidebar date filtering
st.sidebar.header("📅 Filter by Date")
min_date = data.index.min().date()
max_date = data.index.max().date()
start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

if start_date >= end_date:
    st.error("⚠️ End date must be after start date.")
    st.stop()

# Convert to pandas datetime with time to ensure proper slicing
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)

data_filtered = data.loc[start_date:end_date]

# Sidebar: Forecast highlight per model
st.sidebar.header("🎯 Forecast Value Inspector")
model_selected = st.sidebar.selectbox("Select Model", options=[m for m in model_list if m != "Actual"])
forecast_only = data_filtered[data_filtered['Model'] == model_selected]
forecast_only = forecast_only['Price'].dropna()
forecast_date = None
selected_price = None

if not forecast_only.empty:
    forecast_date_input = st.sidebar.slider(
        "Select Forecast Date",
        min_value=forecast_only.index.min().date(),
        max_value=forecast_only.index.max().date(),
        value=forecast_only.index.min().date(),
        format="YYYY-MM-DD"
    )
    forecast_date = pd.to_datetime(forecast_date_input)
    if forecast_date in forecast_only.index:
        selected_price = forecast_only.loc[forecast_date]
        st.sidebar.write(f"{model_selected} Forecast on {forecast_date.date()}: **${selected_price:.2f}**")

# Prepare data for Altair chart
df_chart = data_filtered.reset_index().melt(
    id_vars=["Date", "Model"],
    value_vars=["Price"],
    var_name="ValueType",
    value_name="Value"
).dropna(subset=['Value'])

chart = alt.Chart(df_chart).mark_line().encode(
    x=alt.X('Date:T', title='Date'),
    y=alt.Y('Value:Q', title='Price'),
    color=alt.Color('Model:N', title="Model"),
    tooltip=['Date:T', alt.Tooltip('Value:Q', title='Price'), 'Model:N']
).properties(
    title="Stock Price Forecasts by Model"
).interactive()

# Add highlight point for selected forecast date and price
if forecast_date and selected_price is not None:
    highlight_point = alt.Chart(pd.DataFrame({
        'Date': [forecast_date],
        'Value': [selected_price],
        'Model': [model_selected]
    })).mark_circle(size=100, color='red').encode(
        x='Date:T',
        y='Value:Q',
        tooltip=[alt.Tooltip('Date:T'), alt.Tooltip('Value:Q', title='Forecast Price')]
    )
    chart += highlight_point

st.altair_chart(chart, use_container_width=True)

# Optional raw data table
if st.checkbox("Show raw data"):
    st.dataframe(data_filtered.sort_index())
