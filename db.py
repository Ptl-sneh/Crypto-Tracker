import mysql.connector

conn = mysql.connector.connect(host = "localhost",user="root",password="",database= "crypto_tracker")

cursor = conn.cursor()

if conn.is_connected():
    print("Connected")
else:
    print("not connected")    
