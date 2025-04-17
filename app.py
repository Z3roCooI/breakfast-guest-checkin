import streamlit as st

st.set_page_config(page_title="Breakfast Check-In", page_icon="🥐", layout="centered")
st.markdown("<h1 style='text-align: center;'>🍳 Breakfast Check-In</h1>", unsafe_allow_html=True)

# Style
st.markdown("""
    <style>
        #MainMenu, footer {visibility: hidden;}
        .stTextInput > div > div > input {font-size: 28px; height: 50px;}
        .stButton button {font-size: 24px; padding: 12px;}
        .room-box {font-size: 16px; padding: 4px;}
        .room-box.checked {color: green;}
        .room-box.pending {color: gray;}
    </style>
""", unsafe_allow_html=True)

# Admin PIN and URL toggle
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

# Shared room list using cache_resource
@st.cache_resource
def get_expected_rooms():
    return set()

expected_rooms = get_expected_rooms()

# Upload file (admin only)
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

# Track check-ins
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
    st.warning("Room list not uploaded yet. Please contact staff.")

# ✅ ADMIN PANEL: Live Room Overview
if admin_mode and expected_rooms:
    st.divider()
    st.subheader("📊 Live Breakfast Overview")

    checked = st.session_state.checked_in
    remaining = expected_rooms - checked

    st.markdown(f"""
    ✅ **Checked-in:** {len(checked)} / {len(expected_rooms)}  
    🔲 **Remaining:** {len(remaining)}  
    """)

    # Scrollable view of all rooms
    with st.expander("📋 Full Room Status"):
        all_rooms = sorted(expected_rooms, key=int)
        for room in all_rooms:
            if room in checked:
                st.markdown(f"<div class='room-box checked'>✅ Room {room}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='room-box pending'>🔲 Room {room}</div>", unsafe_allow_html=True)
