import streamlit as st
from streamlit_extras.st_autorefresh import st_autorefresh

# Auto-refresh every 5 seconds on admin view
st.set_page_config(page_title="Breakfast Check-In", page_icon="🥐", layout="centered")

# Style for UI
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

# Admin PIN
ADMIN_PIN = "1234"
query_params = st.query_params
admin_requested = query_params.get("admin", ["0"])[0] == "1"
admin_mode = False

# Rerun admin view every 5s
if admin_requested:
    st_autorefresh(interval=5000, limit=None, key="admin_autorefresh")

    with st.expander("🔐 Admin Access"):
        entered_pin = st.text_input("Enter admin PIN:", type="password")
        if entered_pin == ADMIN_PIN:
            st.success("Admin access granted.")
            admin_mode = True
        elif entered_pin:
            st.error("Incorrect PIN")

# Persistent room list
@st.cache_resource
def get_expected_rooms():
    return set()

expected_rooms = get_expected_rooms()

# Admin: Upload room list
if admin_mode:
    uploaded_file = st.file_uploader("Upload expected_rooms.txt", type="txt")
    if uploaded_file:
        room_list = set(
            line.strip() for line in uploaded_file.getvalue().decode("utf-8").splitlines()
            if line.strip().isdigit() and 100 <= int(line.strip()) <= 639
        )
        expected_rooms.clear()
        expected_rooms.update(room_list)
        st.success(f"{len(expected_rooms)} rooms loaded.")

# Guest check-ins
if "checked_in" not in st.session_state:
    st.session_state.checked_in = set()

# Guest check-in UI
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
    st.warning("Room list not uploaded yet. Please contact staff.")

# 🧾 Admin Panel
if admin_mode and expected_rooms:
    st.divider()
    st.subheader("📊 Live Breakfast Overview")

    checked = st.session_state.checked_in
    remaining = expected_rooms - checked

    st.markdown(f"""
    ✅ **Checked-in:** {len(checked)} / {len(expected_rooms)}  
    🔲 **Remaining:** {len(remaining)}  
    """)

    # Group by floor
    st.markdown("### 📋 Room Status by Floor")
    floors = {
        "100–199": [r for r in expected_rooms if 100 <= int(r) <= 199],
        "200–299": [r for r in expected_rooms if 200 <= int(r) <= 299],
        "300–399": [r for r in expected_rooms if 300 <= int(r) <= 399],
        "400–499": [r for r in expected_rooms if 400 <= int(r) <= 499],
        "500–599": [r for r in expected_rooms if 500 <= int(r) <= 599],
        "600–639": [r for r in expected_rooms if 600 <= int(r) <= 639],
    }

    for label, rooms in floors.items():
        st.markdown(f"**🧭 {label}**")
        for room in sorted(rooms, key=int):
            if room in checked:
                st.markdown(f"<div class='room-box checked'>✅ Room {room}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='room-box pending'>🔲 Room {room}</div>", unsafe_allow_html=True)
