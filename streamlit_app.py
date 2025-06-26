import streamlit as st
import pandas as pd
import altair as alt
import os

# 💠 Background color using CSS
st.set_page_config(page_title="📈 Tesla Forecast Dashboard", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #f2f2f7;
    }
    .main > div {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 Tesla Stock Price - 30 Days Forecast Comparison Dashboard")

# Load forecast CSVs
def load_data(model_name):
    file_path = f"forecast_data/{model_name}_forecast.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, parse_dates=["Date"])
        df["Model"] = model_name
        return df
    return pd.DataFrame()

# Model list and loading
model_list = ["Actual", "ARIMA", "SARIMA", "Prophet", "LSTM", "BiLSTM"]
data_frames = [load_data(model) for model in model_list]
data = pd.concat(data_frames, ignore_index=True)

if data.empty:
    st.error("No forecast data files found in 'forecast_data/' directory.")
    st.stop()

data['Price'] = pd.to_numeric(data['Price'], errors='coerce')
data.dropna(subset=["Price"], inplace=True)
data.set_index("Date", inplace=True)
data.sort_index(inplace=True)

# 📅 Date filter
st.sidebar.header("📅 Filter by Date")
min_date = data.index.min().date()
max_date = data.index.max().date()
start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

if start_date >= end_date:
    st.error("⚠️ End date must be after start date.")
    st.stop()

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
data_filtered = data.loc[start_date:end_date]

# 📦 Model Comparison Buttons in Container
st.subheader("📊 Select Model Comparison")
with st.container():
    col1, col2, col3 = st.columns(3)
    compare_mode = st.session_state.get("compare_mode", "All")

    if col1.button("Actual vs LSTM"):
        compare_mode = "Actual_LSTM"
    if col1.button("Actual vs ARIMA"):
        compare_mode = "Actual_ARIMA"
    if col2.button("Actual vs BiLSTM"):
        compare_mode = "Actual_BiLSTM"
    if col2.button("Actual vs SARIMA"):
        compare_mode = "Actual_SARIMA"
    if col3.button("Actual vs Prophet"):
        compare_mode = "Actual_Prophet"
    if col3.button("All Models"):
        compare_mode = "All"

# Save current state
st.session_state.compare_mode = compare_mode

# 🔘 Model filter logic
if compare_mode == "Actual_LSTM":
    models_to_show = ["Actual", "LSTM"]
elif compare_mode == "Actual_ARIMA":
    models_to_show = ["Actual", "ARIMA"]
elif compare_mode == "Actual_BiLSTM":
    models_to_show = ["Actual", "BiLSTM"]
elif compare_mode == "Actual_SARIMA":
    models_to_show = ["Actual", "SARIMA"]
elif compare_mode == "Actual_Prophet":
    models_to_show = ["Actual", "Prophet"]
else:
    models_to_show = model_list

data_filtered = data_filtered[data_filtered["Model"].isin(models_to_show)]

# 🎯 Forecast value inspector
st.sidebar.header("🎯 Forecast Value Inspector")
model_selected = st.sidebar.selectbox("Select Model", options=[m for m in model_list if m != "Actual"])
forecast_only = data_filtered[data_filtered["Model"] == model_selected]
forecast_only = forecast_only["Price"].dropna()
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

# 📈 Prepare chart
df_chart = data_filtered.reset_index().melt(
    id_vars=["Date", "Model"],
    value_vars=["Price"],
    var_name="ValueType",
    value_name="Value"
).dropna(subset=["Value"])

nearest = alt.selection(type='single', nearest=True, on='mouseover', fields=['Date'], empty='none')

line_chart = alt.Chart(df_chart).mark_line().encode(
    x=alt.X('Date:T', title='Date'),
    y=alt.Y('Value:Q', title='Price'),
    color=alt.Color('Model:N', title='Model'),
    tooltip=['Date:T', 'Model:N', alt.Tooltip('Value:Q', title='Price')]
)

selectors = alt.Chart(df_chart).mark_point().encode(
    x='Date:T',
    opacity=alt.value(0),
).add_selection(nearest)

points = alt.Chart(df_chart).mark_circle(size=50).encode(
    x='Date:T',
    y='Value:Q',
    color='Model:N'
).transform_filter(nearest)

text = alt.Chart(df_chart).mark_text(align='left', dx=5, dy=-5).encode(
    x='Date:T',
    y='Value:Q',
    text=alt.Text('Value:Q', format=".2f"),
    color='Model:N'
).transform_filter(nearest)

rules = alt.Chart(df_chart).mark_rule(color='gray').encode(
    x='Date:T'
).transform_filter(nearest)

chart = (line_chart + selectors + points + rules + text).properties(
    width=900,
    height=500,
    title="📈 Model Forecast Comparison (Hover to Inspect)"
).interactive()

# 🔴 Highlight selected point
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

# 📋 Raw data view
with st.expander("📋 Show Raw Data"):
    st.dataframe(data_filtered.sort_index())
