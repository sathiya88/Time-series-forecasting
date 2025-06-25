import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="📈 Tesla Forecast Dashboard", layout="wide")
st.title(" 🚗Tesla Stock Price 30 days Forecast Dashboard")

# Load data
data = pd.read_csv("lstm_forecast_30days.csv", parse_dates=["Date"])
data.set_index("Date", inplace=True)
data['Price'] = pd.to_numeric(data['Price'], errors='coerce')
data.dropna(subset=["Price"], how="all", inplace=True)

# Date Range Filter
st.sidebar.header("📅 Filter by Date")
min_date = data.index.min().date()
max_date = data.index.max().date()
start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

if start_date >= end_date:
    st.error("⚠️ End date must be after start date.")
    st.stop()

data_filtered = data.loc[str(start_date):str(end_date)]

# Forecast Point Selector
st.sidebar.header("🎯 Highlight Forecast Point")
forecast_only = data_filtered[data_filtered['Type'] == 'Forecast']
forecast_only = forecast_only['Price'].dropna()
forecast_date = None
selected_price = None

if not forecast_only.empty:
    forecast_date_input = st.sidebar.slider(
        "Select Date on Forecast Line",
        min_value=forecast_only.index.min().date(),
        max_value=forecast_only.index.max().date(),
        value=forecast_only.index.min().date(),
        format="YYYY-MM-DD"
    )
    forecast_date = pd.to_datetime(forecast_date_input)
    if forecast_date in forecast_only.index:
        selected_price = forecast_only.loc[forecast_date]
        st.sidebar.write(f"Forecast Price on {forecast_date.date()}: **${selected_price:.2f}**")

# Plotting
df_chart = data_filtered.reset_index().melt(
    id_vars=['Date', 'Type'],
    value_vars=['Price'],
    var_name='ValueType',
    value_name='Value'
).dropna(subset=['Value'])

chart = alt.Chart(df_chart).mark_line().encode(
    x=alt.X('Date:T', title='Date'),
    y=alt.Y('Value:Q', title='Price'),
    color='Type:N',
    tooltip=['Date:T', alt.Tooltip('Value:Q', title='Price'), 'Type:N']
).properties(
    title="Stock Price: Actual vs Forecast"
).interactive()

if forecast_date and selected_price is not None:
    highlight_point = alt.Chart(pd.DataFrame({
        'Date': [forecast_date],
        'Value': [selected_price],
        'Type': ['Forecast']
    })).mark_circle(size=100, color='red').encode(
        x='Date:T',
        y='Value:Q',
        tooltip=[alt.Tooltip('Date:T'), alt.Tooltip('Value:Q', title='Selected Forecast Price')]
    )
    chart += highlight_point

st.altair_chart(chart, use_container_width=True)

# Show raw data
if st.checkbox("Show raw data"):
    st.dataframe(data_filtered)
