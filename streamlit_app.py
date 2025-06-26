import streamlit as st
import pandas as pd
import altair as alt
import os

# 💠 Page config and CSS styling
st.set_page_config(page_title="📈 Tesla Forecast Dashboard", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #2e4053;
    }
    .main > div {
        background-color: #2e4053;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .legend-container {
        background-color: #ecf0f1;
        padding: 10px 20px;
        border-radius: 10px;
        margin-top: 20px;
        box-shadow: 0 1px 5px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# 🚗 Title
st.title("🚗 Tesla Stock Price - 30 Days Forecast Comparison Dashboard")

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

# 📅 Date Filter
st.sidebar.header("📅 Filter by Date")
min_date = data.index.min().date()
max_date = data.index.max().date()
start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

if start_date >= end_date:
    st.error("⚠️ End date must be after start date.")
    st.stop()

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
data_filtered = data.loc[start_date:end_date]

# 📦 Model Comparison Buttons
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

st.session_state.compare_mode = compare_mode

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

# 🎯 Forecast Value Inspector
st.sidebar.header("🎯 Forecast Value Inspector")
model_selected = st.sidebar.selectbox("Select Model", options=[m for m in model_list if m != "Actual"])
forecast_only = data_filtered[data_filtered["Model"] == model_selected]["Price"].dropna()

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

# 📈 Altair Chart
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

# 🔴 Highlight selected forecast date
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

# Display chart
st.altair_chart(chart, use_container_width=True)

# 📘 Legend in White Box
with st.container():
    st.markdown("""
    <div class="legend-container">
        <h4 style='color:#007BFF;'>📘 Legend</h4>
        <ul>
            <li><b>Actual</b> – Real Tesla stock prices</li>
            <li><b>LSTM</b> – Long Short-Term Memory forecast</li>
            <li><b>ARIMA</b> – Autoregressive Integrated Moving Average</li>
            <li><b>BiLSTM</b> – Bidirectional LSTM forecast</li>
            <li><b>SARIMA</b> – Seasonal ARIMA forecast</li>
            <li><b>Prophet</b> – Meta’s Prophet model forecast</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# 📋 Show Raw Data
with st.expander("📋 Show Raw Data"):
    st.dataframe(data_filtered.sort_index())
