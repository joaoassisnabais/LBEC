
class send_email():
    def __init__(self, calendar, date):
        self.calendar = calendar
        self.date = date
    
    def send_reminder_emails(self, smtp_server="smtp.gmail.com", port=587,
                             sender_email="railguntime@gmail.com", password="zmxp vpxg oeqf mjsl",
                             recipient_email="daniela.farinhacardoso@gmail.com"):
        """Sends email reminders for events within the next hour.

        Args:
            smtp_server (str, optional): The SMTP server address. Defaults to "smtp.example.com".
            port (int, optional): The SMTP server port. Defaults to 587.
            sender_email (str, optional): The email address of the sender. Defaults to "your_email@example.com".
            password (str, optional): The password for the sender's email account. Defaults to "your_password".
            recipient_email (str, optional): The email address of the recipient. Defaults to "recipient@example.com".
        """

        events_within_hour = self.get_events_within_hour()
        
        if not events_within_hour:
            print("No events found within the next hour.")
            return
        
        # Import smtplib for email sending (assuming it's not already imported)
        import smtplib

        # Create message content
        message_content = f"Upcoming event(s) within the next hour:\n"
        for events in events_within_hour:
            message_content += f"\n- {events.date}, {events.title}, {events.description}\n"

        # Create message (you can customize the format)
        message = f"From: {sender_email}\nSubject: Event Reminders\n\n{message_content}"

        # Connect to SMTP server
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # Start TLS encryption
            server.login(sender_email, password)  # Login with credentials
            server.sendmail(sender_email, recipient_email, message.encode())  # Send email
    
    def get_events_within_hour(self):
        events_today = self.calendar.get_events(self.date)
        remind = []
        for event in events_today:
            if event.date.hour <= self.date.hour + 1:
                remind.append(event)  
        return remind

    


