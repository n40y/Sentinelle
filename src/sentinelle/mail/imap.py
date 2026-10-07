# src/sentinelle/mail/imap.py

import imaplib

from .base import MailProvider
from .models import MailMessage


class ImapMailProvider(MailProvider):
    """
    Implémentation du fournisseur de mails via IMAP.

    Cette classe ne doit gérer que :
    - la connexion ;
    - la récupération des identifiants ;
    - le téléchargement du message brut.

    Elle ne fait aucune analyse de sécurité.
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 993,
        mailbox: str = "INBOX",
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.mailbox = mailbox

        self._connection: imaplib.IMAP4_SSL | None = None

    def connect(self) -> None:
        """Connexion au serveur IMAP en TLS."""

        if self._connection is not None:
            return

        connection = imaplib.IMAP4_SSL(
            self.host,
            self.port,
        )

        connection.login(
            self.username,
            self.password,
        )

        # Lecture seule :
        # Sentinelle ne doit pas modifier la boîte mail.
        status, _ = connection.select(
            self.mailbox,
            readonly=True,
        )

        if status != "OK":
            connection.logout()
            raise RuntimeError(
                f"Impossible d'ouvrir la boîte '{self.mailbox}'."
            )

        self._connection = connection

    def list_message_ids(self) -> list[str]:
        """Retourne les UID des messages présents dans la boîte."""

        if self._connection is None:
            raise RuntimeError(
                "La connexion IMAP n'est pas établie."
            )

        status, data = self._connection.uid(
            "SEARCH",
            None,
            "ALL",
        )

        if status != "OK":
            raise RuntimeError(
                "Impossible de récupérer la liste des messages."
            )

        if not data or not data[0]:
            return []

        return data[0].decode("ascii").split()

    def fetch_message(self, message_id: str) -> MailMessage:
        """Récupère le contenu brut d'un message."""

        if self._connection is None:
            raise RuntimeError(
                "La connexion IMAP n'est pas établie."
            )

        status, data = self._connection.uid(
            "FETCH",
            message_id,
            "(BODY.PEEK[])",
        )

        if status != "OK":
            raise RuntimeError(
                f"Impossible de récupérer le message {message_id}."
            )

        raw_content: bytes | None = None

        for item in data:
            if isinstance(item, tuple) and len(item) == 2:
                raw_content = item[1]
                break

        if raw_content is None:
            raise RuntimeError(
                f"Aucun contenu trouvé pour le message {message_id}."
            )

        return MailMessage(
            message_id=message_id,
            raw_content=raw_content,
        )

    def close(self) -> None:
        """Ferme proprement la connexion."""

        if self._connection is None:
            return

        try:
            self._connection.close()
        finally:
            self._connection.logout()
            self._connection = None