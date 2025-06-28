
# 📈 Tesla Stock Price Forecasting Dashboard

Unlock the future of Tesla stock prices with this dynamic forecasting dashboard! Combining classic statistical models and advanced deep learning techniques, this tool empowers users to explore, compare, and analyze multiple forecasting approaches—all within a modern, interactive interface.

---

## 🔍 What Makes This Project Unique?

### ✅ Diverse Forecasting Arsenal  
Blends traditional models like **ARIMA**, **SARIMA**, and **Prophet** with powerful deep learning models like **LSTM** and **Bidirectional LSTM**, offering a well-rounded perspective on time series forecasting.

### 🔄 Tailored Comparison Modes  
Easily switch between:
- **All Models View**
- Focused pairwise comparisons (e.g., **Actual vs. LSTM**, **Actual vs. ARIMA**)  
Perfect for performance benchmarking.

### 🎨 Interactive Visuals with Clear Legends  
- Each model is **color-coded** for quick identification  
- **Legend placed outside the chart** for better readability  
- Responsive **Altair charts** allow intuitive exploration

### 📅 Real-Time Date Filtering  
Instantly filter forecasts by date range to perform **temporal analysis** and detect model performance trends over time.

### 🔢 Transparent Forecast Data  
A toggleable section provides access to **raw forecast tables**, allowing users to inspect the exact predictions behind the visuals.

### 🌙 Professional UI  
Built with a **sleek dark theme** and minimalist layout to ensure a clean, user-friendly experience.

---

## 🛠 Tech Stack

| Tool               | Purpose                                 |
|--------------------|------------------------------------------|
| Python 3.7+        | Core programming language                |
| Streamlit          | Web-based dashboard framework            |
| yfinance           | Tesla stock data retrieval               |
| pandas, numpy      | Data manipulation and preprocessing      |
| Altair             | Interactive data visualization           |
| statsmodels        | ARIMA, SARIMA implementations            |
| Prophet (Meta)     | Forecasting with trend and seasonality   |
| TensorFlow/Keras   | Deep learning models (LSTM, BiLSTM)      |

---

## 🎯 How to Use

### 🔹 Clone the Repository
```bash
git clone https://github.com/your-username/tesla-stock-forecasting.git
cd tesla-stock-forecasting
```

### 🔹 Install Required Libraries
```bash
pip install -r requirements.txt
```

### 🔹 Launch the Dashboard
```bash
streamlit run streamlit_app.py
```

### 🔹 Interact with the App
- Use the **sidebar** to filter by date or model
- **Hover over the chart** for data tooltips
- Expand **"Show Raw Data"** to see actual forecast values

---

## 🌐 Live Demo

Try the app instantly without installation:  
🔗 [Streamlit Cloud App](https://timeseries-8tadzglttnvakkfwxujcgj.streamlit.app/)

---

## 🗂 Project Structure

```
tesla-stock-forecasting/
├── forecast_data/         # CSV files with actual & predicted prices
├── streamlit_app.py       # Main Streamlit dashboard
├── generate_forecast_data.py # Script to simulate and save forecasts
├── requirements.txt       # Required Python libraries
└── README.md              # Project documentation (this file)
```

---

## 🤝 Contributions & Feedback

This project thrives on collaboration!  
- Open an issue for bugs or feature requests  
- Submit a pull request to improve code or UI  
- Share your suggestions to help make this dashboard even better

---
