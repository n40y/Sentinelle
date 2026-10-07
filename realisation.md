# Étapes du projet


## 1. Faire fonctionner la lecture d'une boîte mail

Python
imaplib
connexion TLS
récupérer les derniers mails
récupérer uniquement les métadonnées nécessaires
comprendre les UID IMAP
ne surtout pas commencer par scanner toute une boîte


## 2. Transformer un mail en objet exploitable
Créer par exemple un objet EmailMessage contenant :

expéditeur
Reply-To
sujet
date
en-têtes SPF/DKIM/DMARC lorsqu'ils sont disponibles
URLs
pièces jointes
texte du message

C'est le rôle que tu as prévu pour parser.py.


## 3. Construire le moteur de détection
Je commencerais volontairement avec seulement 3 règles :

```bash
Reply-To différent de From       → +20
Lien suspect                     → +30
Vocabulaire d'urgence            → +15
```
Puis un scoring.py qui transforme ces signaux en :

0–29    faible
30–59   moyen
60–100  élevé

Le but n'est pas d'avoir une IA parfaite : c'est de construire un système compréhensible et explicable.


## 4. Ajouter Telegram

Une fois que :

mail → analyse → score

fonctionne en console, tu ajoutes :

score élevé → Telegram

C'est exactement le découpage prévu dans ton README.


## 5. Ajouter SQLite

Tu stockeras uniquement ce que tu as prévu :

identifiant du mail
expéditeur
score
raisons
statut légitime/suspect

et pas le corps du mail ni les pièces jointes, conformément à ton principe de confidentialité.


## 6. Interface

À ce stade, je choisirais probablement PySide6 plutôt que CustomTkinter si tu veux arriver à une application réellement propre et distribuable.

Ton interface pourra ensuite encapsuler tout ce qui existe déjà :

                 SENTINELLE
                     │
        ┌────────────┴────────────┐
        │                         │
     Interface                 Service
        │                         │
        │                   Planificateur
        │                         │
        │                    Collecteur IMAP
        │                         │
        │                       Parser
        │                         │
        │                      Analyzer
        │                         │
        │                      Scoring
        │                         │
        └───────────────┬─────────┘
                        │
                    SQLite
                        │
              Telegram / Email

