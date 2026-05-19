from utils.functions.send_email import send_email


def test_send_email():

    result = send_email(emails=["test@test.com"], subject="Test", message="Test")

    result == 1
