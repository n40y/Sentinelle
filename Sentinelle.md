# 🛡️ Sentinelle

**Un gardien discret qui surveille la boîte mail d'un proche vulnérable et prévient son aidant dès qu'un message ressemble à une arnaque.**

> Dossier local à créer : `sentinelle/`

---

## 1. Objectif

Les personnes âgées sont des cibles privilégiées du phishing et des arnaques par mail (faux colis, faux impôts, faux conseiller bancaire, faux support technique...). Sentinelle :

1. lit (en lecture seule) la boîte mail de la personne protégée ;
2. attribue à chaque nouveau message un **score de risque** et en explique les raisons ;
3. **alerte l'aidant** (un proche de confiance) par Telegram ou par e-mail quand le score dépasse un seuil ;
4. fonctionne en arrière-plan, **sans que la personne protégée n'ait rien à faire**.

## 2. Principes de conception

| Principe | Conséquence concrète |
|---|---|
| **Grand public** | Aucun terminal. Application installable (un `.exe` / `.app`) avec un assistant de configuration graphique. |
| **Simple** | Un seul écran de réglages, des mots clairs, des valeurs par défaut sensées. |
| **Lecture seule** | Dans la v1, l'outil ne supprime et ne déplace aucun mail. Il signale uniquement. |
| **Local d'abord** | L'analyse se fait sur l'ordinateur. Rien n'est envoyé à un serveur tiers, sauf les URL vérifiées via les services de réputation (désactivable). |
| **Respect de la vie privée** | On ne stocke ni le corps des mails ni les pièces jointes. Uniquement : identifiant du mail, expéditeur, score, raisons. |
| **Consentement** | La personne protégée est informée et d'accord. L'application affiche une icône visible dans la zone de notification. |
| **Explicable** | Chaque alerte dit *pourquoi* (ex. « domaine créé il y a 3 jours »). |

## 3. Fonctionnalités de la v1

### Pour la personne protégée
- Icône dans la barre des tâches (vert = tout va bien, orange/rouge = alerte récente).
- Aucune manipulation requise au quotidien.

### Pour l'aidant
- Assistant de première configuration (voir §6).
- Alerte instantanée avec : expéditeur, objet, score, liste des raisons.
- Tableau de bord local : historique des alertes, bouton « c'était légitime » pour affiner.
- Réglage de la sensibilité (Prudent / Équilibré / Discret).

### Détection (règles)
- **En-têtes** : échec SPF / DKIM / DMARC, `Reply-To` différent de l'expéditeur.
- **Usurpation** : nom affiché d'une marque connue mais adresse d'un autre domaine ; domaines à fautes volontaires (`paypa1.com`, `ameli-assure.fr`...).
- **Liens** : texte du lien différent de l'URL réelle, raccourcisseurs, domaines très récents, URL signalées par des bases de réputation.
- **Pièces jointes** : extensions à risque (`.exe`, `.scr`, `.iso`, `.html`, `.js`, macros Office).
- **Contenu** : vocabulaire d'urgence ou de menace (« dernier avertissement », « compte suspendu »), demande de codes, de cartes cadeaux, de virements.

## 4. Pile technique

