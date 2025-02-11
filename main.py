import streamlit as st
from db import conn, cursor
import requests
import matplotlib.pyplot as plt
import time
import pandas as pd


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


class CryptoManager:
        
    def get_crypto_data(self):
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "inr", "order": "market_cap_desc", "per_page": "100", "page": "1", "sparkline": "false"}
        response = requests.get(url,params=params)
        data = response.json()
        return data

if "page" not in st.session_state:
    st.session_state.page = "Login"


def switch_page(page):
    st.session_state.page = page
    st.rerun()  


# **Signup Page**
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
                st.success("Signup Successful! Please login.")
                switch_page("Login")  
            else:
                st.warning("Username already exists! Try a different one.")

    st.button("Already have an account? Login", on_click=lambda: switch_page("Login"))


#  **Login Page**
def login_page():
    st.title("Login Page")

    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        user = User(username, password)
        if user.login():
            st.success(f"Welcome {username}!")
            st.session_state.page = "Dashboard"  
            st.rerun() 
        else:
            st.warning("Invalid username or password! Try again or Sign up.")

    st.button("Don't have an account? Signup", on_click=lambda: switch_page("Signup"))


#  **Dashboard Page**
def dashboard():
    st.title("Welcome to Crypto Tracker")


    st.button("View Crypto", on_click=lambda: switch_page("view_crypto"))
    st.button("Buy Crypto", on_click=lambda: switch_page("buy_crypto"))
    st.button("Sell Crypto", on_click=lambda: switch_page("sell_crypto"))
    st.button("View Portfolio", on_click=lambda: switch_page("view_portfolio"))

    if st.button("Logout"):
        switch_page("Login")

def view_crypto():
    manager = CryptoManager()
    st.title("Crypto Currencies")
    data = manager.get_crypto_data()
    df = pd.DataFrame(data)
    st.write(df)
    st.button("Return to Dashboard", on_click=lambda: switch_page("Dashboard"))

def buy_crypto():
    pass

def sell_crypto():
    pass

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
