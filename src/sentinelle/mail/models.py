# src/sentinelle/mail/models.py

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MailMessage:
    """
    Message brut récupéré par un fournisseur.
    """
    message_id: str
    raw_content: bytes


@dataclass
class AttachmentInfo:
    """
    Informations minimales sur une pièce jointe.
    On ne conserve pas son contenu.
    """
    filename: str | None
    content_type: str
    extension: str | None


@dataclass
class ParsedEmail:
    """
    Représentation normalisée d'un e-mail.

    Cette classe est utilisée par les modules d'analyse.
    Elle ne dépend d'aucun fournisseur de messagerie.
    """

    message_id: str

    subject: str | None
    sender_name: str | None
    sender_email: str | None
    reply_to: str | None

    date: str | None
    message_id_header: str | None

    headers: dict[str, str] = field(default_factory=dict)

    text_body: str = ""
    html_body: str = ""

    urls: list[str] = field(default_factory=list)
    attachments: list[AttachmentInfo] = field(default_factory=list)