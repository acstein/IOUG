import streamlit as st
import json
import streamlit.components.v1 as components
from supabase_client import get_supabase

st.set_page_config(page_title="Conference Schedule", layout="wide")
supabase = get_supabase()

# -------------------------------
# Load events from Supabase
# -------------------------------
def load_events():
    response = supabase.table("Events").select("*").execute()
    events = response.data or []
    # FullCalendar format
    return [
        {
            "id": ev["id"],
            "title": ev["title"],
            "start": ev["start"],
            "end": ev["end"],
            "colour": ev.get("colour", "#4a90e2")
        }
        for ev in events
    ]

def update_event(event_id, start, end):
    supabase.table("Events").update({
        "start": start,
        "end": end
    }).eq("id", event_id).execute()


# --------------------------------
# Main page UI
# --------------------------------
st.title("📅 Conference Schedule")

# Holder to capture JS events
if "calendar_update" not in st.session_state:
    st.session_state.calendar_update = None

# Detect update request from JS
params = st.query_params
if "updated_event" in params:
    updated = json.loads(params["updated_event"][0])
    st.session_state.calendar_update = updated

# Apply updates
if st.session_state.calendar_update:
    ev = st.session_state.calendar_update
    update_event(ev["id"], ev["start"], ev["end"])
    st.success(f"Updated: {ev['title']}")
    st.session_state.calendar_update = None

events = load_events()

# -------------------------------
# Render FullCalendar
# -------------------------------
calendar_html = f"""
<!DOCTYPE html>
<html>
<head>
<link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.css' rel='stylesheet' />
<script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js'></script>

<style>
  body {{
    background: #f7f7f9;
    font-family: Sans-serif;
  }}

  #calendar {{
    max-width: 1200px;
    margin: 20px auto;
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  }}

  .fc-event {{
    border-radius: 8px;
    padding: 3px 6px;
    color: white !important;
    border: none;
  }}
</style>
</head>

<body>

<div id='calendar'></div>

<script>
document.addEventListener('DOMContentLoaded', function() {{

  var calendarEl = document.getElementById('calendar');

  var calendar = new FullCalendar.Calendar(calendarEl, {{
    initialView: 'timeGridWeek',
    editable: true,
    selectable: true,
    allDaySlot: false,
    expandRows: true,
    slotMinTime: "08:00:00",
    slotMaxTime: "22:00:00",
    events: {json.dumps(events)},

    eventDrop: function(info) {{
      sendUpdate(info.event);
    }},
    eventResize: function(info) {{
      sendUpdate(info.event);
    }},
  }});

  calendar.render();

  function sendUpdate(event) {{
    const updated = {{
      id: event.id,
      title: event.title,
      start: event.start.toISOString(),
      end: event.end.toISOString()
    }};
    const encoded = encodeURIComponent(JSON.stringify(updated));
    window.location.search = "?updated_event=" + encoded;
  }}

}});
</script>

</body>
</html>
"""

components.html(calendar_html, height=800, scrolling=True)
