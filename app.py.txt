import streamlit as st

st.set_page_config(page_title="Breakfast Self Check-In", page_icon="🍽️", layout="centered")
st.markdown("<h1 style='text-align: center;'>🍳 Breakfast Self Check-In</h1>", unsafe_allow_html=True)

# Hide Streamlit menu and footer
st.markdown("""
    <style>
        #MainMenu, footer {visibility: hidden;}
        .stTextInput > div > div > input {font-size: 28px; height: 50px;}
        .stButton button {font-size: 24px; padding: 12px;}
    </style>
""", unsafe_allow_html=True)

# Upload expected room list (only once by staff)
uploaded_file = st.file_uploader("Upload today's room list (.txt)", type="txt")
if uploaded_file:
    expected_rooms = set(
        line.strip() for line in uploaded_file.getvalue().decode("utf-8").splitlines()
        if line.strip().isdigit() and 100 <= int(line.strip()) <= 639
    )
    st.success(f"{len(expected_rooms)} expected rooms loaded.")
else:
    st.warning("Waiting for room list upload...")
    st.stop()

# Store checked-in rooms (no unexpected guests here)
if "checked_in" not in st.session_state:
    st.session_state.checked_in = set()

# Input field for guests
room_input = st.text_input("Enter your room number to check in:", placeholder="e.g. 215")

if st.button("✅ Check In"):
    room = room_input.strip()
    if not room.isdigit():
        st.error("Please enter a valid room number.")
    elif int(room) < 100 or int(room) > 639:
        st.error("Room number out of range.")
    elif room in st.session_state.checked_in:
        st.info(f"Room {room} has already been checked in. Enjoy your breakfast! 🥐")
    elif room in expected_rooms:
        st.session_state.checked_in.add(room)
        st.success(f"✅ Room {room} successfully checked in. Bon appétit! 🍽️")
    else:
        st.error("Room not found on today's list. Please speak to staff.")

# Optional: show checked-in rooms
with st.expander("✅ View checked-in rooms (for staff only)"):
    st.write(", ".join(sorted(st.session_state.checked_in)) or "None")
