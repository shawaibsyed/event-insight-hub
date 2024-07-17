from unittest.mock import patch
from app.utils.email_notifications import send_event_registration_successful_notification

@patch('app.utils.email_notifications.send_email_notification')
def test_send_event_registration_successful_notification(mock_send_email):
    event = {
        "EventName": "Test Event",
        "Description": "A test event",
        "EventLocation": "Test Location",
        "EventDateTime": "2024-07-16T15:00:00Z"
    }
    send_event_registration_successful_notification(event, 'test@example.com', 'Test User')
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    assert args[0] == 'test@example.com'
    assert 'Successfully registered to Test Event' in args[1]
    assert 'You have successfully registered for the event Test Event.' in args[2]
