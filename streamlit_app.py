import streamlit as st
import pandas as pd
import altair as alt
import os

# 🔠 Page config and CSS styling
st.set_page_config(page_title="📈 Tesla Forecast Dashboard", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #2e4053;
    }
    .main > div {
        background-color: #2e4053 !important;
    }
    .block-container {
        padding: 1rem 2rem;
    }
    .dataframe-container {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 1px 5px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# 🚗 Title
st.title(":red_car: Tesla Stock Price - 30 Days Forecast Comparison Dashboard")

# Load forecast data
def load_data(model_name):
    file_path = f"forecast_data/{model_name}_forecast.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, parse_dates=["Date"])
        df['Model'] = model_name
        return df
    return pd.DataFrame()

# Models
model_list = ["Actual", "ARIMA", "SARIMA", "Prophet", "LSTM", "BiLSTM"]
data_frames = [load_data(model) for model in model_list]
data = pd.concat(data_frames, ignore_index=True)

if data.empty:
    st.error("No forecast data found in 'forecast_data/' directory.")
    st.stop()

data['Price'] = pd.to_numeric(data['Price'], errors='coerce')
data.dropna(subset=["Price"], inplace=True)
data.set_index("Date", inplace=True)
data.sort_index(inplace=True)

# 🗓️ Sidebar Controls
st.sidebar.header("🗓️ Filter and Compare")
min_date = data.index.min().date()
max_date = data.index.max().date()
start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

if start_date >= end_date:
    st.error("⚠️ End date must be after start date.")
    st.stop()

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
data = data.loc[start_date:end_date]

# Select comparison models using radio buttons
comparison_mode = st.sidebar.radio("Compare Models", options=[
    "All Models", "Actual vs LSTM", "Actual vs ARIMA", "Actual vs BiLSTM", "Actual vs SARIMA", "Actual vs Prophet"])

if comparison_mode == "Actual vs LSTM":
    models_to_show = ["Actual", "LSTM"]
elif comparison_mode == "Actual vs ARIMA":
    models_to_show = ["Actual", "ARIMA"]
elif comparison_mode == "Actual vs BiLSTM":
    models_to_show = ["Actual", "BiLSTM"]
elif comparison_mode == "Actual vs SARIMA":
    models_to_show = ["Actual", "SARIMA"]
elif comparison_mode == "Actual vs Prophet":
    models_to_show = ["Actual", "Prophet"]
else:
    models_to_show = model_list

data_filtered = data[data["Model"].isin(models_to_show)]

# 📊 Altair Chart
chart_data = data_filtered.reset_index().melt(
    id_vars=["Date", "Model"],
    value_vars=["Price"],
    var_name="ValueType",
    value_name="Value"
).dropna(subset=["Value"])

nearest = alt.selection(type='single', nearest=True, on='mouseover', fields=['Date'], empty='none')

line_chart = alt.Chart(df_chart).mark_line(interpolate='monotone').encode(
    x=alt.X("Date:T", title="Date"),
    y=alt.Y("Value:Q", title="Price"),
    color=alt.Color("Model:N", title="Model")
)

selectors = alt.Chart(df_chart).mark_point(opacity=0).encode(
    x="Date:T",
    y="Value:Q",
).add_selection(nearest)

tooltips = alt.Chart(df_chart).mark_rule().encode(
    x="Date:T",
    y="Value:Q",
    tooltip=[
        alt.Tooltip("Date:T", title="Date"),
        alt.Tooltip("Value:Q", title="Price"),
        alt.Tooltip("Model:N", title="Model")
    ],
    color=alt.Color("Model:N", legend=None)
).transform_filter(nearest)

chart = (line_chart + selectors + tooltips).properties(

    width=900,
    height=500,
    title="📊 Model Forecast Comparison (Hover to Inspect)",
    background="#d0d3d4"
).interactive()

st.altair_chart(chart, use_container_width=True)

# 📋 Show Raw Data
with st.expander("📋 Show Raw Data"):
    st.markdown("<div class='dataframe-container'>", unsafe_allow_html=True)
    st.dataframe(data_filtered.sort_index())
    st.markdown("</div>", unsafe_allow_html=True)
