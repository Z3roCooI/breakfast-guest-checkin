import streamlit as st
import requests

st.set_page_config(page_title="Breakfast Check-In", page_icon="🥐", layout="wide")

# Firebase Realtime DB URL
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

# Admin access via ?admin=1
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
        response = requests.get(f"{FIREBASE_URL}/rooms.json")
        if response.status_code == 200 and response.json():
            return set(response.json())
        return set()
    except Exception as e:
        st.error(f"Failed to load room list from Firebase: {e}")
        return set()

# Upload room list (admin only)
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
            else:
                st.error("Failed to upload to Firebase.")
        except Exception as e:
            st.error(f"Upload error: {e}")

# Read latest room list
expected_rooms = get_expected_rooms()

# Local session check-in storage
if "checked_in" not in st.session_state:
    st.session_state.checked_in = set()

# Guest check-in
if expected_rooms:
    st.subheader("🎫 Guest Check-In")
    room_input = st.text_input("Enter your room number:", placeholder="e.g. 215")

    if st.button("✅ Check In"):
        room = room_input.strip()
        if not room.isdigit():
            st.error("Please enter a valid room number.")
        elif int(room) < 100 or int(room) > 639:
            st.error("Room number out of range.")
        elif room in st.session_state.checked_in:
            st.info(f"Room {room} is already checked in. Enjoy your breakfast! 🥐")
        elif room in expected_rooms:
            st.session_state.checked_in.add(room)
            st.success(f"✅ Room {room} checked in. Bon appétit!")
        else:
            st.error("Room not found on today’s list. Please speak to staff.")
else:
    st.warning("Room list not uploaded yet. Please upload it from the admin PC.")

# Admin view: live floor layout
if admin_mode and expected_rooms:
    st.divider()
    st.subheader("📊 Live Breakfast Overview")

    checked = st.session_state.checked_in
    remaining = expected_rooms - checked

    st.markdown(f"""
    ✅ **Checked-in:** {len(checked)} / {len(expected_rooms)}  
    🔲 **Remaining:** {len(remaining)}  
    """)

    # Floor column layout
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
                if room_str in checked:
                    col.markdown(f"<div class='room-box checked'>✅ {room_str}</div>", unsafe_allow_html=True)
                else:
                    col.markdown(f"<div class='room-box pending'>🔲 {room_str}</div>", unsafe_allow_html=True)
