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

| Besoin                  | Technologie prévue       |
| ----------------------- | ------------------------ |
| Langage                 | Python 3.11+             |
| Interface graphique     | PySide6 ou CustomTkinter |
| Zone de notification    | pystray + Pillow         |
| Lecture des mails       | IMAP / `imaplib`         |
| Parsing e-mail          | `email`                  |
| Configuration           | JSON + `platformdirs`    |
| Secrets                 | `keyring`                |
| Base de données         | SQLite                   |
| Requêtes HTTP           | `requests`               |
| Informations de domaine | `python-whois`           |
| Empaquetage             | PyInstaller              |
| Tests                   | pytest                   |

La technologie de récupération des messages reste volontairement abstraite dans l'architecture afin de permettre l'ajout d'autres fournisseurs ou APIs ultérieurement.

---

# 🔐 Confidentialité et sécurité

La protection des données personnelles fait partie intégrante du projet.

Sentinelle doit notamment respecter les principes suivants :

### Identifiants

Le mot de passe principal de la boîte mail ne doit pas être stocké en clair.

La première version privilégie l'utilisation d'un **mot de passe d'application** lorsque le fournisseur le permet.

Les secrets sont destinés à être stockés via le coffre-fort du système avec `keyring`.

### Connexion

La connexion à la messagerie doit utiliser une connexion chiffrée TLS.

### Stockage

Le contenu complet des e-mails et les pièces jointes ne doivent pas être conservés dans la base de données de Sentinelle.

### Services externes

Les services de réputation doivent pouvoir être désactivés afin de permettre un mode de fonctionnement entièrement local.

### Contrôle utilisateur

Le tableau de bord reste local et la personne protégée doit pouvoir mettre le système en pause ou le désinstaller.

---

# 📦 Installation

## Pré-requis

* Python 3.11 ou supérieur ;
* Git ;
* une boîte mail compatible avec le mode de connexion utilisé ;
* pour les tests de notification : un compte Telegram configuré ou une adresse e-mail de réception.

## Cloner le projet

```bash
git clone https://github.com/n40y/Sentinelle.git
cd Sentinelle
```

## Créer un environnement virtuel

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Installer les dépendances

```bash
pip install -r requirements.txt
```

> Le projet est actuellement en développement. Les instructions d'installation et la liste des dépendances évolueront avec les différentes versions de Sentinelle.

---

# 🧪 Développement et tests

Les règles de détection doivent être développées avec des tests automatisés.

Les tests utilisent autant que possible des **messages e-mail fictifs ou anonymisés**, plutôt que de véritables messages contenant des données personnelles.

Exemple :

```bash
pytest
```

Les différents composants doivent pouvoir être testés indépendamment :

```text
Parser
  ↓
tests parser

Headers rules
  ↓
tests headers

Links rules
  ↓
tests links

Scoring
  ↓
tests scoring
```

L'objectif est d'éviter qu'une modification d'une règle de détection casse silencieusement une autre partie du système.

---

# 🗺️ Roadmap

## v0.1 — Preuve de concept

Objectif : valider le fonctionnement du cœur du projet.

* [x] Première structure du projet
* [ ] Abstraction `MailProvider`
* [ ] Collecteur IMAP
* [ ] Parsing d'un e-mail
* [ ] Détection de quelques règles simples
* [ ] Système de score minimal
* [ ] Notification Telegram
* [ ] Fonctionnement en ligne de commande

## v0.2 — Moteur d'analyse

Objectif : construire le cœur de détection.

* [ ] Analyse des en-têtes
* [ ] Analyse des liens
* [ ] Analyse des pièces jointes
* [ ] Analyse du contenu
* [ ] Système de scoring complet
* [ ] SQLite
* [ ] Historique des messages analysés
* [ ] Tests automatisés plus complets

## v0.3 — Application graphique

Objectif : rendre Sentinelle utilisable par le grand public.

* [ ] Assistant de première configuration
* [ ] Interface graphique
* [ ] Icône de zone de notification
* [ ] Réglages
* [ ] Réglage de sensibilité
* [ ] Pause du système
* [ ] Tableau de bord local

## v0.4 — Réputation et amélioration

Objectif : améliorer la capacité de détection.

* [ ] Vérification de réputation des URLs
* [ ] Vérification de réputation des domaines
* [ ] Détection de l'âge des domaines
* [ ] Intégration de sources de réputation
* [ ] Retours utilisateur « c'était légitime »
* [ ] Amélioration progressive du scoring

## v1.0 — Première version distribuable

Objectif : disposer d'une application réellement utilisable.

* [ ] Exécutable Windows
* [ ] Support macOS
* [ ] Démarrage automatique
* [ ] Documentation utilisateur
* [ ] Guide pour l'aidant
* [ ] Guide pour la personne protégée
* [ ] Tests sur des cas réels anonymisés
* [ ] Vérification complète des mécanismes de sécurité

---

# 🚀 Évolutions futures

