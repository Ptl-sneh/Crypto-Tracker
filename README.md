# Crypto Tracker

A comprehensive cryptocurrency tracking and trading platform built with Python and Streamlit. This application allows users to track cryptocurrency prices, manage portfolios, and simulate buying/selling of cryptocurrencies with real-time market data.

## 🚀 Features

- **User Authentication**: Secure login and registration system
- **Real-time Crypto Data**: Live cryptocurrency prices and market data from CoinGecko API
- **Portfolio Management**: Track your cryptocurrency investments and performance
- **Buy/Sell Functionality**: Simulated cryptocurrency trading with profit/loss tracking
- **Price Charts**: Interactive price trend visualization for each cryptocurrency
- **Transaction History**: Complete record of all buy/sell transactions
- **Balance Management**: Add funds and withdraw earnings
- **Responsive Design**: Clean, user-friendly interface built with Streamlit

## 🛠️ Technology Stack

- **Backend**: Python 3.x
- **Web Framework**: Streamlit
- **Database**: MySQL
- **API**: CoinGecko API for cryptocurrency data
- **Data Visualization**: Matplotlib, Pandas
- **Database Connector**: mysql-connector-python

## 📋 Prerequisites

Before running this application, ensure you have:

- Python 3.7 or higher installed
- MySQL Server installed and running
- Git (for cloning the repository)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd Crypto-Tracker
```

### 2. Create Virtual Environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

1. Create a MySQL database named `crypto_tracker`:

```sql
CREATE DATABASE crypto_tracker;
```

2. Create the necessary tables by running the following SQL commands:

```sql
USE crypto_tracker;

-- Users table
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    pwd VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phnnum VARCHAR(15),
    balance DECIMAL(15,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Buy transactions table
CREATE TABLE buycrypto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    cryptoname VARCHAR(100) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    buyingprice DECIMAL(20,8) NOT NULL,
    amountpaid DECIMAL(15,2) NOT NULL,
    buy_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES user(username)
);

-- Sell transactions table
CREATE TABLE sellcrypto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    cryptoname VARCHAR(100) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    sellingprice DECIMAL(20,8) NOT NULL,
    buyingprice DECIMAL(20,8) NOT NULL,
    total_sell_amount DECIMAL(15,2) NOT NULL,
    gain_loss DECIMAL(15,2) NOT NULL,
    sell_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES user(username)
);

-- Withdrawals table
CREATE TABLE withdrawals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    upi_id VARCHAR(100) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    withdrawal_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES user(username)
);
```

### 5. Configure Database Connection

Update the database connection in `db.py` with your MySQL credentials:

```python
# db.py
conn = mysql.connector.connect(
    host="localhost",
    user="your_username",  # Change this
    password="your_password",  # Change this
    database="crypto_tracker"
)
```

## 🎯 Usage

### Starting the Application

```bash
streamlit run main.py
```

The application will open in your default web browser at `http://localhost:8501`

### Application Flow

1. **Registration/Login**: Create an account or login with existing credentials
2. **Dashboard**: Main navigation hub with access to all features
3. **View Crypto**: Browse available cryptocurrencies with detailed information and price charts
4. **Buy Crypto**: Purchase cryptocurrencies using your account balance
5. **Sell Crypto**: Sell your cryptocurrency holdings
6. **Portfolio**: View your investment portfolio with profit/loss calculations
7. **Transaction History**: Review your buy/sell transaction history
8. **Balance Management**: Add funds to your account or withdraw earnings

## 📁 Project Structure

```
Crypto-Tracker/
├── main.py          # Main application file with Streamlit UI and business logic
├── db.py            # Database connection and configuration
├── requirements.txt # Python dependencies
├── .gitignore       # Git ignore file
└── README.md        # Project documentation
```

## 🔧 Key Components

### Database Schema

- **user**: Stores user information and account balances
- **buycrypto**: Records cryptocurrency purchase transactions
- **sellcrypto**: Records cryptocurrency sale transactions with profit/loss calculations
- **withdrawals**: Tracks fund withdrawal requests

### API Integration

The application uses the CoinGecko API to fetch:
- Real-time cryptocurrency prices
- Market capitalization data
- Historical price data for charts
- 24-hour high/low prices

### Security Features

- Password authentication
- Session management with Streamlit
- Input validation for transactions
- Balance verification before transactions

## 🚨 Important Notes

- This is a simulation application - no real cryptocurrency transactions occur
- All financial transactions are simulated within the application
- The application uses real-time cryptocurrency prices from CoinGecko API
- Ensure your MySQL server is running before starting the application
- Keep your database credentials secure

## 📊 Features in Detail

### User Management
- Secure registration and login system
- Balance tracking and management
- Transaction history per user

### Cryptocurrency Tracking
- Real-time price updates (cached for performance)
- Detailed cryptocurrency information
- Interactive price charts (30-day history)
- Market cap and trading volume data

### Trading Features
- Buy cryptocurrencies with account balance
- Sell cryptocurrencies with profit/loss calculation
- Portfolio diversification tracking
- Transaction history with timestamps

### Financial Management
- Add funds to account
- Withdraw earnings via UPI
- Balance verification before transactions
- Comprehensive profit/loss reporting

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Ensure MySQL server is running
   - Verify database credentials in `db.py`
   - Check if database `crypto_tracker` exists

2. **API Rate Limiting**:
   - Application uses caching to minimize API calls
   - If issues persist, wait and retry

3. **Dependency Issues**:
   - Ensure all packages from requirements.txt are installed
   - Use virtual environment to avoid conflicts

### Performance Tips

- The application caches API responses to reduce load on CoinGecko API
- Database queries are optimized for performance
- Use the refresh button to update prices when needed

## 📈 Future Enhancements

Potential improvements for future versions:
- Real cryptocurrency trading integration
- Advanced charting with more timeframes
- Price alerts and notifications
- Multi-currency support
- Mobile app version
- Advanced analytics and reporting
- Social features and portfolio sharing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and demonstration purposes.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Ensure all prerequisites are met
3. Verify database configuration

---

**Note**: This application uses simulated trading - no real financial transactions occur. Always exercise caution when dealing with real cryptocurrency investments.
