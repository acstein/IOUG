import streamlit as st
import pandas as pd
from datetime import time
from supabase_client import get_supabase

supabase = get_supabase()

st.title("⚙️ Edit Schedule")

# -------------------------------
# Supabase event functions
# -------------------------------
def load_events():
    response = supabase.table("Events").select("*").execute()
    return response.data or []

def add_event(title, start, end, colour):
    supabase.table("Events").insert({
        "title": title,
        "start": start,
        "end": end,
        "colour": colour
    }).execute()

def delete_event(event_id):
    supabase.table("Events").delete().eq("id", event_id).execute()


# -------------------------------
# Add Event Form
# -------------------------------
st.subheader("➕ Add New Event")

day_map = {
    "Monday": "2025-03-10",
    "Tuesday": "2025-03-11",
    "Wednesday": "2025-03-12",
    "Thursday": "2025-03-13",
    "Friday": "2025-03-14",
}

with st.form("add_event_form"):
    title = st.text_input("Title")

    col1, col2, col3 = st.columns(3)
    with col1:
        day = st.selectbox("Day", list(day_map.keys()))
    with col2:
        start_time = st.time_input("Start", time(9, 0))
    with col3:
        end_time = st.time_input("End", time(10, 0))

    colour = st.color_picker("Colour", "#4a90e2")

    submit = st.form_submit_button("Add Event")

if submit:
    if end_time <= start_time:
        st.error("End must be after start")
    else:
        start = f"{day_map[day]}T{start_time.strftime('%H:%M')}:00"
        end = f"{day_map[day]}T{end_time.strftime('%H:%M')}:00"
        add_event(title, start, end, colour)
        st.success(f"Added: {title}")
        st.experimental_rerun()


# -------------------------------
# Delete existing events
# -------------------------------
st.subheader("🗂 Existing Events")
events = load_events()

if not events:
    st.info("No events yet.")
else:
    df = pd.DataFrame(events)
    st.dataframe(df, use_container_width=True)

    for ev in events:
        with st.expander(f"{ev['title']} – {ev['start']}"):
            if st.button("Delete", key=ev["id"]):
                delete_event(ev["id"])
                st.experimental_rerun()
