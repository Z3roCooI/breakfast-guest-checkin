import streamlit as st
import requests
import time

st.set_page_config(page_title="Breakfast Check-In", page_icon="🥐", layout="wide")

# Firebase Realtime DB URL
FIREBASE_URL = "https://breakfast-50e37-default-rtdb.europe-west1.firebasedatabase.app"

# Title & styles
st.markdown("""
    <h1 style='text-align: center;'>🍳 Breakfast Check-In</h1>
    <style>
        #MainMenu, footer {visibility: hidden;}
        .stTextInput > div > div > input,
        .stNumberInput input {
            font-size: 28px;
            height: 50px;
        }
        .stButton button {font-size: 24px; padding: 12px;}
        .room-box {font-size: 16px; padding: 4px;}
        .room-box.checked {color: green;}
        .room-box.pending {color: gray;}
    </style>
""", unsafe_allow_html=True)

# Admin access
ADMIN_PIN = "1234"
query_params = st.query_params
admin_requested = query_params.get("admin", ["0"])[0] == "1"
admin_mode = False

if admin_requested:
    with st.expander("🔐 Admin Access"):
        entered_pin = st.text_input("Enter admin PIN:", type="password", label_visibility="collapsed", placeholder="Enter Admin PIN")
        if entered_pin == ADMIN_PIN:
            st.success("Admin access granted.")
            admin_mode = True
        elif entered_pin:
            st.error("Incorrect PIN")

# Load from Firebase
@st.cache_data(ttl=5)
def get_expected_rooms():
    try:
        response = requests.get(f"{FIREBASE_URL}/rooms.json")
        if response.status_code == 200 and response.json():
            return set(response.json())
        return set()
    except Exception as e:
        st.error(f"Failed to load room list: {e}")
        return set()

@st.cache_data(ttl=3)
def get_checked_in_rooms():
    try:
        response = requests.get(f"{FIREBASE_URL}/checkins.json")
        if response.status_code == 200 and response.json():
            return set(response.json())
        return set()
    except Exception as e:
        st.error(f"Failed to load check-ins: {e}")
        return set()

# Admin: Upload room list
if admin_mode:
    uploaded_file = st.file_uploader("Upload expected_rooms.txt", type="txt")
    if uploaded_file:
        try:
            room_list = sorted({
                line.strip() for line in uploaded_file.getvalue().decode("utf-8").splitlines()
                if line.strip().isdigit() and 100 <= int(line.strip()) <= 639
            }, key=int)
            response = requests.put(f"{FIREBASE_URL}/rooms.json", json=room_list)
            if response.status_code == 200:
                st.success(f"{len(room_list)} rooms uploaded to Firebase.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Failed to upload to Firebase.")
        except Exception as e:
            st.error(f"Upload error: {e}")

    # ❌ Full Reset
    st.markdown("---")
    if st.button("❌ Full Reset (Rooms + Check-ins)"):
        try:
            r1 = requests.delete(f"{FIREBASE_URL}/rooms.json")
            r2 = requests.delete(f"{FIREBASE_URL}/checkins.json")
            if r1.status_code == 200 and r2.status_code == 200:
                st.success("✅ All data reset successfully.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("❌ Failed to reset data.")
        except Exception as e:
            st.error(f"Reset error: {e}")

# Load room/check-in data
expected_rooms = get_expected_rooms()
checked_in = get_checked_in_rooms()

# ✅ Guest Check-In
if expected_rooms:
    st.subheader("🎫 Guest Check-In")
    room_input = st.number_input(
        label="Enter your room number:",
        min_value=100,
        max_value=639,
        step=1,
        format="%d",
        label_visibility="collapsed",
        placeholder="Enter room number"
    )

    if st.button("✅ Check In"):
        room = str(int(room_input))
        if room in checked_in:
            st.info(f"Room {room} is already checked in. Enjoy your breakfast! 🥐")
        elif room in expected_rooms:
            updated_list = list(checked_in) + [room]
            response = requests.put(f"{FIREBASE_URL}/checkins.json", json=sorted(updated_list))
            if response.status_code == 200:
                st.success(f"✅ Room {room} checked in. Bon appétit!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("❌ Failed to update check-in list.")
        else:
            st.error("Room not found on today’s list. Please speak to staff.")
else:
    st.warning("Room list not uploaded yet. Please contact staff.")

# 🔁 Refresh controls for admin
if admin_mode:
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        auto_refresh = st.checkbox("⏱ Auto-refresh every 10 seconds")
        if auto_refresh:
            time.sleep(10)
            st.cache_data.clear()
            st.rerun()

# 📊 Admin Overview
if admin_mode and expected_rooms:
    st.divider()
    st.subheader("📊 Live Breakfast Overview")

    remaining = expected_rooms - checked_in
    st.markdown(f"""
    ✅ **Checked-in:** {len(checked_in)} / {len(expected_rooms)}  
    🔲 **Remaining:** {len(remaining)}  
    """)

    floor_ranges = {
        "100–199": range(100, 200),
        "200–299": range(200, 300),
        "300–399": range(300, 400),
        "400–499": range(400, 500),
        "500–599": range(500, 600),
        "600–639": range(600, 640),
    }

    columns = st.columns(6)
    for col, (label, room_range) in zip(columns, floor_ranges.items()):
        col.markdown(f"**🧭 {label}**")
        for room in room_range:
            room_str = str(room)
            if room_str in expected_rooms:
                if room_str in checked_in:
                    col.markdown(f"<div class='room-box checked'>✅ {room_str}</div>", unsafe_allow_html=True)
                else:
                    col.markdown(f"<div class='room-box pending'>🔲 {room_str}</div>", unsafe_allow_html=True)
