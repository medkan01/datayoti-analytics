# DataYoti Analytics

Environnement d'analyse et de Business Intelligence pour le projet DataYoti, utilisant une architecture moderne ELT avec Apache Airflow et dbt.

## 🏗️ Architecture

- **Environnement** : OLAP (Online Analytical Processing)
- **Base de données** : PostgreSQL 16 (Data Mart)
- **Orchestration** : Apache Airflow 3.1.0 avec CeleryExecutor
- **Transformation** : dbt (Data Build Tool)
- **Modélisation** : Star Schema avec approche Kimball
- **Visualisation** : Grafana Analytics
- **Cache** : Redis pour Airflow Celery

## 🔄 Séparation des environnements

```
datayoti-esp32-firmware/     # Sources de données (IoT)
    ├── Capteurs IoT
    └── Firmware ESP32
datayoti-mqtt-broker/        # Environnement OLTP (opérationnel)
    ├── TimescaleDB
    └── MQTT Broker
datayoti-analytics/          # Environnement OLAP (analytique) ← VOUS ÊTES ICI
    ├── PostgreSQL Data Mart
    ├── Apache Airflow
    └── dbt Core
```

## 🚀 Installation

### Prérequis

- Docker et Docker Compose
- Au moins 4GB de RAM disponible
- Au moins 2 CPUs
- Environnement `datayoti-mqtt-broker` déjà en fonctionnement

### Configuration

1. **Créez votre fichier `.env`** :
   ```bash
   cp .env.example .env
   ```

2. **Modifiez les variables d'environnement** dans `.env` :
   ```bash
   # Base de données Data Mart
   DM_PG_USER=datamart_admin
   DM_PG_PASSWORD=VotreMotDePasse_DataMart_2024!
   DM_PG_DATABASE=datayoti_datamart
   DM_PG_PORT=5433

   # Connexion vers l'environnement OLTP
   OLTP_PG_HOST=localhost
   OLTP_PG_PORT=5432
   OLTP_PG_USER=mqtt_ingestor
   OLTP_PG_PASSWORD=VotreMotDePasse_OLTP_2024!
   OLTP_PG_DATABASE=datayoti_db
   ```

3. **Configurez les connexions Airflow** :
   - Connexion `oltp_connection` : Base source (TimescaleDB)
   - Connexion `olap_connection` : Base cible (PostgreSQL Data Mart)

### Démarrage

```bash
# Démarrer l'infrastructure complète
docker-compose up -d

# Vérifier le statut des services
docker-compose ps

# Suivre les logs
docker-compose logs -f
```

## 🌐 Accès aux interfaces

- **Apache Airflow** : http://localhost:8080
  - Utilisateur : `airflow`
  - Mot de passe : `airflow`
- **PostgreSQL Data Mart** : `localhost:5433`
- **Flower (Monitoring Celery)** : http://localhost:5555 (optionnel)

## 📊 Pipeline de données (ELT)

### 1. Extraction et Chargement (Airflow)

Les DAGs Airflow orchestrent l'ingestion des données depuis l'environnement OLTP :

#### DAG `ingest_raw_iot_data`
- **Fréquence** : Quotidienne
- **Fonction** : Ingestion incrémentale des données brutes
- **Tables sources** :
  - `sites` → `raw.raw_sites`
  - `devices` → `raw.raw_devices`
  - `device_heartbeats` → `raw.raw_device_heartbeats`
  - `sensor_data` → `raw.raw_sensor_data`

#### Autres DAGs
- `dim_reference_iot` : Construction des dimensions de référence
- `daily_facts_sensor` : Agrégation des faits quotidiens
- `dbt_housekeeping` : Maintenance et nettoyage
- `clear_tables` : Utilitaires de gestion

### 2. Transformation (dbt)

Architecture dbt en couches selon les meilleures pratiques :

```
datayoti_dbt/
├── models/
│   ├── raw/           # Données brutes (sources)
│   ├── staging/       # Nettoyage et standardisation
│   │   ├── stg_sites.sql
│   │   ├── stg_devices.sql
│   │   ├── stg_device_heartbeats.sql
│   │   ├── stg_sensor_data.sql
│   │   └── stg_conformity_rules.sql
│   ├── intermediate/  # Logique métier intermédiaire
│   └── marts/         # Modèles dimensionnels finaux
│       ├── dim_sites.sql
│       ├── dim_devices.sql
│       ├── dim_dates.sql
│       ├── dim_conformity_rules.sql
│       ├── fct_daily_sensor_reading.sql
│       ├── fct_daily_sensor_health.sql
│       ├── fct_daily_site_compliance.sql
│       └── vw_daily_site_compliance_summary.sql
```

### 3. Modèle dimensionnel (Star Schema)

#### Dimensions
- **`dim_sites`** : Sites IoT avec métadonnées
- **`dim_devices`** : Appareils IoT et caractéristiques
- **`dim_dates`** : Dimension temporelle
- **`dim_conformity_rules`** : Règles de conformité métier

#### Faits
- **`fct_daily_sensor_reading`** : Lectures quotidiennes des capteurs
- **`fct_daily_sensor_health`** : Santé quotidienne des capteurs
- **`fct_daily_site_compliance`** : Conformité quotidienne des sites

#### Vues métier
- **`vw_daily_site_compliance_summary`** : Tableau de bord de conformité

## 🛠️ Développement

### Commandes dbt utiles

