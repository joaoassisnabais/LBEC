import calendar
from EventCalendar import Event, Calendar
from export import send_email
from datetime import date, datetime


event1 = Event("Meeting", datetime(2024, 3, 17, 5), "Project discussion")

event2 = Event("Ronaldo", datetime(2024, 3, 17, 6), "LBEC")

event3 = Event("Beira Interior", datetime(2024, 4, 24), "Maranho")


calendar = Calendar()
calendar.add_event(event1)
calendar.add_event(event2)
calendar.add_event(event3)

mail = send_email(calendar, datetime(2024,3,17,4))
mail.send_reminder_emails()

# Remove the meeting event (assuming only one meeting event exists)
calendar.remove_event(event2)


calendar.remove_event(event1)

print("sewy")

