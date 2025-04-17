
import streamlit as st
import requests

st.set_page_config(page_title="Breakfast Check-In", page_icon="🥐", layout="wide")

FIREBASE_URL = "https://breakfast-50e37-default-rtdb.europe-west1.firebasedatabase.app"

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
        .room-box.manual {color: blue;}
    </style>
""", unsafe_allow_html=True)

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

@st.cache_data(ttl=5)
def get_expected_rooms():
    try:
        response = requests.get(f"{FIREBASE_URL}/rooms.json")
        if response.status_code == 200 and response.json():
            return set(response.json())
        return set()
    except:
        return set()

@st.cache_data(ttl=3)
def get_checked_in_rooms():
    try:
        response = requests.get(f"{FIREBASE_URL}/checkins.json")
        if response.status_code == 200 and response.json():
            return set(response.json())
        return set()
    except:
        return set()

@st.cache_data(ttl=3)
def get_manual_rooms():
    try:
        response = requests.get(f"{FIREBASE_URL}/manual_rooms.json")
        if response.status_code == 200 and response.json():
            return set(response.json())
        return set()
    except:
        return set()

if admin_mode:
    uploaded_file = st.file_uploader("Upload expected_rooms.txt", type="txt")
    if uploaded_file:
        try:
            room_list = sorted({
                line.strip() for line in uploaded_file.getvalue().decode("utf-8").splitlines()
                if line.strip().isdigit() and 100 <= int(line.strip()) <= 639
            }, key=int)
            requests.put(f"{FIREBASE_URL}/rooms.json", json=room_list)
            st.success(f"{len(room_list)} rooms uploaded.")
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Upload error: {e}")

    st.markdown("---")
    if st.button("❌ Full Reset (Rooms + Check-ins)"):
        requests.delete(f"{FIREBASE_URL}/rooms.json")
        requests.delete(f"{FIREBASE_URL}/checkins.json")
        requests.delete(f"{FIREBASE_URL}/manual_rooms.json")
        st.success("✅ All data reset.")
        st.cache_data.clear()
        st.rerun()

expected_rooms = get_expected_rooms()
checked_in = get_checked_in_rooms()
manual_rooms = get_manual_rooms()

# ✅ Guest Check-In
if expected_rooms or manual_rooms:
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
        all_valid_rooms = expected_rooms.union(manual_rooms)
        if room in checked_in:
            st.info(f"Room {room} is already checked in.")
        elif room in all_valid_rooms:
            updated_list = list(checked_in) + [room]
            requests.put(f"{FIREBASE_URL}/checkins.json", json=sorted(updated_list))
            st.success(f"✅ Room {room} checked in.")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("Room not on today's list. Please speak to staff.")
else:
    st.warning("Room list not available yet.")

# 🔧 Admin Manual Room Add
if admin_mode:
    st.markdown("---")
    st.subheader("🔧 Add Extra Room (Manual Entry)")
    manual_input = st.number_input("Add room not in original list", min_value=100, max_value=639, step=1, key="manual_room_add")
    if st.button("➕ Add Room Manually"):
        if str(manual_input) not in manual_rooms:
            updated_manual = list(manual_rooms) + [str(manual_input)]
            requests.put(f"{FIREBASE_URL}/manual_rooms.json", json=sorted(updated_manual))
            st.success(f"Room {int(manual_input)} added manually.")
            st.cache_data.clear()
            st.rerun()
        else:
            st.info("Room already added manually.")

# 🧾 Admin Overview
if admin_mode and (expected_rooms or manual_rooms):
    st.divider()
    st.subheader("📊 Live Breakfast Overview")

    all_rooms = expected_rooms.union(manual_rooms)
    remaining = all_rooms - checked_in

    st.markdown(f"""
    ✅ **Checked-in:** {len(checked_in)} / {len(all_rooms)}  
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
            if room_str in all_rooms:
                if room_str in checked_in:
                    col.markdown(f"<div class='room-box checked'>✅ {room_str}</div>", unsafe_allow_html=True)
                elif room_str in manual_rooms:
                    col.markdown(f"<div class='room-box manual'>🔧 {room_str}</div>", unsafe_allow_html=True)
                else:
                    col.markdown(f"<div class='room-box pending'>🔲 {room_str}</div>", unsafe_allow_html=True)
