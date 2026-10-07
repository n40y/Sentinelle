# src/tests/test_parser.py

from sentinelle.mail.models import MailMessage
from sentinelle.mail.parser import MailParser


def test_parse_simple_email():
    raw_email = b"""\
From: Jean Dupont <jean@example.com>
To: pierre@example.com
Subject: Bonjour
Date: Wed, 7 Oct 2026 20:00:00 +0200
Message-ID: <123@example.com>
Reply-To: autre@example.com>
Content-Type: text/plain; charset="utf-8"

Bonjour Pierre,

Ceci est un message de test.
"""

    message = MailMessage(
        message_id="42",
        raw_content=raw_email,
    )

    parser = MailParser()

    result = parser.parse(message)

    assert result.message_id == "42"
    assert result.subject == "Bonjour"
    assert result.sender_name == "Jean Dupont"
    assert result.sender_email == "jean@example.com"
    assert result.reply_to == "autre@example.com"
    assert "message de test" in result.text_body