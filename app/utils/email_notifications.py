import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email_notification(to_email, subject, body):
    from_email = 'shawaibsyedruby@gmail.com'
    from_password = 'qexxxjicloqpgylz'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()
    print("Email sent successfully")

def send_event_registration_successful_notification(event, participant_email, participant_name):
    subject = f"Event Insights Hub | Successfully registered to {event.get("EventName")}"
    body = f"""Hi {participant_name},

You have successfully registered for the event {event.get("EventName")}.

Description: {event.get("Description")}
Location: {event.get("EventLocation")}
Date & Time: {datetime.strptime(event.get("EventDateTime"), "%Y-%m-%dT%H:%M:%SZ").strftime("%d, %b %Y %H:%M")}


Best regards,
Event Insight Hub Team
"""

    print("Sending Event Registration Successful notification")
    send_email_notification(participant_email, subject, body)

def send_event_updated_notification(event, participant_email, participant_name):
    subject = f"Event Insights Hub | {event.get("EventName")} has been updated"
    body = f"""Hi {participant_name},

Event {event.get("EventName")} has been updated.

{
(f'Description: {event.get("Description")}\n' if event.get("Description") else '') + \
(f'Location: {event.get("EventLocation")}\n' if event.get("EventLocation") else '') + \
(f'Date & Time: {datetime.strptime(event.get("EventDateTime"), "%Y-%m-%dT%H:%M:%SZ").strftime("%d, %b %Y %H:%M")}\n' if event.get("EventDateTime") else '')
}

Best regards,
Event Insight Hub Team
"""

    print("Sending Event Registration Successful notification")
    send_email_notification(participant_email, subject, body)

def send_participant_registration_successful_notification(participant_email, participant_name):
    subject = f"Event Insights Hub | Welcome {participant_name}"
    body = f"""Hi {participant_name},

Welcome to Event Insights Hub!!

Best regards,
Event Insight Hub Team
"""

    print("Sending Participant Registration Successful notification")
    send_email_notification(participant_email, subject, body)

def send_event_deleted_notification(event, participant_email, participant_name):
    subject = f"Event Insights Hub | {event.get("EventName")} has been cancelled"
    body = f"""Hi {participant_name},

This is to notify that the event {event.get("EventName")} has been cancelled.

Best regards,
Event Insight Hub Team
"""

    print("Sending Event Cancelled notification")
    send_email_notification(participant_email, subject, body)

if __name__ == "__main__":
    # send_participant_registration_successful_notification("shawaibsyed@gmail.com", "Shoaib")
    event = {
        "Description": "Engagement with Rim",
        "EventDateTime": "2024-07-16T15:00:00Z",
        "EventID": "4d5a8c09-1ff7-468f-a187-53f0f42fb0d7",
        "EventLocation": "HBR Layout near Elements mall",
        "Feedback": [
            {
                "Comment": "Did not keep Paneer at all. Extremely disappointed!! Will not attend marriage if paneer not kept",
                "FeedbackID": "7bf1eb8e-b3aa-4309-bb57-d8c956c7a240",
                "ParticipantID": "bf53a085-5fd0-4666-b9db-20c2454b8d2b",
                "Rating": "3"
            }
        ],
        "EventName": "Shoaib's engagement",
        "OrganizerID": "ebd577af-35e8-4433-b5ca-9b3b82991d75",
        "Participants": [
            "bf53a085-5fd0-4666-b9db-20c2454b8d2b"
        ]
    }
    send_event_deleted_notification(event, "shawaibsyed@gmail.com", "Shoaib")
