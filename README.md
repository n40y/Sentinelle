# 🛡️ Sentinelle

**Sentinelle** est un outil local de cybersécurité conçu pour aider à protéger les personnes vulnérables, notamment les personnes âgées, contre les arnaques et tentatives de phishing reçues par e-mail.

L'application surveille, en lecture seule, la boîte mail d'une personne protégée, analyse les nouveaux messages à la recherche de signaux suspects, attribue un score de risque et prévient un proche de confiance lorsqu'un message semble dangereux.

> **Sentinelle est une aide à la détection, pas une garantie.**
> Aucun système ne peut détecter 100 % des arnaques. L'objectif est d'ajouter une couche de protection supplémentaire, sans remplacer la vigilance, l'accompagnement ou le dialogue avec les proches.

---

## 📌 Sommaire

* [Présentation](#-présentation)
* [Objectif](#-objectif)
* [Fonctionnement](#-fonctionnement)
* [Principes de conception](#-principes-de-conception)
* [Fonctionnalités](#-fonctionnalités)
* [Détection des menaces](#-détection-des-menaces)
* [Architecture du projet](#-architecture-du-projet)
* [Pile technique](#-pile-technique)
* [Confidentialité et sécurité](#-confidentialité-et-sécurité)
* [Installation](#-installation)
* [Développement](#-développement)
* [Tests](#-tests)
* [Roadmap](#-roadmap)
* [Évolutions futures](#-évolutions-futures)
* [Limites](#-limites)
* [Licence](#-licence)

---

# 📖 Présentation

Les campagnes de phishing et les arnaques par e-mail peuvent prendre de nombreuses formes :

* faux colis ;
* faux messages bancaires ;
* faux impôts ou organismes publics ;
* faux services techniques ;
* demande urgente de paiement ;
* récupération de codes ou d'informations personnelles ;
* usurpation d'une marque ou d'un organisme connu.

Ces messages peuvent être particulièrement difficiles à identifier lorsque l'utilisateur n'est pas habitué aux mécanismes du phishing ou lorsqu'un message utilise les logos, noms et formulations d'un service connu.

**Sentinelle** cherche à apporter une réponse simple :

> surveiller discrètement la messagerie et demander l'intervention d'un proche lorsque quelque chose semble anormal.

L'utilisateur protégé n'a pas besoin d'analyser lui-même chaque message.

---

# 🎯 Objectif

Sentinelle suit quatre objectifs principaux :

1. **Surveiller** les nouveaux e-mails d'une boîte protégée.
2. **Analyser** chaque message avec plusieurs règles de détection.
3. **Expliquer** pourquoi un message est considéré comme suspect.
4. **Alerter** un proche de confiance lorsque le niveau de risque dépasse un certain seuil.

Le système doit fonctionner en arrière-plan et demander le moins d'interaction possible à la personne protégée.

---

# ⚙️ Fonctionnement

Le fonctionnement général est conçu autour d'une chaîne modulaire :

```text
                ┌──────────────────────┐
                │   Boîte mail         │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │    Mail Provider      │
                │ IMAP / autres APIs    │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │       Parser         │
                │  Normalisation mail  │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │      Analyzer        │
                │  règles de sécurité  │
                └──────────┬───────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
   ┌──────────────────┐        ┌──────────────────┐
   │      Scoring     │        │  Raisons détectées│
   │    0 → 100       │        │  et explications  │
   └────────┬─────────┘        └────────┬─────────┘
            └──────────────┬────────────┘
                           ▼
                ┌──────────────────────┐
                │  Seuil de risque     │
                └──────────┬───────────┘
                           │
                  ┌────────┴────────┐
                  ▼                 ▼
          ┌─────────────┐   ┌───────────────┐
          │ Notification│   │   Historique  │
          │ Telegram /  │   │    SQLite     │
          │ e-mail      │   │               │
          └─────────────┘   └───────────────┘
```

Le planificateur vérifie périodiquement l'arrivée de nouveaux messages. Seuls les messages encore inconnus sont analysés.

L'architecture est volontairement conçue pour ne pas dépendre définitivement d'IMAP : un autre fournisseur de messagerie pourra être ajouté plus tard sans modifier le moteur d'analyse.

---

# 🧩 Principes de conception

## Grand public

L'utilisateur ne doit pas avoir besoin d'utiliser un terminal.

À terme, Sentinelle doit être distribuable sous la forme d'une application installable (`.exe` / `.app`) avec un assistant de configuration graphique.

## Simple

L'interface doit rester volontairement limitée :

* peu de paramètres ;
* vocabulaire compréhensible ;
* valeurs par défaut raisonnables ;
* fonctionnement automatique.

## Lecture seule

Dans la première version, Sentinelle :

* ne supprime aucun e-mail ;
* ne déplace aucun e-mail ;
* ne modifie pas volontairement la boîte mail ;
* se contente d'observer, d'analyser et de signaler.

## Local d'abord

L'analyse doit être réalisée localement autant que possible.

Les services externes de réputation d'URL ou de domaine restent optionnels et désactivables.

## Respect de la vie privée

Sentinelle ne doit pas conserver inutilement le contenu des messages.

La base locale doit se limiter aux informations nécessaires au fonctionnement du système : identifiant du message, expéditeur, score, raisons de détection et éventuels retours utilisateur.

## Consentement

La personne protégée doit être informée du fonctionnement de l'application et pouvoir accéder à une fonction de pause ou de désinstallation.

Une icône visible dans la zone de notification indique que Sentinelle est actif.

## Explicabilité

Une alerte ne doit pas seulement dire :

> ⚠️ Message suspect

Elle doit expliquer **pourquoi**.

Exemple :

```text
Score : 78/100

Raisons :
- Reply-To différent de l'expéditeur
- Domaine du lien récemment créé
- Message contenant une formulation d'urgence
- Adresse proche d'une marque connue
```

---

# 🚨 Fonctionnalités

## Pour la personne protégée

* fonctionnement en arrière-plan ;
* icône visible dans la zone de notification ;
* indication de l'état du système ;
* aucune intervention quotidienne nécessaire ;
* possibilité de mettre le système en pause ;
* possibilité de désinstaller l'application.

## Pour l'aidant

* assistant de première configuration ;
* configuration du fournisseur de messagerie ;
* configuration des notifications ;
* réglage de la sensibilité ;
* réception d'alertes ;
* consultation de l'historique ;
* possibilité d'indiquer qu'un message signalé était légitime.

---

# 🔍 Détection des menaces

Le système repose initialement sur plusieurs familles de règles.

## En-têtes

Analyse notamment :

* SPF ;
* DKIM ;
* DMARC ;
* différence entre `From` et `Reply-To` ;
* incohérences dans les informations d'expédition.

## Usurpation

Détection possible de :

* marques connues utilisées dans le nom affiché ;
* domaine différent du domaine attendu ;
* domaines ressemblant fortement à une marque légitime ;
* fautes volontaires et typosquatting.

Exemples :

```text
paypa1.com
ameli-assure.fr
```

## Liens

Analyse de :

* différence entre le texte affiché et l'URL réelle ;
* raccourcisseurs d'URL ;
* domaines récemment créés ;
* réputation d'une URL ou d'un domaine ;
* domaines suspects.

## Pièces jointes

Détection d'extensions potentiellement dangereuses, notamment :

```text
.exe
.scr
.iso
.html
.js
```

ainsi que certains formats Office susceptibles de contenir des macros.

Sentinelle ne cherche pas à ouvrir ou exécuter les pièces jointes dans le cadre de son analyse initiale.

## Contenu

Recherche de schémas linguistiques associés à certaines arnaques :

* sentiment d'urgence ;
* menace de suspension ;
* demande de code ;
* demande de paiement ;
* demande de carte cadeau ;
* demande de virement ;
* formulations inhabituelles ou coercitives.

---

# 📊 Système de scoring

Chaque règle détectée produit un ou plusieurs signaux.

Ces signaux sont ensuite combinés pour produire un score compris entre **0 et 100**.

Exemple conceptuel :

```text
Reply-To suspect                 +20
Lien potentiellement frauduleux  +30
Urgence / menace                 +15
Pièce jointe à risque            +25
------------------------------------
Score                            90
```

Le résultat final pourra être associé à un niveau :

```text
0 – 29     → Faible
30 – 59    → Moyen
60 – 100   → Élevé
```

Les valeurs exactes pourront évoluer au fur et à mesure des tests.

L'objectif n'est pas seulement de produire un nombre : chaque point ajouté au score doit être associé à une **raison compréhensible**.

---

# 🏗️ Architecture du projet

```text
sentinelle/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
│
├── src/
│   └── sentinelle/
│       │
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── secrets.py
│       ├── scheduler.py
│       ├── autostart.py
│       │
│       ├── mail/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── models.py
│       │   ├── providers.py
│       │   ├── imap.py
│       │   ├── collector.py
│       │   └── parser.py
│       │
│       ├── analysis/
│       │   ├── analyzer.py
│       │   ├── scoring.py
│       │   ├── reputation.py
│       │   │
│       │   └── rules/
│       │       ├── headers.py
│       │       ├── links.py
│       │       ├── attachments.py
│       │       └── content.py
│       │
│       ├── notify/
│       │   ├── base.py
│       │   ├── telegram.py
│       │   └── email_notifier.py
│       │
│       ├── storage/
│       │   └── db.py
│       │
│       └── gui/
│           ├── wizard.py
│           ├── tray.py
│           ├── dashboard.py
│           └── settings.py
│
├── data/
│   ├── marques_surveillees.json
│   ├── mots_urgence_fr.json
│   └── extensions_risque.json
│
├── assets/
│   ├── icon_ok.png
│   ├── icon_warning.png
│   └── logo.png
│
├── tests/
│   ├── test_headers.py
│   ├── test_links.py
│   ├── test_content.py
│   ├── test_scoring.py
│   └── samples/
│
├── build/
│   └── sentinelle.spec
│
└── docs/
    ├── guide_aidant.md
    └── guide_personne_protegee.md
```

### Principe d'architecture

Chaque module doit avoir une responsabilité clairement définie.

Par exemple :

| Module         | Rôle                                   |
| -------------- | -------------------------------------- |
| `mail/`        | récupérer et normaliser les messages   |
| `analysis/`    | détecter les signaux suspects          |
| `notify/`      | envoyer les alertes                    |
| `storage/`     | conserver les informations nécessaires |
| `gui/`         | interaction avec l'utilisateur         |
| `scheduler.py` | exécuter les vérifications périodiques |
| `config.py`    | gérer la configuration                 |
| `secrets.py`   | gérer les identifiants sensibles       |

Cette séparation permet notamment de remplacer IMAP par une autre méthode de récupération des messages sans réécrire le moteur de détection.

---

# 🛠️ Pile technique

| Besoin              | Technologie prévue |
| ------------------- | ------------------ |
| Langage             | Python 3.11+       |
| Interface graphique | PySide6 ou C       |
