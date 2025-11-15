import streamlit as st
import json
import streamlit.components.v1 as components
from supabase_client import get_supabase

st.set_page_config(page_title="Schedule", layout="wide")
supabase = get_supabase()

# -------------------------------
# Load events from Supabase
# -------------------------------
def load_events():
    response = supabase.table("Events").select("*").execute()
    events = response.data or []

    return [
        {
            "id": ev["id"],
            "title": ev["title"],
            "start": ev["start"],   # full ISO datetime
            "end": ev["end"],
            "color": ev.get("colour", "#4a90e2"),  # FullCalendar uses "color"
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
st.title("Conference Schedule")

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
<html lang="en-gb">
<head>
<link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.css' rel='stylesheet' />
<script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js'></script>

<style>
  body {{
    background: #f0f2f6;
    font-family: Sans-serif;
  }}

  #calendar {{
    max-width: 1200px;
    margin: 20px auto;
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  }}

  .fc-event {{
    border-radius: 6px;
    border: none !important;
    padding: 2px 4px;
    font-size: 0.8rem;
    white-space: normal;       /* allow text wrap */
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  .fc-event-title {{
    line-height: 1.1;
  }}
</style>
</head>

<body>

<div id='calendar'></div>

<script>
document.addEventListener('DOMContentLoaded', function() {{

  // Function to determine readable text color based on background
  function getContrastYIQ(hexcolor){{
      hexcolor = hexcolor.replace("#", "");
      var r = parseInt(hexcolor.substr(0,2),16);
      var g = parseInt(hexcolor.substr(2,2),16);
      var b = parseInt(hexcolor.substr(4,2),16);
      var yiq = ((r*299)+(g*587)+(b*114))/1000;
      return (yiq >= 128) ? 'black' : 'white';
  }}

  var calendarEl = document.getElementById('calendar');

  var calendar = new FullCalendar.Calendar(calendarEl, {{
    locale: 'en-gb',                  // UK date format
    initialView: 'timeGridWeek',
    initialDate: '2025-12-01',        // pinned conference week
    editable: true,
    selectable: true,
    allDaySlot: false,
    expandRows: true,

    slotMinTime: "08:30:00",
    slotMaxTime: "17:00:00",

    eventTimeFormat: {{               // 24-hour time
      hour: "2-digit",
      minute: "2-digit",
      hour12: false
    }},

    events: {json.dumps(events)},

    eventDrop: function(info) {{
      sendUpdate(info.event);
    }},
    eventResize: function(info) {{
      sendUpdate(info.event);
    }},

    eventDidMount: function(info) {{
      // Tooltip for full title
      info.el.setAttribute('title', info.event.title);

      // Force background and readable text color for all views
      let color = info.event.backgroundColor || info.event.color || '#4a90e2';
      info.el.style.backgroundColor = color;
      info.el.style.color = getContrastYIQ(color);
      info.el.style.border = 'none';
    }}
  }});

  calendar.render();

  // ------------------------------
  // Mobile responsiveness
  // ------------------------------
  function handleResize() {{
      if (window.innerWidth < 768) {{
          calendar.changeView('listWeek');
      }} else {{
          calendar.changeView('timeGridWeek');
      }}
  }}

  window.addEventListener('resize', handleResize);
  handleResize();  // call once on load

  // ------------------------------
  // Send drag/drop updates to Streamlit
  // ------------------------------
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

components.html(calendar_html, height=650, scrolling=True)
