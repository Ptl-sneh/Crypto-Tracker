import streamlit as st
from db import conn, cursor
import requests
import matplotlib.pyplot as plt
import datetime
import pandas as pd


# USER CLASS 
# UserExists
# register
# login

class User:
    def __init__(self, username, pwd, email="", phone=""):
        self.un = username
        self.pwd = pwd
        self.email = email
        self.phone = phone
    
    def userExists(self):
        """Check if user exists in database"""
        cursor.execute("SELECT * FROM user WHERE username = %s", (self.un,))
        return cursor.fetchone() is not None

    def register(self):
        if self.userExists():
            return False  
        cursor.execute("INSERT INTO user (username, pwd, email, phnnum) VALUES (%s, %s, %s, %s)", (self.un, self.pwd, self.email, self.phone))
        conn.commit()
        return True 

    def login(self):
        """Authenticate user"""
        cursor.execute("SELECT * FROM user WHERE username = %s AND pwd = %s", (self.un, self.pwd))
        return cursor.fetchone() is not None 
    
    def checkBalance(self):  # Fixed method to return actual balance
        cursor.execute("SELECT balance FROM user WHERE username = %s", (self.un,))
        result = cursor.fetchone()
        return result[0] if result else 0


# CRYPTO MANAGER
# get_crypto_data
# get_historical_data


class CryptoManager:
        
    def get_crypto_data(self):
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "inr", "order": "market_cap_desc", "per_page": "100", "page": "1", "sparkline": "false"}
        response = requests.get(url,params=params)
        
        if response.status_code == 429:
            st.warning("Out of requests! Please try again later.")
            return []  # Return an empty list to prevent errors

        if response.status_code != 200:
            st.warning(f"API Error: {response.status_code}. Please try again later.")
            return []
        
        data = response.json()
        return data
    
    def get_historical_data(self, crypto_id):
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
        params = {"vs_currency": "inr", "days": "30", "interval": "daily"}
        response = requests.get(url, params=params)
            
        if response.status_code == 200:
            return response.json()
        else:
            return None

if "page" not in st.session_state:
    st.session_state.page = "Login"


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


def dashboard():
    st.title("Welcome to Crypto Tracker")


    st.button("View Crypto", on_click=lambda: switch_page("view_crypto"))
    st.button("Buy Crypto", on_click=lambda: switch_page("buy_crypto"))
    st.button("Sell Crypto", on_click=lambda: switch_page("sell_crypto"))
    st.button("View Portfolio", on_click=lambda: switch_page("view_portfolio"))

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


def buy_crypto():
    st.title("Buy Crypto")

    # Get username from session state
    if "username" not in st.session_state:
        st.error("Please login first!")
        if st.button("Go to Login"):
            st.session_state["page"] = "Login"
            st.rerun()
        return

    username = st.session_state.username
    user = User(username, "")  # Password not needed for balance check
    balance = user.checkBalance()

    if balance == 0:
        st.warning("Your balance is ₹0. Please add funds first!")
        if st.button("Add Balance"):
            switch_page("add_balance")

    st.write(f"Current Balance: ₹{balance}")
    manager = CryptoManager()
    data = manager.get_crypto_data()

    # Get crypto names for selection
    crypto_names = [coin["name"] for coin in data]
    crypto_choice = st.selectbox("Select Cryptocurrency to Buy:", crypto_names)



    for coin in data:
        if coin["name"] == crypto_choice:
            current_price = coin["current_price"]
            st.write(f"Current Price of {crypto_choice}: ₹{current_price}")
            st.write(f"Market Cap of {crypto_choice}: ₹{coin['market_cap']}")
            st.write(f"24H High of {crypto_choice}: ₹{coin['high_24h']}")
            st.write(f"24H Low of {crypto_choice}: ₹{coin['low_24h']}")
            st.write(f"All time high of {crypto_choice}: ₹{coin['ath']}")
            st.write(f"All time low of {crypto_choice}: ₹{coin['atl']}")
        break


    # Get user input for quantity
    quantity = st.number_input("Enter quantity to buy:", min_value=0, step=1)

    # Validate quantity input
    if quantity <= 0:
        st.warning("Please enter a valid quantity greater than zero!")
        return
    
    
    try:
        total_cost = quantity * current_price
        st.write(f"**Total Cost:** ₹{total_cost}")
        
    
        if total_cost > balance:
            st.warning("Insufficient balance! Please add more funds.")
            if st.button("Add Balance", key="add_funds_button"):
                switch_page("add_balance")


        if st.button("Confirm Purchase"):

            # Database transaction
                cursor.execute("UPDATE user SET balance = balance - %s WHERE username = %s", (total_cost, username))
                cursor.execute("INSERT INTO buycrypto (username, quantity, buyingprice, amountpaid, cryptoname) VALUES (%s, %s, %s, %s, %s)", (username, quantity, current_price, total_cost, crypto_choice))
                conn.commit()
                st.success(f"Successfully purchased {quantity} {crypto_choice} for ₹{total_cost}!")
                st.rerun()
    except Exception as e:
        st.warning("Network Error! Try again later.")
        
    
    if st.button("Back"):
        switch_page("Dashboard")


        
