import streamlit as st
import requests

st.set_page_config(page_title="Breakfast Check-In", page_icon="🥐", layout="wide")

# Firebase Config
FIREBASE_URL = "https://breakfast-50e37-default-rtdb.europe-west1.firebasedatabase.app"

# Title & styles
st.markdown("""
    <h1 style='text-align: center;'>🍳 Breakfast Check-In</h1>
    <style>
        #MainMenu, footer {visibility: hidden;}
        .stTextInput > div > div > input {font-size: 28px; height: 50px;}
        .stButton button {font-size: 24px; padding: 12px;}
        .room-box {font-size: 16px; padding: 4px;}
        .room-box.checked {color: green;}
        .room-box.pending {color: gray;}
    </style>
""", unsafe_allow_html=True)

# Admin toggle via ?admin=1
ADMIN_PIN = "1234"
query_params = st.query_params
admin_requested = query_params.get("admin", ["0"])[0] == "1"
admin_mode = False

if admin_requested:
    with st.expander("🔐 Admin Access"):
        entered_pin = st.text_input("Enter admin PIN:", type="password")
        if entered_pin == ADMIN_PIN:
            st.success("Admin access granted.")
            admin_mode = True
        elif entered_pin:
            st.error("Incorrect PIN")

# Load expected rooms from Firebase
@st.cache_data(ttl=5)
def get_expected_rooms():
  try:
    response = requests.put(f"{FIREBASE_URL}/rooms.json", json=room_list)
    if response.status_code == 200:
        st.success(f"{len(room_list)} rooms uploaded to Firebase.")
    else:
        st.error("Failed to upload to Firebase.")
except Exception as e:
    st.error(f"Upload error: {e}")