```bash
# Accéder au conteneur Airflow
docker-compose exec airflow-scheduler bash

# Naviguer vers le projet dbt
cd /opt/airflow/datayoti_dbt

# Tester les connexions
dbt debug

# Compiler les modèles
dbt compile

# Exécuter tous les modèles
dbt run

# Exécuter les tests
dbt test

# Générer la documentation
dbt docs generate
dbt docs serve
```

### Airflow CLI

```bash
# Lister les DAGs
docker-compose exec airflow-scheduler airflow dags list

# Déclencher un DAG manuellement
docker-compose exec airflow-scheduler airflow dags trigger ingest_raw_iot_data

# Voir les tâches d'un DAG
docker-compose exec airflow-scheduler airflow tasks list ingest_raw_iot_data
```

## 📁 Structure complète du projet

```
datayoti-analytics/
├── .env.example                    # Template variables d'environnement
├── .gitignore                      # Exclusions Git optimisées
├── docker-compose.yml              # Infrastructure complète
├── README.md                       # Cette documentation
├── airflow/                        # Configuration Apache Airflow
│   ├── config/
│   │   └── airflow.cfg            # Configuration Airflow
│   ├── dags/                      # Pipelines d'orchestration
│   │   ├── ingest_raw_iot_data.py # Ingestion données IoT
│   │   ├── dim_reference_iot.py   # Construction dimensions
│   │   ├── daily_facts_sensor.py  # Agrégation faits
│   │   ├── dbt_housekeeping.py    # Maintenance dbt
│   │   ├── clear_tables.py        # Utilitaires
│   │   └── utils/                 # Fonctions communes
│   ├── logs/                      # Logs Airflow
│   └── plugins/                   # Plugins personnalisés
└── datayoti_dbt/                  # Projet dbt
    ├── dbt_project.yml            # Configuration projet
    ├── profiles/
    │   └── profiles.yml           # Connexions bases de données
    ├── models/                    # Modèles de transformation
    │   ├── raw/                   # Sources de données
    │   ├── staging/               # Couche de nettoyage
    │   ├── intermediate/          # Logique métier
    │   └── marts/                 # Modèles dimensionnels
    ├── macros/                    # Macros dbt réutilisables
    ├── tests/                     # Tests de qualité données
    ├── seeds/                     # Données de référence
    └── snapshots/                 # Historisation SCD
```

## 🔧 Services Docker

| Service | Description | Port | Santé |
|---------|-------------|------|--------|
| `postgres` | Base Airflow | - | pg_isready |
| `redis` | Cache Celery | 6379 | redis-cli ping |
| `airflow-apiserver` | API Airflow | 8080 | curl /api/v2/version |
| `airflow-scheduler` | Ordonnanceur | - | curl /health |
| `airflow-dag-processor` | Processeur DAGs | - | jobs check |
| `airflow-worker` | Worker Celery | - | celery inspect ping |
| `airflow-triggerer` | Déclencheur | - | jobs check |
| `datamart-db` | PostgreSQL Data Mart | 5433 | - |

## 📈 Métriques et monitoring

### Métriques IoT disponibles
- **Température** : Min/Max/Moyenne par site et période
- **Humidité** : Min/Max/Moyenne par site et période
- **Uptime** : Ratio de disponibilité des capteurs
- **Conformité** : Respect des règles métier par site
- **Santé système** : Heartbeats et diagnostics

### Règles de conformité
- **Plage température** : Vérification des seuils min/max
- **Seuil humidité** : Plancher et plafond d'humidité
- **Stabilité température** : Variation maximale autorisée
- **Taux uptime** : Disponibilité minimale requise
- **Validité données** : Pourcentage de données valides

## 🚨 Troubleshooting

### Problèmes courants

1. **Erreur de connexion dbt** :
   ```bash
   # Vérifier la configuration des profils
   cat datayoti_dbt/profiles/profiles.yml
   ```

2. **DAGs non visibles** :
   ```bash
   # Vérifier les logs du dag-processor
   docker-compose logs airflow-dag-processor
   ```

3. **Problèmes de permissions** :
   ```bash
   # Redémarrer l'initialisation
   docker-compose up airflow-init
   ```

### Logs utiles

```bash
# Logs Airflow complets
docker-compose logs -f airflow-scheduler

# Logs d'un DAG spécifique
docker-compose exec airflow-scheduler airflow tasks log ingest_raw_iot_data bootstrap_raw_schema

# Logs PostgreSQL Data Mart
docker-compose logs datamart-db
```

## 🔐 Sécurité

- Tous les mots de passe doivent être changés en production
- Les connexions entre services utilisent des réseaux Docker isolés
- Les volumes persistent les données en cas de redémarrage
- Fichier `.env` exclu du contrôle de version

## 🚀 Prochaines étapes

1. **✅ Infrastructure** : Airflow + dbt + PostgreSQL opérationnels
2. **✅ Ingestion** : Pipelines d'extraction depuis OLTP
3. **✅ Transformation** : Modèles dbt en couches
4. **🔄 En cours** : Tableaux de bord Grafana
5. **📋 À venir** : Tests de qualité étendus
6. **📋 À venir** : Alerting et monitoring avancé
7. **📋 À venir** : Documentation dbt automatisée

---

**Note** : Cet environnement respecte les bonnes pratiques moderne d'architecture analytique avec séparation OLTP/OLAP, orchestration déclarative et transformation en code.