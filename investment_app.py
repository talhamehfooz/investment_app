import streamlit as st
import firebase_admin
from firebase_admin import auth, credentials, firestore
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Firebase Setup
cred = credentials.Certificate("firebase_credentials.json")  # Your Firebase service account key
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
google_creds = Credentials.from_service_account_file("google_credentials.json", scopes=scope)
gc = gspread.authorize(google_creds)

# Open Google Sheet
SHEET_ID = "your_google_sheet_id"
worksheet = gc.open_by_key(SHEET_ID).sheet1

# Streamlit UI
st.title("Investor Dashboard")

# Login System
st.sidebar.title("Login")
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    try:
        user = auth.get_user_by_email(email)
        st.sidebar.success(f"Welcome, {user.email}!")
        st.session_state["user"] = user.email
    except:
        st.sidebar.error("Invalid login credentials.")

# Dashboard (For Logged-in Users)
if "user" in st.session_state:
    st.subheader(f"Welcome, {st.session_state['user']}!")

    # Fetch investment data from Google Sheets
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    # Display investments related to the logged-in user
    user_investments = df[df["Investor Email"] == st.session_state["user"]]

    if not user_investments.empty:
        st.write("### Your Investments")
        st.dataframe(user_investments)
    else:
        st.warning("No investments found for your account.")

# Admin Panel (To Add Investments)
st.sidebar.title("Admin Panel")
if st.sidebar.button("Add Investment"):
    st.session_state["admin"] = True

if "admin" in st.session_state:
    st.subheader("Add Investment")
    investor_email = st.text_input("Investor Email")
    venture_name = st.text_input("Venture Name")
    amount = st.number_input("Investment Amount", min_value=0)
    profit_rate = st.number_input("Profit Rate (%)", min_value=0.0, format="%.2f")
    maturity_date = st.date_input("Maturity Date")
    investment_model = st.selectbox("Investment Model", ["Venture-Based", "Sleeping Investment"])
    
    if st.button("Save Investment"):
        new_data = [investor_email, venture_name, amount, profit_rate, str(maturity_date), investment_model]
        worksheet.append_row(new_data)
        st.success("Investment added successfully!")


