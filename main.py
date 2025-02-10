import streamlit as st
from db import conn,cursor


class User:
    
    def __init__(self,username,pwd,email,phone):
        self.un = username
        self.pwd = pwd
        self.email = email
        self.phone = phone

    def userExists(self):
        cursor.execute("Select * from user where username = %s" , (self.un,))
        return cursor.fetchone() is not None
    
    def register(self):
        """Register a new user"""
        if self.userExists():
            return False  # User already exists
        cursor.execute("INSERT INTO user (username, pwd, email, phnnum) VALUES (%s, %s ,%s ,%s)", (self.un, self.pwd, self.email, self.phone))
        conn.commit()
        return True  # Registration successful

    def login(self):
        """Authenticate user"""
        cursor.execute("SELECT * FROM user WHERE username = %s AND pwd = %s", (self.un, self.pwd))
        return cursor.fetchone() is not None
    

if "page" not in st.session_state:
    if conn.is_connected():
        print("Caonnected")
    else:
        print("not connected")    
    st.session_state.page = "Login"

def switch_page(page):
    st.session_state.page = page
    


# ---------------------- Signup Page ----------------------
def signup_page():
    st.title("Signup Page")

    new_username = st.text_input("Enter a Username")
    new_email = st.text_input("Enter email" , type="email")
    new_phone = st.text_input("Enter phone number" , type="number")
    new_password = st.text_input("Enter a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Signup"):
        if new_password != confirm_password:
            st.warning("Passwords do not match!")
        else:
            user = User(new_username, new_password , new_email, new_phone)
            if user.register():
                st.success("Signup Successful! Please login.")
                switch_page("Login")
            else:
                st.warning("Username already exists! Try a different one.")

    st.button("Already have an account? Login", on_click=lambda: switch_page("Login"))


# ---------------------- Login Page ----------------------
def login_page():
    st.title("Login Page")

    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        user = User(username, password)
        if user.userExists():
            if user.login():
                st.success(f"Welcome {username}!")
                st.session_state.page = "Dashboard"  # ✅ Set session state
                st.rerun()  # ✅ Force refresh
            else:
                st.error("Incorrect Password! Try again.")
        else:
            st.warning("User does not exist! Please sign up first.")
            st.session_state.page = "Signup"
            st.rerun()  # ✅ Redirect to signup

    st.button("Don't have an account? Signup", on_click=lambda: switch_page("Signup"))


# ---------------------- Dashboard ----------------------
def dashboard():
    st.title("Welcome to Crypto Tracker")
    st.write("This is the dashboard after successful login!")

    if st.button("Logout"):
        switch_page("Login")


# ---------------------- Page Navigation ----------------------
if st.session_state.page == "Login":
    login_page()
elif st.session_state.page == "Signup":
    signup_page()
elif st.session_state.page == "Dashboard":
    dashboard()
    
