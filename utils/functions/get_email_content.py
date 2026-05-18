from django.template.loader import render_to_string


def get_email_content(template_name: str, context: dict):
    """Return html and text content

    template_name: template name,not include file extension
    """

    text_content = render_to_string(f"{template_name}.txt", context)
    html_content = render_to_string(f"{template_name}.html", context)

    return html_content, text_content
