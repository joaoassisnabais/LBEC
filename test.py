import calendar
from EventCalendar import Event, Calendar
from datetime import date, datetime


event1 = Event("Meeting", datetime(2024, 3, 18), "Project discussion", 10, 11)

event2 = Event("Ronaldo", datetime(2024, 3, 18), "LBEC", 15, 21)


event3 = Event("Beira Interior", datetime(2024, 4, 24), "Maranho", 7, 12)


calendar = Calendar()
calendar.add_event(event1)
calendar.add_event(event2)
calendar.add_event(event3)

# Remove the meeting event (assuming only one meeting event exists)
calendar.remove_event(event2)


calendar.remove_event(event1)

print("sewy")

