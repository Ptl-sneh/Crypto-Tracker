import streamlit as st
from db import conn, cursor
import requests
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import decimal


# USER CLASS 
# UserExists
# register
# login

# Cache API responses to reduce API calls

@st.cache_data(ttl=60)
def get_cached_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "inr", "order": "market_cap_desc", "per_page": "100", "page": "1", "sparkline": "false"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.warning("⚠️ API Error: Using last cached data.")
        return []

@st.cache_data(ttl=300)
def get_cached_historical_data(crypto_id):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    params = {"vs_currency": "inr", "days": "30", "interval": "daily"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

class User:
    def __init__(self, username, pwd, email="", phone=""):
        self.un = username
        self.pwd = pwd
        self.email = email
        self.phone = phone
        
    # checks user is exists or not
    
    def userExists(self):
        """Check if user exists in database"""
        cursor.execute("SELECT * FROM user WHERE username = %s", (self.un,))
        return cursor.fetchone() is not None

    # sign up
    
    def register(self):
        if self.userExists():
            return False  
        cursor.execute("INSERT INTO user (username, pwd, email, phnnum) VALUES (%s, %s, %s, %s)", (self.un, self.pwd, self.email, self.phone))
        conn.commit()
        return True 

    # login

    def login(self):
        """Authenticate user"""
        cursor.execute("SELECT * FROM user WHERE username = %s AND pwd = %s", (self.un, self.pwd))
        return cursor.fetchone() is not None 
    
    # Check Balance
    
    def checkBalance(self):
        cursor.execute("SELECT balance FROM user WHERE username = %s", (self.un,))
        result = cursor.fetchone()
        return result[0] if result else 0
    
    # Withdraw
    
    def withdraw(self, upi_id, amount):
        """Withdraw amount using UPI ID."""
        balance = self.checkBalance()
        
        if amount > balance:
            return False, "Insufficient balance!"

        try:
            cursor.execute("UPDATE user SET balance = balance - %s WHERE username = %s", (amount, self.un))
            
            cursor.execute("INSERT INTO withdrawals (username, upi_id, amount) VALUES (%s, %s, %s)",(self.un, upi_id, amount))
            
            conn.commit()
            return True, f"₹{amount} withdrawn successfully to {upi_id}!"
        except Exception as e:
            return False, f"Error: {e}"


# CRYPTO MANAGER

class CryptoManager:
    
    # get crypto
    
    def get_crypto_data(self):
        return get_cached_crypto_data()
    
    # get historical data for graph
    
    def get_historical_data(self, crypto_id):
        return get_cached_historical_data(crypto_id)

if "page" not in st.session_state:
    st.session_state.page = "Login"
    
# Switch Page

def switch_page(page):
    st.session_state.page = page
    st.rerun()


# Signup Page

def signup_page():
    st.title("Signup Page")

    new_username = st.text_input("Enter a Username")
    new_email = st.text_input("Enter Email")
    new_phone = st.text_input("Enter Phone Number")
    new_password = st.text_input("Enter a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Signup"):
        if new_password != confirm_password:
            st.warning("Passwords do not match!")
        else:
            user = User(new_username, new_password, new_email, new_phone)
            if user.register():
                st.session_state.username = new_username
                st.session_state.password = new_password
                st.session_state.email = new_email
                st.session_state.phone = new_phone
                st.success("Signup Successful! Please login.")
                switch_page("Login")  
            else:
                st.warning("Username already exists! Try a different one.")

    st.button("Already have an account? Login", on_click=lambda: switch_page("Login"))


#  Login Page


def login_page():
    st.title("Login Page")
    
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        user = User(username, password)
        if user.login():
            st.session_state.username = username
            st.success(f"Welcome {username}!")
            st.session_state.page = "Dashboard"  
            st.rerun() 
        else:
            st.warning("Invalid username or password! Try again or Sign up.")

    st.button("Don't have an account? Signup", on_click=lambda: switch_page("Signup"))


#  Dashboard Page

# pages redirection


def dashboard():
    st.title("Welcome to Crypto Tracker")


    st.button("View Crypto", on_click=lambda: switch_page("view_crypto"))
    st.button("Buy Crypto", on_click=lambda: switch_page("buy_crypto"))
    st.button("Sell Crypto", on_click=lambda: switch_page("sell_crypto"))
    st.button("View Portfolio", on_click=lambda: switch_page("view_portfolio"))
    st.button("View Sell History", on_click=lambda: switch_page("sell_history"))

    if st.button("Logout"):
        switch_page("Login")
        

# View Crypto Page
        

def see_Details(data,crypto,manager):
    found = False
    for coin in data:
        if coin['name'] == crypto:
            st.write(f"Name: {coin['name']}")
            st.write(f"Symbol: {coin['symbol'].upper()}")
            st.write(f"Price (INR): ₹{coin['current_price']}")
            st.write(f"Market Cap: ₹{coin['market_cap']}")
            st.write(f"24H High: ₹{coin['high_24h']}")
            st.write(f"24H Low: ₹{coin['low_24h']}")
            st.write(f"All time high: ₹{coin['ath']}")
            st.write(f"All time low: ₹{coin['atl']}")
            
            historical_data = manager.get_historical_data(coin['id'])
            if historical_data:
                prices = historical_data["prices"]
                dates = [datetime.datetime.fromtimestamp(price[0] / 1000).date() for price in prices]
                values = [price[1] for price in prices]

                plt.figure(figsize=(10, 5))
                plt.plot(dates, values, marker='o', linestyle='-', color='b', label=coin['name'])
                plt.xlabel("Date")
                plt.ylabel("Price (INR)")
                plt.title(f"{coin['name']} Price Trend (Last 30 Days)")
                plt.xticks(rotation=45)
                plt.legend()
                plt.grid()
                st.pyplot(plt)
            else:
                st.warning("Historical data unavailable for this cryptocurrency.")
            
            found = True
            break
    if not found:
        st.warning("Cryptocurrency not found!")
        


def view_crypto():
    manager = CryptoManager()
    st.title("Crypto Currencies")
    data = manager.get_crypto_data()
    
    df = st.dataframe(width=1000, data=[{"Name": crypto["name"]}for crypto in data])
    
    if "crypto_input" not in st.session_state:
        st.session_state.crypto_input = ""

    crypto = st.text_input("Enter the cryptocurrency name to view details:", key="crypto_input")

    if st.button("Search"):
        if crypto:
            see_Details(data,crypto,manager)
        else:
            st.warning("Please enter a cryptocurrency name.")
    if st.button("Back"):
        switch_page("Dashboard")


# buy crypto


def buy_crypto():
    st.title("Buy Cryptocurrency")

    # Ensure user is logged in
    if "username" not in st.session_state:
        st.error("Please login first!")
        if st.button("Go to Login"):
            st.session_state["page"] = "Login"
            st.rerun()
        return

    username = st.session_state.username
    user = User(username, "")
    balance = user.checkBalance()

    # checks the balance

    if balance == 0:
        st.warning("Your balance is ₹0. Please add funds first!")
        if st.button("Add Balance"):
            switch_page("add_balance")
        return

    manager = CryptoManager()
    data = manager.get_crypto_data()

    if not data:
        st.warning("⚠️ No cryptocurrency data available. Try again later.")
        return

    crypto_names = [coin["name"] for coin in data]

    # Reset session state variables if not set
    # It is for refreshing the page
    
    if "crypto_choice" not in st.session_state:
        st.session_state["crypto_choice"] = crypto_names[0]

    if "investment_amount" not in st.session_state:
        st.session_state["investment_amount"] = 0.0

    # Select cryptocurrency
    
    selected_crypto = st.selectbox("Select Cryptocurrency to Buy:", crypto_names, key="crypto_choice")

    if st.button("Refresh Prices 🔄"):
        st.rerun()

    selected_coin = next((coin for coin in data if coin["name"] == selected_crypto), None)

    
    # Display selected cryptocurrency details
    
    if selected_coin:
        st.write(f"**Name:** {selected_coin['name']}")
        st.write(f"**Symbol:** {selected_coin['symbol'].upper()}")
        st.write(f"**Current Price (INR):** ₹{selected_coin['current_price']}")
        st.write(f"**Market Cap:** ₹{selected_coin['market_cap']}")
        st.write(f"**24H High:** ₹{selected_coin['high_24h']}")
        st.write(f"**24H Low:** ₹{selected_coin['low_24h']}")
        st.write(f"**All-time High:** ₹{selected_coin['ath']}")
        st.write(f"**All-time Low:** ₹{selected_coin['atl']}")

        # Function to plot price trend
        
        def plot_price_trend(crypto_id):
            historical_data = manager.get_historical_data(crypto_id)

            if historical_data:
                prices = historical_data["prices"]
                dates = [datetime.datetime.fromtimestamp(price[0] / 1000).date() for price in prices]
                values = [price[1] for price in prices]

                plt.figure(figsize=(10, 5))
                plt.plot(dates, values, marker='o', linestyle='-', color='b', label="Price Trend")
                plt.xlabel("Date")
                plt.ylabel("Price (INR)")
                plt.title(f"{selected_coin['name']} Price Trend (Last 7 Days)")
                plt.xticks(rotation=45)
                plt.legend()
                plt.grid()
                st.pyplot(plt)
            else:
                st.warning("No historical data available.")

        plot_price_trend(selected_coin["id"])

        # User enters investment amount
        
        amount_invested = st.number_input("Enter Rupees to Invest:", min_value=0.01, step=0.01, format="%.2f", key="investment_amount")
        
        if amount_invested > balance:
            st.warning("❌ Insufficient balance! Please add more funds.")
            if st.button("Add Balance"):
                switch_page("add_balance")
            return

        # Calculate how much crypto the user will receive
        
        crypto_quantity = round(amount_invested / selected_coin["current_price"], 8)
        st.write(f"**You will own {selected_coin['name']}:** {crypto_quantity} units")
        st.write(f"💰 **Your Current Balance:** ₹{balance}")

        if st.button("Confirm Purchase ✅"):
            try:
                # Convert values to Decimal for precise calculations
                
                amount_decimal = decimal.Decimal(str(amount_invested))
                crypto_quantity_decimal = decimal.Decimal(str(crypto_quantity))
                price_decimal = decimal.Decimal(str(round(selected_coin["current_price"], 8)))

                # Update user balance
                
                cursor.execute("UPDATE user SET balance = balance - %s WHERE username = %s", (amount_decimal, username))
                
                # Insert into buycrypto table
                
                cursor.execute("""
                    INSERT INTO buycrypto (username, cryptoname, quantity, buyingprice, amountpaid, buy_date)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (username, selected_crypto, crypto_quantity_decimal, price_decimal, amount_decimal))
                
                conn.commit()
                
                st.success(f"✅ Successfully purchased {crypto_quantity} {selected_crypto} for ₹{amount_invested}!")
                st.rerun()

            except Exception as e:
                st.warning(f"⚠️ Network Error! Try again later.\nError: {e}")

        if st.button("Cancel Purchase ❌"):
            switch_page("Dashboard")

    if st.button("Back"):
        switch_page("Dashboard")



        
def add_balance():
    st.title("Add Balance")
    
    # Ensure user is logged in 
    
    username = st.session_state.username
    user = User(username, "") 
    balance = user.checkBalance()
    
    
    st.write(f"Current Balance: ₹{balance}")
    st.write("Enter amount to add to your balance.")
    
    amount = st.number_input("Add amount to balance (INR):", min_value=0.0, step=100.0)
    
    if st.button("Add Balance"):
        if amount > 0:
            cursor.execute("UPDATE user SET balance = balance + %s WHERE username = %s", (amount, username))
            conn.commit()
            st.success(f"Added ₹{amount} to your balance!")
            switch_page("buy_crypto")
        else:
            st.warning("Please enter a valid amount!")
    
    if st.button("Back"):
        switch_page("buy_crypto")




def sell_crypto():
    st.title("Sell Crypto")

    # Ensure user is logged in
    
    if "username" not in st.session_state:
        st.error("Please login first!")
        if st.button("Go to Login"):
            st.session_state["page"] = "Login"
            st.rerun()
        return

    username = st.session_state.username
    user = User(username, "")

    # Fetch user balance
    
    balance = user.checkBalance()
    st.write(f"💰 **Your Current Balance:** ₹{balance}")

    manager = CryptoManager()
    data = manager.get_crypto_data()

    # Fetch user's owned crypto
    
    cursor.execute("SELECT id, cryptoname, quantity, buyingprice FROM buycrypto WHERE username = %s", (username,))
    owned_crypto = cursor.fetchall()

    if not owned_crypto:
        st.warning("⚠️ You don't own any cryptocurrency.")
        if st.button("Back"):
            switch_page("Dashboard")
        return

    # Select cryptocurrency to sell
    
    crypto_names = list(set([row[1] for row in owned_crypto])) 
    selected_crypto = st.selectbox("Select Cryptocurrency to Sell:", crypto_names)

    # get current price of the selected crypto
    
    for coin in data:
        if coin["name"] == selected_crypto:
            current_price = decimal.Decimal(str(coin["current_price"]))
            break
    else:
        st.warning("⚠️ Cryptocurrency data unavailable.")
        return

    # Select buy lot to sell from
    
    selected_crypto_lots = [row for row in owned_crypto if row[1] == selected_crypto]

    lot_options = [f"Lot ID: {row[0]} | {row[2]} {selected_crypto} @ ₹{row[3]}" for row in selected_crypto_lots]
    selected_lot = st.selectbox("Select Buy Lot to Sell From:", lot_options)

    # Extract selected lot details
    
    selected_lot_id = int(selected_lot.split("|")[0].split(":")[1].strip())
    selected_lot_quantity = decimal.Decimal(str([row[2] for row in selected_crypto_lots if row[0] == selected_lot_id][0]))
    selected_lot_price = decimal.Decimal(str([row[3] for row in selected_crypto_lots if row[0] == selected_lot_id][0]))

    st.write(f"📈 **Current Price:** ₹{current_price}")
    st.write(f"📊 **You Own in Selected Lot:** {selected_lot_quantity} {selected_crypto} at ₹{selected_lot_price}")

    quantity_to_sell = st.number_input("Enter quantity to sell:", min_value=0.0001, max_value=float(selected_lot_quantity), step=0.0001, format="%.4f")

    # Convert quantity to Decimal
    
    quantity_to_sell = decimal.Decimal(str(quantity_to_sell))

    # Calculate profit/loss
    
    total_sell_amount = quantity_to_sell * current_price
    profit_loss = (current_price - selected_lot_price) * quantity_to_sell

    st.write(f"💰 **Total Sell Amount:** ₹{total_sell_amount}")
    st.write(f"📈 **Profit/Loss:** ₹{profit_loss}")

    if st.button("Sell"):
        try:
            cursor.execute("UPDATE user SET balance = balance + %s WHERE username = %s", (total_sell_amount, username))

            # Update or remove buy lot in the database
            
            if quantity_to_sell == selected_lot_quantity:
                cursor.execute("DELETE FROM buycrypto WHERE id = %s", (selected_lot_id,))
            else:
                cursor.execute("UPDATE buycrypto SET quantity = quantity - %s WHERE id = %s", (quantity_to_sell, selected_lot_id))

            # Insert into sellcrypto history
            
            cursor.execute("""
                INSERT INTO sellcrypto (username, cryptoname, sellingprice, buyingprice, quantity, total_sell_amount, gain_loss, sell_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, (username, selected_crypto, current_price, selected_lot_price, quantity_to_sell, total_sell_amount, profit_loss))

            conn.commit()

            # Fetch updated balance
            
            updated_balance = user.checkBalance()

            st.success(f"✅ Successfully sold {quantity_to_sell} {selected_crypto} for ₹{total_sell_amount}!")
            st.write(f"📈 **Profit/Loss:** ₹{profit_loss}")
            st.write(f"💰 **Updated Balance:** ₹{updated_balance}")

            # Reset fields and refresh page
            
            st.session_state["quantity_to_sell"] = 0.0001
            st.rerun()

        except Exception as e:
            st.warning(f"⚠️ Error: {e}")

    if st.button("Back"):
        switch_page("Dashboard")



def view_sells_history():
    st.title("📜 Sell History")

    # Ensure user is logged in
    
    if "username" not in st.session_state:
        st.error("Please login first!")
        if st.button("Go to Login"):
            st.session_state["page"] = "Login"
            st.rerun()
        return

    username = st.session_state.username

    # Fetch sell history from database
    
    cursor.execute("""
        SELECT cryptoname, quantity, sellingprice, buyingprice, total_sell_amount, gain_loss, sell_date 
        FROM sellcrypto 
        WHERE username = %s 
        ORDER BY sell_date DESC
    """, (username,))
    sell_data = cursor.fetchall()

    # If no sell exist, show message
    
    if not sell_data:
        st.warning("📭 No sell history available.")
        if st.button("Back"):
            switch_page("Dashboard")
        return

    # Convert sell history to Pandas DataFrame
    
    df = pd.DataFrame(sell_data, columns=[
        "Cryptocurrency", "Quantity Sold", "Selling Price (INR)", "Buying Price (INR)", 
        "Total Sell Amount (INR)", "Profit/Loss (INR)", "Sell Date"
    ])

    # Convert INR columns to float

    df["Profit/Loss (INR)"] = df["Profit/Loss (INR)"].astype(float)



    df["Selling Price (INR)"] = df["Selling Price (INR)"].apply(lambda x: f"₹{x:,.2f}")
    df["Buying Price (INR)"] = df["Buying Price (INR)"].apply(lambda x: f"₹{x:,.2f}")
    df["Total Sell Amount (INR)"] = df["Total Sell Amount (INR)"].apply(lambda x: f"₹{x:,.2f}")


    
    def highlight_profit_loss(val):
        return "color: green" if val >= 0 else "color: red"

    st.dataframe(df.style.applymap(highlight_profit_loss, subset=["Profit/Loss (INR)"]))

    if st.button("Back to Dashboard"):
        switch_page("Dashboard")



# Function to fetch owned cryptocurrencies

def get_owned_cryptos(username):
    cursor.execute("""
        SELECT cryptoname, SUM(quantity), SUM(quantity * buyingprice) 
        FROM buycrypto WHERE username = %s GROUP BY cryptoname
    """, (username,))
    return cursor.fetchall()

# Function to fetch transaction history

def get_transaction_history(username):
    cursor.execute("""
        SELECT cryptoname, quantity, buyingprice, 'BUY' AS type, buy_date FROM buycrypto WHERE username = %s
        UNION
        SELECT cryptoname, quantity, sellingprice, 'SELL' AS type, sell_date FROM sellcrypto WHERE username = %s
        ORDER BY buy_date DESC
    """, (username, username))
    return cursor.fetchall()




# Portfolio Page


def view_portfolio():
    st.title("📊 Your Portfolio")

    # Ensure user is logged in
    
    if "username" not in st.session_state:
        st.error("Please login first!")
        if st.button("Go to Login"):
            st.session_state.page = "Login"
            st.rerun()
        return
    
    username = st.session_state.username
    manager = CryptoManager()
    
    # Fetch owned cryptocurrencies
    
    owned_cryptos = get_owned_cryptos(username)
    if not owned_cryptos:
        st.warning("You don't own any cryptocurrencies yet.")
        if st.button("Back"):
            switch_page("Dashboard")
        return
    
    # Get live prices
    
    live_data = manager.get_crypto_data()
    price_map = {coin["name"]: decimal.Decimal(str(coin["current_price"])) for coin in live_data}
    
    total_investment = 0
    total_value = 0
    portfolio_data = []
    
    # data for the table and portfolio value
    
    for crypto, quantity, invested in owned_cryptos:
        current_price = price_map.get(crypto, decimal.Decimal("0"))
        current_value = quantity * current_price
        profit_loss = current_value - invested
        profit_loss_pct = (profit_loss / invested * 100) if invested > 0 else 0
        
        total_investment += invested
        total_value += current_value
        
        portfolio_data.append([crypto, quantity, invested, current_value, profit_loss, profit_loss_pct])
    
    # Display Total Portfolio Value
    
    st.metric("💰 Total Portfolio Value", f"₹{total_value:,.2f}")
    st.metric("📈 Total Investment", f"₹{total_investment:,.2f}")
    st.metric("📊 Overall Profit/Loss", f"₹{(total_value - total_investment):,.2f}")
    
    
    # Display Portfolio Table
    
    df = pd.DataFrame(portfolio_data, columns=["Cryptocurrency", "Quantity", "Investment (₹)", "Current Value (₹)", "Profit/Loss (₹)", "Profit/Loss (%)"])
    st.dataframe(df.style.applymap(lambda x: "color: green" if x > 0 else "color: red", subset=["Profit/Loss (₹)", "Profit/Loss (%)"]))
    
    
    # transaction history
    
    st.subheader("📜 Transaction History")
    transactions = get_transaction_history(username)
    history_df = pd.DataFrame(transactions, columns=["Cryptocurrency", "Quantity", "Price (₹)", "Type", "Date"])
    st.dataframe(history_df)
    

    if st.button("Back to Dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()
    elif st.button("withdraw"):
        st.session_state.page = "withdraw_funds"
        st.rerun()
        
        
        
# Withdraw Funds
     
def withdraw_funds():
    st.title("Withdraw Funds 💸")

    if "username" not in st.session_state:
        st.error("Please login first!")
        if st.button("Go to Login"):
            st.session_state["page"] = "Login"
            st.rerun()
        return

    username = st.session_state.username
    user = User(username, "")

    # Fetch current balance
    
    balance = user.checkBalance()
    st.write(f"💰 **Current Balance:** ₹{balance}")

    # User inputs withdrawal details
    
    upi_id = st.text_input("Enter UPI ID")
    amount = st.number_input("Enter amount to withdraw (INR):", min_value=100.0, step=50.0)

    if st.button("Withdraw"):
        if not upi_id:
            st.warning("Please enter a valid UPI ID!")
        elif amount <= 0:
            st.warning("Enter a valid withdrawal amount!")
        else:
            success, message = user.withdraw(upi_id, amount)
            if success:
                st.success(message)
            else:
                st.warning(message)

    if st.button("Back to Portfolio"):
        st.session_state.page = "view_portfolio"
        st.rerun()



# **Navigation Handling**

if st.session_state.page == "Login":
    login_page()
elif st.session_state.page == "Signup":
    signup_page()
elif st.session_state.page == "Dashboard":
    dashboard()
elif st.session_state.page == "view_crypto":
    view_crypto()
elif st.session_state.page == "buy_crypto":
    buy_crypto()
elif st.session_state.page == "sell_crypto":
    sell_crypto()
elif st.session_state.page == "view_portfolio":    
    view_portfolio()
elif st.session_state.page == "add_balance":
    add_balance()
elif st.session_state.page == "sell_history":
    view_sells_history()
elif st.session_state.page == "withdraw_funds":
    withdraw_funds()