| Besoin | Choix |
|---|---|
| Langage | Python 3.11+ |
| Interface graphique | `customtkinter` (simple, léger) ou `PySide6` si tu veux plus de finition |
| Icône de zone de notification | `pystray` + `Pillow` |
| Lecture des mails | `imaplib` + `email` (bibliothèque standard) |
| Stockage de la config | JSON via `platformdirs` (dossier utilisateur de l'OS) |
| Stockage des mots de passe | `keyring` (coffre-fort du système, jamais en clair) |
| Base de données | SQLite (`sqlite3`, bibliothèque standard) |
| Requêtes HTTP | `requests` |
| Âge de domaine | `python-whois` |
| Empaquetage | `PyInstaller` (génère l'exécutable à double-cliquer) |
| Démarrage automatique | Dossier « Démarrage » de Windows / LaunchAgent macOS |

## 5. Arborescence et rôle de chaque fichier

```
sentinelle/
├── README.md                     # Ce document
├── LICENSE                       # Licence du projet
├── .gitignore                    # Exclut config, base locale, builds, secrets
├── requirements.txt              # Dépendances Python
│
├── src/
│   └── sentinelle/
│       ├── __init__.py           # Version du projet
│       ├── main.py               # Point d'entrée : 1er lancement -> assistant, sinon -> service + icône
│       ├── config.py             # Lit/écrit la configuration (seuil, fréquence, canal d'alerte...)
│       ├── secrets.py            # Enregistre/récupère les mots de passe via `keyring`
│       ├── scheduler.py          # Boucle de fond : toutes les N minutes, collecte -> analyse -> alerte
│       ├── autostart.py          # Active/désactive le lancement automatique avec la session
│       │
│       ├── mail/
│       │   ├── providers.py      # Préréglages IMAP (Gmail, Outlook, Orange, Free, SFR, Yahoo...)
│       │   ├── collector.py      # Connexion IMAP en lecture seule, récupère les nouveaux mails
│       │   └── parser.py         # Transforme un mail brut en objet propre (en-têtes, liens, pièces jointes)
│       │
│       ├── analysis/
│       │   ├── analyzer.py       # Orchestre toutes les règles et produit le résultat final
│       │   ├── scoring.py        # Combine les signaux en score 0-100 + niveau (faible/moyen/élevé)
│       │   ├── reputation.py     # Vérifie URL/domaines (Safe Browsing, URLhaus, âge WHOIS)
│       │   └── rules/
│       │       ├── headers.py    # SPF/DKIM/DMARC, Reply-To, incohérences d'expéditeur
│       │       ├── links.py      # Liens trompeurs, raccourcisseurs, typosquatting
│       │       ├── attachments.py# Extensions et types de fichiers dangereux
│       │       └── content.py    # Mots et schémas d'urgence / de menace / de demande d'argent
│       │
│       ├── notify/
│       │   ├── base.py           # Interface commune d'un canal d'alerte
│       │   ├── telegram.py       # Alerte via un bot Telegram
│       │   └── email_notifier.py # Alerte par e-mail (SMTP) vers l'aidant
│       │
│       ├── storage/
│       │   └── db.py             # SQLite : mails déjà vus, scores, raisons, retours « légitime »
│       │
│       └── gui/
│           ├── wizard.py         # Assistant de configuration pas à pas (voir §6)
│           ├── tray.py           # Icône de zone de notification et son menu
│           ├── dashboard.py      # Historique des alertes + bouton « c'était légitime »
│           └── settings.py       # Réglages : sensibilité, fréquence, canal d'alerte, pause
│
├── data/
│   ├── marques_surveillees.json  # Marques/organismes usurpés (banques, Ameli, impôts, La Poste...)
│   ├── mots_urgence_fr.json      # Expressions d'urgence et de menace typiques
│   └── extensions_risque.json    # Extensions de fichiers à risque
│
├── assets/
│   ├── icon_ok.png               # Icône « tout va bien »
│   ├── icon_warning.png          # Icône « alerte récente »
│   └── logo.png                  # Logo affiché dans l'assistant
│
├── tests/
│   ├── test_headers.py           # Tests des règles d'en-têtes
│   ├── test_links.py             # Tests des règles de liens
│   ├── test_content.py           # Tests des règles de contenu
│   ├── test_scoring.py           # Tests du calcul de score
│   └── samples/                  # Mails d'exemple (phishing et légitimes) en .eml
│
├── build/
│   └── sentinelle.spec           # Configuration PyInstaller pour générer l'exécutable
│
└── docs/
    ├── guide_aidant.md           # Installation et usage côté aidant
    └── guide_personne_protegee.md# Explication courte et rassurante pour la personne protégée
```

## 6. Parcours de configuration (assistant graphique)

1. **Bienvenue** : explication de ce que fait l'outil et de ce qu'il ne fait pas (il ne supprime rien, il ne lit que ce qu'il faut).
2. **Choix du fournisseur mail** : liste déroulante (Gmail, Outlook, Orange...). Les serveurs IMAP sont préremplis.
3. **Connexion** : adresse + *mot de passe d'application*, avec un guide illustré pour le créer chez le fournisseur. Bouton « Tester la connexion ».
4. **Choix de l'alerte** : Telegram (recommandé) ou e-mail.
   - Telegram : l'aidant envoie un message à un bot, l'application détecte automatiquement son identifiant de conversation (aucune manipulation technique).
   - E-mail : saisie de l'adresse de l'aidant.
5. **Sensibilité** : Prudent / Équilibré / Discret.
6. **Test** : envoi d'une alerte factice pour vérifier que tout fonctionne.
7. **Terminé** : l'application passe en arrière-plan et se lancera à chaque démarrage.

## 7. Flux de fonctionnement

```
Planificateur (toutes les 2-5 min)
   -> Collector : nouveaux mails (UID non vus en base)
   -> Parser : mail normalisé
   -> Analyzer : règles headers / links / attachments / content + réputation
   -> Scoring : score 0-100
   -> score >= seuil ? -> Notifier (Telegram / e-mail) + enregistrement en base
   -> mise à jour de l'icône de zone de notification
```

## 8. Sécurité et vie privée

- Mot de passe d'application uniquement (jamais le vrai mot de passe), stocké dans le coffre-fort du système.
- Connexion IMAP chiffrée (SSL/TLS) obligatoire.
- Aucun contenu de mail conservé : seulement métadonnées et raisons de l'alerte.
- Vérifications de réputation désactivables dans les réglages (mode 100 % local).
- Le tableau de bord n'est accessible qu'en local.
- Bouton « Pause / Désinstaller » toujours accessible à la personne protégée.

## 9. Feuille de route

- **v0.1** : collecteur IMAP + notifieur Telegram + 3 règles de base (en console, pour valider l'idée).
- **v0.2** : analyseur complet (headers, liens, pièces jointes, contenu) + SQLite.
- **v0.3** : interface graphique : assistant, icône de zone de notification, réglages.
- **v0.4** : réputation d'URL, âge de domaine, retours « c'était légitime ».
- **v1.0** : exécutables Windows et macOS, guides utilisateur, tests sur de vrais cas.
- **Ensuite** :
  - connexion OAuth (Gmail/Outlook) pour éviter les mots de passe d'application ;
  - analyse des SMS ;
  - filtrage des appels (liste blanche, numéros signalés) ;
  - mise en quarantaine optionnelle ;
  - version mobile.

## 10. Avertissement

Sentinelle est une aide, pas une garantie : aucun outil ne détecte 100 % des arnaques. Il complète, sans la remplacer, la vigilance et le dialogue avec les proches. En cas d'arnaque avérée : opposition bancaire, plainte, signalement sur **signal-spam.fr**, **Cybermalveillance.gouv.fr** et **17Cyber**.