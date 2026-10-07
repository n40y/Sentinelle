# src/sentinelle/config.py

from dataclasses import dataclass

@dataclass(frozen=True)
class MailConfig:
    host:   str
    username:   str
    password:   str
    port:       int = 993
    mailbox:    str = "INBOX"