# 💹 Crypto Tracker & Trading System

A full-featured cryptocurrency trading platform built with Python and Streamlit that enables users to track real-time crypto prices, manage their portfolio, buy/sell coins, and monitor profit/loss. The app uses CoinGecko API for live market data and integrates with a MySQL backend for persistent user transactions.

## 🧠 Features
- 🔐 User Authentication (Signup/Login)
- 📈 Live Crypto Price Tracking via CoinGecko API
- 💰 Buy & Sell Cryptocurrency with real-time validation
- 🧾 Portfolio Dashboard with profit/loss calculation
- 📉 Sell History with visual performance
- 💸 Withdraw INR balance using UPI ID
- 🎯 Caching for efficient API usage
- 📊 Historical price trends with Matplotlib

## 🛠 Tech Stack
- Python
- Streamlit
- MySQL
- CoinGecko API
- Matplotlib
- Pandas

## 🚀 How to Run
1. Install dependencies:
   ```bash
   pip install streamlit mysql-connector-python requests matplotlib pandas

   streamlit run main.py

