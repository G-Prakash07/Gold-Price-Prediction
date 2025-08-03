import streamlit as st
import joblib
import numpy as np
import os
import json
import hashlib
from PIL import Image
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Gold Price Prediction App", layout="wide")

# Load model
model = joblib.load('rfr_model.pkl')

# Constants
USER_FILE = "users.json"
if not os.path.exists(USER_FILE):
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)

# Helper Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    with open(USER_FILE, 'r') as f:
        users = json.load(f)
    return username in users and users[username]['password'] == hash_password(password)

def save_user(username, email, password):
    with open(USER_FILE, 'r') as f:
        users = json.load(f)
    users[username] = {
        "email": email,
        "password": hash_password(password)
    }
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# Session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# Sidebar Menu
with st.sidebar:
    selected = option_menu("Menu", ["Home", "Login", "SignUp", "Dashboard"], 
                           icons=["house", "box-arrow-in-right", "person-plus", "bar-chart"], 
                           menu_icon="cast", default_index=0)

    if st.session_state.logged_in:
        st.write(f"👤 Logged in as: `{st.session_state.username}`")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("✅ Logged out successfully.")

# Home Tab
if selected == "Home":
    st.title("🏆 Welcome to Gold Price Prediction App")
    st.markdown("""
        Predict the **price of gold** using market index values.  
        Our model uses financial indicators such as **SPX**, **USO**, **SLV**, and **EUR/USD** rates  
        to accurately forecast gold prices in both **USD** and **EUR**.
        
        👉 Login to use the prediction tool.
    """)
    st.image("gold.jpg", width=400)
    
    if st.session_state.logged_in:
        st.success(f"Welcome, {st.session_state.username}! You are logged in.")
        st.subheader("🔮 Make a Prediction")
        
        spx = st.number_input("Enter SPX Value")
        uso = st.number_input("Enter USO Value")
        slv = st.number_input("Enter SLV Value")
        eur_per_usd = st.number_input("Enter EUR/USD Value")

        if st.button("Predict"):
            features = np.array([[spx, uso, slv, eur_per_usd]])
            prediction = model.predict(features)
            usd_price = prediction[0]
            eur_price = usd_price * eur_per_usd

            st.success("✅ Prediction Successful!")
            
            # Display as metrics
            st.markdown("### 💰 Predicted Gold Prices:")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="**Gold Price (USD)**", value=f"${usd_price:,.2f}", delta=None)
            with col2:
                st.metric(label="**Gold Price (EUR)**", value=f"€{eur_price:,.2f}", delta=None)

            # Optional: add styled markdown below the metrics
            st.markdown("""
            <div style="background-color:#f1f3f6;padding:15px;border-radius:10px;">
                <h4 style='color:#004d99;'>📊 Financial Insight</h4>
                <p><strong>USD:</strong> The predicted gold price is <span style='color:green;'>${:,.2f}</span></p>
                <p><strong>EUR:</strong> The equivalent gold price is <span style='color:green;'>€{:,.2f}</span></p>
            </div>
            """.format(usd_price, eur_price), unsafe_allow_html=True)

    else:
        st.info("ℹ️ Please login to access the prediction form.")

# Login Tab
elif selected == "Login":
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Logged in successfully!")
        else:
            st.error("❌ Invalid credentials")

# SignUp Tab
elif selected == "SignUp":
    st.title("📝 Sign Up")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if not username or not email or not password or not confirm_password:
            st.warning("⚠️ All fields are required.")
        elif password != confirm_password:
            st.error("❌ Passwords do not match.")
        else:
            with open(USER_FILE, 'r') as f:
                users = json.load(f)
            if username in users:
                st.error("❌ Username already exists.")
            else:
                save_user(username, email, password)
                st.success("✅ Account created successfully! You can now login.")

# Dashboard Tab
elif selected == "Dashboard":
    st.title("📊 Dashboard - Gold Price Visualizations")

    plot_folder = "plots"
    image_files = [file for file in os.listdir(plot_folder) if file.endswith((".png", ".jpg", ".jpeg"))]

    if image_files:
        cols = st.columns(3)
        for index, image_file in enumerate(image_files):
            img = Image.open(os.path.join(plot_folder, image_file))
            with cols[index % 3]:
                st.image(img, caption=image_file, use_container_width=True)
    else:
        st.warning("⚠️ No images found in 'plots' folder.")
