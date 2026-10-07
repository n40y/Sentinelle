# src/sentinelle/mail/parser.py

from email import policy
from email.header import decode_header, make_header
from email.message import Message
from email.parser import BytesParser
from email.utils import parseaddr

from .models import AttachmentInfo, MailMessage, ParsedEmail


class MailParser:
    """
    Transforme un MailMessage brut en ParsedEmail.

    Le parser ne connaît pas :
    - IMAP
    - Gmail
    - Outlook
    - Telegram
    - SQLite

    Il reçoit simplement un message brut et retourne un objet normalisé.
    """

    def parse(self, message: MailMessage) -> ParsedEmail:
        email_message = BytesParser(
            policy=policy.default
        ).parsebytes(message.raw_content)

        headers = self._extract_headers(email_message)

        sender_name, sender_email = parseaddr(
            email_message.get("From", "")
        )

        reply_to = email_message.get("Reply-To")

        body_data = {
            "text": "",
            "html": "",
        }

        urls: list[str] = []
        attachments: list[AttachmentInfo] = []

        if email_message.is_multipart():
            for part in email_message.walk():
                self._process_part(
                    part,
                    body_data=body_data,
                    urls=urls,
                    attachments=attachments,
                )
        else:
            content_type = email_message.get_content_type()

            if content_type == "text/plain":
                body_data["text"] = self._decode_part(
                    email_message
                )

            elif content_type == "text/html":
                body_data["html"] = self._decode_part(
                    email_message
                )

        return ParsedEmail(
            message_id=message.message_id,
            subject=self._decode_header(
                email_message.get("Subject")
            ),
            sender_name=sender_name or None,
            sender_email=sender_email or None,
            reply_to=reply_to,
            date=email_message.get("Date"),
            message_id_header=email_message.get("Message-ID"),
            headers=headers,
            text_body=body_data["text"],
            html_body=body_data["html"],
            urls=urls,
            attachments=attachments,
        )

    def _process_part(
        self,
        part: Message,
        body_data: dict[str, str],
        urls: list[str],
        attachments: list[AttachmentInfo],
    ) -> None:
        """
        Traite une partie du message multipart.

        Important :
        nous ne conservons jamais le contenu binaire
        des pièces jointes.
        """

        if part.is_multipart():
            return

        content_type = part.get_content_type()
        disposition = part.get_content_disposition()

        if disposition == "attachment":
            filename = part.get_filename()

            attachments.append(
                AttachmentInfo(
                    filename=self._decode_header(filename),
                    content_type=content_type,
                    extension=self._get_extension(filename),
                )
            )

            return

        if content_type == "text/plain":
            body_data["text"] += self._decode_part(part)

        elif content_type == "text/html":
            body_data["html"] += self._decode_part(part)

    def _decode_part(self, part: Message) -> str:
        """
        Décode proprement le contenu texte d'une partie.
        """

        try:
            content = part.get_content()

            if isinstance(content, str):
                return content

        except (UnicodeDecodeError, AttributeError):
            pass

        payload = part.get_payload(decode=True)

        if not payload:
            return ""

        charset = part.get_content_charset() or "utf-8"

        try:
            return payload.decode(
                charset,
                errors="replace",
            )
        except LookupError:
            return payload.decode(
                "utf-8",
                errors="replace",
            )

    def _decode_header(self, value: str | None) -> str | None:
        if value is None:
            return None

        try:
            return str(make_header(decode_header(value)))
        except (ValueError, UnicodeDecodeError):
            return value

    def _extract_headers(
        self,
        message: Message,
    ) -> dict[str, str]:
        """
        Extrait les en-têtes intéressants pour Sentinelle.

        On pourra compléter cette liste plus tard.
        """

        interesting_headers = {
            "From",
            "To",
            "Reply-To",
            "Subject",
            "Date",
            "Message-ID",
            "Return-Path",
            "Received",
            "Authentication-Results",
        }

        result: dict[str, str] = {}

        for header in interesting_headers:
            value = message.get(header)

            if value is not None:
                result[header] = value

        return result

    def _get_extension(
        self,
        filename: str | None,
    ) -> str | None:
        if not filename:
            return None

        if "." not in filename:
            return None

        return "." + filename.rsplit(".", 1)[1].lower()