La première version est volontairement limitée au courrier électronique. Plusieurs pistes pourront être explorées ensuite.

## 🔑 OAuth

Remplacer progressivement les mots de passe d'application par des mécanismes OAuth lorsque les fournisseurs de messagerie le permettent.

L'objectif est de limiter encore davantage la manipulation d'identifiants sensibles.

## 📱 Analyse des SMS

Étendre le concept de Sentinelle aux SMS afin de détecter certaines campagnes de phishing envoyées directement sur téléphone.

## ☎️ Protection contre les appels

Étudier un système permettant d'identifier certains numéros signalés ou de gérer une liste blanche.

## 🗃️ Quarantaine optionnelle

Une version future pourrait proposer un mode plus actif avec déplacement ou mise en quarantaine de certains messages.

Cette fonctionnalité ne fait pas partie de la première version, qui reste volontairement en lecture seule.

## 📱 Version mobile

Une application mobile pourrait éventuellement reprendre le concept de Sentinelle sur smartphone.

Cette évolution nécessiterait probablement une architecture différente du client desktop actuel, notamment pour accéder aux SMS et aux appels selon les possibilités offertes par chaque système.

## 🧠 Amélioration du moteur de détection

À terme, le moteur de règles pourrait être complété par d'autres techniques d'analyse.

L'objectif resterait toutefois de conserver une détection **compréhensible et explicable**, plutôt que de produire uniquement une probabilité incompréhensible pour l'utilisateur.

---

# 👥 Parcours utilisateur prévu

## Première installation

```text
Installation
    ↓
Bienvenue
    ↓
Choix du fournisseur mail
    ↓
Configuration de la connexion
    ↓
Configuration des alertes
    ↓
Choix de la sensibilité
    ↓
Test
    ↓
Sentinelle fonctionne en arrière-plan
```

## Utilisation quotidienne

```text
Nouveau mail
     ↓
Analyse automatique
     ↓
Score
     ↓
┌───────────────────────┐
│ Risque faible         │
│ → aucune action       │
└───────────────────────┘

ou

┌───────────────────────┐
│ Risque élevé          │
│ → alerte à l'aidant   │
└───────────────────────┘
```

La personne protégée n'a normalement rien à faire.

---

# ⚠️ Limites

Sentinelle ne peut pas garantir qu'un message est légitime ou frauduleux.

Un système basé sur des règles peut :

* produire des faux positifs ;
* ne pas détecter certaines attaques ;
* être trompé par de nouvelles techniques de phishing ;
* dépendre de la qualité des informations disponibles.

Le score doit donc être considéré comme **un indicateur de risque**, et non comme une vérité absolue.

L'objectif de Sentinelle est d'aider un proche à intervenir plus rapidement lorsqu'un message mérite une attention particulière.

---

# 🆘 En cas d'arnaque

Sentinelle ne remplace pas les procédures de sécurité habituelles.

En cas d'arnaque avérée, les démarches appropriées peuvent notamment inclure :

* contacter rapidement sa banque lorsqu'une opération financière est concernée ;
* signaler le message ;
* utiliser les services officiels d'aide et de signalement ;
* conserver les éléments utiles à un éventuel signalement ou dépôt de plainte.

En France, le projet prévoit notamment de rappeler les ressources comme :

* [Cybermalveillance.gouv.fr](https://www.cybermalveillance.gouv.fr/)
* [17Cyber](https://17cyber.gouv.fr/)
* [Signal Spam](https://www.signal-spam.fr/)

---

# 📚 Documentation

La documentation utilisateur sera progressivement séparée en deux guides :

```text
docs/
├── guide_aidant.md
└── guide_personne_protegee.md
```

Le **guide aidant** expliquera l'installation, la configuration, les alertes et le fonctionnement général.

Le **guide personne protégée** présentera le logiciel avec un vocabulaire simple et rassurant.

---

# 🔓 Licence

Sentinelle est distribué sous licence **MIT**.

Voir le fichier [LICENSE](LICENSE) pour le texte complet de la licence.

---

# 🤝 Contribution

Le projet étant en développement, l'architecture et certaines fonctionnalités sont susceptibles d'évoluer.

Les contributions, idées, rapports de bugs et suggestions d'amélioration sont les bienvenus.

Les contributions doivent notamment respecter les principes du projet :

* confidentialité des données ;
* sécurité par défaut ;
* architecture modulaire ;
* fonctionnement compréhensible ;
* explicabilité des alertes ;
* absence de collecte inutile de données personnelles.

---

# 🛡️ Philosophie du projet

Sentinelle repose sur une idée simple :

> **La sécurité informatique ne devrait pas demander à tout le monde d'être expert en sécurité informatique.**

L'objectif est de créer une protection discrète, compréhensible et respectueuse de la vie privée, capable d'aider un proche à intervenir avant qu'une personne vulnérable ne tombe dans un piège.

**Sentinelle observe. Sentinelle explique. Sentinelle alerte.**