def add_balance():
    st.title("Add Balance")
    
    st.warning("Your balance is ₹0. Please add funds first!")
    
    username = st.session_state.username
    user = User(username, "")  # Password not needed for balance check
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
    
    username = st.session_state.username
    user = User(username, "")  # Password not needed for balance check
    
    balance = user.checkBalance()
    
    manager = CryptoManager()
    data = manager.get_crypto_data()
    
    st.write("Select Cryptocurrency to Sell:")
    
    cursor.execute("SELECT cryptoname, quantity, buyingprice FROM buycrypto WHERE username = %s", (username,))
    c_n = cursor.fetchall()
    
    c_name = [c[0] for c in c_n]
    c_quantity = [c[1] for c in c_n]
    c_buyingprice = [c[2] for c in c_n]
    
    crypto_choice = st.selectbox("Select Cryptocurrency to Sell:", c_name)
    
    for coin in data:
        if coin["name"] == crypto_choice:
            current_price = coin["current_price"]
            st.write(f"Current Price of {crypto_choice}: ₹{current_price}")
            
    
    st.write(f"You own {c_quantity[c_name.index(crypto_choice)]} {crypto_choice} at a buying price of ₹{c_buyingprice[c_name.index(crypto_choice)]}.")  
    
    quantity = st.number_input("Enter quantity to sell:", min_value=1, step=1)
    
    if quantity <= 0:
        st.warning("Please enter a valid quantity greater than zero!")
        return
    
    # try:
    total_cost = quantity * current_price
    st.write(f"**Total Cost:** ₹{total_cost}")
    
    if quantity > c_quantity[c_name.index(crypto_choice)]:
        st.warning("You don't own enough of this cryptocurrency to sell.")
        return
    
    
    if st.button("Confirm Sale"):
        # Database transaction
            cursor.execute("UPDATE user SET balance = balance + %s WHERE username = %s", (total_cost, username))
            cursor.execute("UPDATE buycrypto SET quantity = quantity - %s WHERE username = %s", (quantity, username))
            cursor.execute("INSERT INTO sellcrypto (username, cryptoname,sellingprice, buyingprice, quantity, gain/loss) VALUES (%s, %s, %s, %s, %s, %s)", (username, crypto_choice, current_price, c_buyingprice[c_name.index(crypto_choice)], quantity, total_cost - (quantity * c_buyingprice[c_name.index(crypto_choice)])))
            conn.commit()
            st.success(f"Successfully sold {quantity} {crypto_choice} for ₹{total_cost}!")
            st.rerun()
    # except Exception as e:
    #     st.warning("Network Error! Try again later.")
        
    if st.button("Back"):
        switch_page("Dashboard")

def view_portfolio():
    pass

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