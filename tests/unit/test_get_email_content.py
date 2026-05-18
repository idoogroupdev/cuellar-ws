from utils.functions.get_email_content import get_email_content


def test_get_email_content():

    code = "111111"

    html_content, text_content = get_email_content(
        "emails/account_verification_email", {"code": code}
    )

    assert code in text_content
    assert code in html_content
