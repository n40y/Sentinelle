from abc import ABC, abstractmethod
from .models import MailMessage

class MailProvider(ABC):
    """
    Interface commune à toutes les sources de messagerie.

    Sentinelle ne doit pas dépendre directement d'IMAP, Gmail API, etc.
    """
    
    @abstractmethod
    def connect(self) -> None:
        """Établit la connexion au fournisseur."""
        raise NotImplementedError
    
    @abstractmethod
    def list_message_ids(self) -> list[str]:
        """Retourne les identifiants des messages disponibles."""
        raise NotImplementedError
    
    @abstractmethod
    def fetch_message(self, message_id: str) -> MailMessage:
        """Récupère un message brut à partir de son identifiant."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Ferme proprement la connexion."""
        raise NotImplementedError