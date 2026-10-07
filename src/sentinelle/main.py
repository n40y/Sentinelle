# src/sentinelle/main.py

import getpass

from .config import MailConfig
from .mail.imap import ImapMailProvider


def main() -> None:
    print("=== Sentinelle - test IMAP ===")

    host = input("Serveur IMAP : ").strip()
    username = input("Adresse e-mail : ").strip()
    password = getpass.getpass("Mot de passe / mot de passe d'application : ")

    config = MailConfig(
        host=host,
        username=username,
        password=password,
    )

    provider = ImapMailProvider(
        host=config.host,
        username=config.username,
        password=config.password,
        port=config.port,
        mailbox=config.mailbox,
    )

    try:
        print("\nConnexion...")
        provider.connect()

        print("Connexion réussie.")

        message_ids = provider.list_message_ids()

        print(f"{len(message_ids)} message(s) trouvé(s).")

        if message_ids:
            latest_id = message_ids[-1]

            print(f"\nRécupération du message {latest_id}...")

            message = provider.fetch_message(latest_id)

            print(
                f"Message récupéré : "
                f"{len(message.raw_content)} octets"
            )

    finally:
        provider.close()
        print("Connexion fermée.")


if __name__ == "__main__":
    main()