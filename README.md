# DataYoti Analytics

Environnement d'analyse et de Business Intelligence pour le projet DataYoti.

## Architecture

- **Environment** : OLAP (Online Analytical Processing)
- **Base de données** : PostgreSQL (Data Mart)
- **Modélisation** : Star Schema / Snowflake Schema
- **Visualisation** : Grafana Analytics

## Séparation des environnements

```
datayoti-esp32-firmware/     # Sources de données (IoT)
datayoti-mqtt-broker/        # Environnement OLTP (opérationnel)
datayoti-analytics/          # Environnement OLAP (analytique) ← VOUS ÊTES ICI
```

## Installation

### Prérequis

- Docker et Docker Compose
- Environnement `datayoti-mqtt-broker` déjà en fonctionnement

### Configuration

1. **Créez votre fichier `.env`** :
   ```bash
   cp .env.example .env
   ```

2. **Modifiez les variables d'environnement** :
   - Changez tous les mots de passe
   - Adaptez les ports si nécessaire
   - Configurez la connexion vers l'environnement OLTP

### Démarrage

```bash
docker-compose up -d
```

## Accès

- **PostgreSQL Data Mart** : `localhost:5433`
- **Grafana Analytics** : http://localhost:3001

## Développement

### Modélisation dimensionnelle

1. **Analyser les besoins métier**
2. **Identifier les processus d'affaires**
3. **Concevoir les dimensions et les faits**
4. **Implémenter le Star Schema**

### Flux de données

```
[OLTP TimescaleDB] → [ETL/ELT] → [OLAP PostgreSQL] → [BI Tools]
```

## Structure du projet

```
datayoti-analytics/
├── docker-compose.yml          # Infrastructure OLAP
├── .env.example               # Variables d'environnement
├── datamart/                  # Base PostgreSQL Data Mart
│   └── init/                  # Scripts d'initialisation
└── README.md                  # Cette documentation
```

## Prochaines étapes

1. **Modélisation** : Concevoir votre Star Schema
2. **ETL** : Développer les pipelines de transformation
3. **Visualisation** : Créer les dashboards analytiques

---

**Note** : Cet environnement est totalement séparé de l'environnement opérationnel pour respecter les bonnes pratiques OLTP/OLAP.