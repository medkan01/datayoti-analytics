# 📊 DataYoti Analytics

> Plateforme d'analyse et de Business Intelligence pour le monitoring environnemental IoT

**DataYoti Analytics** est une solution complète d'entreposage de données (Data Warehouse) et d'analyse pour les systèmes IoT de monitoring environnemental (température, humidité). Le projet implémente une architecture moderne **ELT** (Extract-Load-Transform) avec orchestration déclarative et transformations testées.

---

## � Objectif du projet

Fournir une plateforme analytique robuste permettant de :

- 📈 **Analyser** les tendances environnementales (température, humidité) sur des périodes étendues
- 🔍 **Surveiller** la santé et la disponibilité des capteurs IoT déployés
- ✅ **Vérifier** la conformité des conditions environnementales par rapport aux règles métier
- 📊 **Agréger** les métriques par site, par appareil et par période
- 🏢 **Historiser** les changements de configuration (SCD Type 2)
- 📉 **Produire** des rapports de conformité et tableaux de bord décisionnels

---

## 🏗️ Architecture technique

### Stack technologique

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **Orchestration** | Apache Airflow | 3.1.0 | Orchestration des pipelines ELT |
| **Transformation** | dbt (Data Build Tool) | Latest | Transformations SQL modulaires et testables |
| **Data Warehouse** | PostgreSQL | 16 | Stockage OLAP avec schémas dimensionnels |
| **Task Queue** | Celery + Redis | Latest | Exécution distribuée des tâches Airflow |
| **Conteneurisation** | Docker Compose | Latest | Infrastructure as Code |

### Architecture ELT

```
┌─────────────────────┐
│   OLTP Source       │
│  (TimescaleDB)      │
│  - Sites            │
│  - Devices          │
│  - Sensor Data      │
│  - Heartbeats       │
└──────────┬──────────┘
           │ Extract & Load (Airflow)
           │ Ingestion incrémentale
           ↓
┌─────────────────────┐
│   Raw Layer         │
│  (PostgreSQL)       │
│  - raw_sites        │
│  - raw_devices      │
│  - raw_sensor_data  │
│  - raw_heartbeats   │
└──────────┬──────────┘
           │ Transform (dbt)
           │ Staging → Intermediate → Marts
           ↓
┌─────────────────────┐
│  Data Warehouse     │
│  (Star Schema)      │
│                     │
│  Dimensions:        │
│  - dim_sites        │
│  - dim_devices      │
│  - dim_dates        │
│  - dim_conformity   │
│                     │
│  Facts:             │
│  - fct_sensor_read  │
│  - fct_sensor_health│
│  - fct_compliance   │
└─────────────────────┘
           │
           ↓
┌─────────────────────┐
│  Business Views     │
│  - Compliance       │
│  - KPIs             │
│  - Dashboards       │
└─────────────────────┘
```

### Séparation des environnements

Le projet fait partie d'un écosystème complet :

```
📡 datayoti-esp32-firmware/      # Firmware IoT (ESP32 + capteurs DHT22)
    └── Collecte des données en temps réel

💾 datayoti-mqtt-broker/         # Environnement OLTP opérationnel
    ├── MQTT Broker (ingestion)
    └── TimescaleDB (stockage transactionnel)

📊 datayoti-analytics/           # Environnement OLAP analytique ← CE PROJET
    ├── Apache Airflow (orchestration)
    ├── dbt (transformations)
    └── PostgreSQL (Data Warehouse)
```

---

## 📐 Modèle de données

### Approche dimensionnelle (Star Schema)

Le Data Warehouse implémente une **modélisation en étoile** selon la méthodologie Kimball :

#### 🌟 Tables de dimensions

| Dimension | Description | Type | Grain |
|-----------|-------------|------|-------|
| **dim_sites** | Sites de déploiement des capteurs | SCD2 | 1 ligne par version de site |
| **dim_devices** | Appareils IoT (ESP32 + DHT22) | SCD2 | 1 ligne par version d'appareil |
| **dim_dates** | Calendrier (1990-2050) | Static | 1 ligne par jour |
| **dim_conformity_rules** | Règles de conformité métier | SCD2 | 1 ligne par version de règle |

**SCD Type 2** : Historisation complète des changements avec colonnes `valid_from_ts`, `valid_to_ts`, `is_current`

#### 📊 Tables de faits

| Fait | Grain | Métriques | Fréquence |
|------|-------|-----------|-----------|
| **fct_daily_sensor_reading** | 1 ligne par capteur par jour | Temp (min/max/avg), Humidity (min/max/avg) | Quotidien |
| **fct_daily_sensor_health** | 1 ligne par capteur par jour | RSSI, Heap, Uptime, NTP sync | Quotidien |
| **fct_daily_site_compliance** | 1 ligne par règle par site par jour | Conformité (booléen), métriques calculées | Quotidien |

#### 📈 Vues métier

- **vw_daily_site_compliance_summary** : Taux de conformité global et violations critiques par site

### Hiérarchies analytiques

```
Site
 └── Device (n:1)
      └── Sensor Reading (n:1)
      └── Sensor Health (n:1)

Site + Date
 └── Compliance Metrics (n:1)
      └── Rule Evaluation (n:n)
```

---

## 🚀 Démarrage rapide

### Prérequis

- **Docker** et **Docker Compose** installés
- **4 GB RAM** minimum disponible
- **2 CPUs** minimum
- Environnement **datayoti-mqtt-broker** en fonctionnement (source OLTP)

### Installation en 3 étapes

#### 1️⃣ Configuration de l'environnement

```bash
# Cloner le projet
git clone https://github.com/medkan01/datayoti-analytics.git
cd datayoti-analytics

# Créer le fichier .env depuis le template
cp .env.example .env

# Éditer les variables d'environnement
nano .env  # ou votre éditeur préféré
```

**Variables essentielles à configurer :**

```bash
# Base de données Data Warehouse (OLAP)
DM_PG_USER=datamart_admin
DM_PG_PASSWORD=VotreMotDePasseSecurise123!
DM_PG_DATABASE=datayoti_datamart
DM_PG_PORT=5433

# Connexion vers la source OLTP (TimescaleDB)
OLTP_PG_HOST=192.168.x.x  # IP de votre broker MQTT
OLTP_PG_PORT=5432
OLTP_PG_USER=mqtt_ingestor
OLTP_PG_PASSWORD=MotDePasseOLTP123!
OLTP_PG_DATABASE=datayoti_db

# Airflow
AIRFLOW_UID=50000
AIRFLOW__CORE__FERNET_KEY=<générer avec: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
```

#### 2️⃣ Démarrage de l'infrastructure

```bash
# Initialiser et démarrer tous les services
docker-compose up -d

# Vérifier l'état des services
docker-compose ps

# Attendre l'initialisation complète (~2 minutes)
docker-compose logs -f airflow-init
```

#### 3️⃣ Configuration d'Airflow

1. Accéder à l'interface Airflow : **http://localhost:8080**
   - Username : `airflow`
   - Password : `airflow`

2. Configurer les connexions (Admin → Connections) :

**Connexion OLTP (source)** :
```
Connection Id: oltp_connection
Connection Type: Postgres
Host: <OLTP_PG_HOST>
Schema: <OLTP_PG_DATABASE>
Login: <OLTP_PG_USER>
Password: <OLTP_PG_PASSWORD>
Port: <OLTP_PG_PORT>
```

**Connexion OLAP (destination)** :
```
Connection Id: olap_connection
Connection Type: Postgres
Host: datamart-db
Schema: public
Login: <DM_PG_USER>
Password: <DM_PG_PASSWORD>
Port: 5432
```

3. Activer les DAGs souhaités et déclencher `ingest_raw_iot_data`

---

## 📋 Pipelines de données

### DAGs Airflow

| DAG | Fréquence | Description | Dépendances |
|-----|-----------|-------------|-------------|
| **ingest_raw_iot_data** | @daily | Ingestion incrémentale depuis OLTP vers raw layer | Connexion OLTP |
| **dim_reference_iot** | @daily | Construction/mise à jour des dimensions | ingest_raw_iot_data |
| **daily_facts_sensor** | @daily | Agrégation des faits quotidiens | dim_reference_iot |
| **dbt_housekeeping** | @weekly | Maintenance et optimisation dbt | - |
| **clear_tables** | Manual | Réinitialisation complète (développement) | - |

### Architecture dbt (4 couches)

```
📁 models/
│
├── 📂 raw/                    # Couche 1: Tables brutes (DDL uniquement)
│   ├── raw_sites.sql          # Structure vide pour ingestion Airflow
│   ├── raw_devices.sql
│   ├── raw_sensor_data.sql
│   └── raw_device_heartbeats.sql
│
├── 📂 staging/                # Couche 2: Nettoyage et standardisation
│   ├── stg_sites.sql          # Conversion types, validation, nettoyage
│   ├── stg_devices.sql        # Format MAC addresses, timestamps
│   ├── stg_sensor_data.sql    # Validation plages température/humidité
│   ├── stg_device_heartbeats.sql
│   └── stg_conformity_rules.sql
│
├── 📂 intermediate/           # Couche 3: Logique métier
│   ├── int_sites_scd2.sql     # Implémentation SCD2 via snapshots
│   ├── int_devices_scd2.sql
│   ├── int_conformity_rules_scd2.sql
│   ├── int_daily_sensor_reading.sql    # Agrégations quotidiennes
│   ├── int_daily_sensor_health.sql
│   └── int_daily_site_env.sql          # Métriques environnementales
│
└── 📂 marts/                  # Couche 4: Modèle dimensionnel
    ├── 🌟 Dimensions
    │   ├── dim_sites.sql
    │   ├── dim_devices.sql
    │   ├── dim_dates.sql
    │   └── dim_conformity_rules.sql
    │
    ├── 📊 Facts
    │   ├── fct_daily_sensor_reading.sql
    │   ├── fct_daily_sensor_health.sql
    │   └── fct_daily_site_compliance.sql
    │
    └── 📈 Views
        └── vw_daily_site_compliance_summary.sql
```

### Exemple de requête analytique

```sql
-- Taux de conformité mensuel par site
SELECT 
    s.site_name,
    d.year_number,
    d.month_name,
    ROUND(AVG(c.compliance_rate) * 100, 2) AS avg_compliance_pct,
    SUM(c.nb_critical_violations) AS total_critical_violations
FROM vw_daily_site_compliance_summary c
JOIN dim_sites s ON c.site_sk = s.site_sk AND s.is_current = TRUE
JOIN dim_dates d ON c.event_day_sk = d.date_sk
WHERE d.year_number = 2025
GROUP BY s.site_name, d.year_number, d.month_name
ORDER BY d.year_number, d.month_number, s.site_name;
```

---

## 🛠️ Développement et maintenance

### Commandes dbt

Toutes les commandes dbt s'exécutent dans le conteneur Airflow :

```bash
# Accéder au conteneur
docker-compose exec airflow-scheduler bash

# Naviguer vers le projet dbt
cd /opt/airflow/datayoti_dbt

# Tester la connexion
dbt debug

# Compiler les modèles (génère SQL dans target/)
dbt compile

# Exécuter tous les modèles
dbt run

# Exécuter un modèle spécifique
dbt run --select dim_sites

# Exécuter une couche
dbt run --select staging.*
dbt run --select marts.*

# Exécuter avec dépendances
dbt run --select +fct_daily_sensor_reading  # inclut upstream
dbt run --select fct_daily_sensor_reading+  # inclut downstream

# Tests de qualité
dbt test                           # Tous les tests
dbt test --select staging.*        # Tests sur staging
dbt test --select dim_sites        # Tests sur un modèle

# Générer et servir la documentation
dbt docs generate
dbt docs serve --port 8081

# Snapshots (historisation SCD2)
dbt snapshot

# Charger les seeds (données de référence)
dbt seed
```

### Commandes Airflow

```bash
# Lister les DAGs
docker-compose exec airflow-scheduler airflow dags list

# Déclencher un DAG manuellement
docker-compose exec airflow-scheduler airflow dags trigger ingest_raw_iot_data

# Voir les tâches d'un DAG
docker-compose exec airflow-scheduler airflow tasks list ingest_raw_iot_data

# Afficher le statut d'une exécution
docker-compose exec airflow-scheduler airflow dags list-runs -d ingest_raw_iot_data

# Tester une tâche spécifique
docker-compose exec airflow-scheduler airflow tasks test ingest_raw_iot_data bootstrap_raw_schema 2025-11-03

# Pause/unpause un DAG
docker-compose exec airflow-scheduler airflow dags pause ingest_raw_iot_data
docker-compose exec airflow-scheduler airflow dags unpause ingest_raw_iot_data
```

### Gestion des logs

```bash
# Logs en temps réel d'un service
docker-compose logs -f airflow-scheduler
docker-compose logs -f datamart-db

# Logs d'une tâche Airflow spécifique
docker-compose exec airflow-scheduler airflow tasks logs ingest_raw_iot_data bootstrap_raw_schema 2025-11-03

# Logs dbt (dans le conteneur)
cd /opt/airflow/datayoti_dbt
cat logs/dbt.log
```

---

## 📊 Métriques et analyses disponibles

### Métriques environnementales

- **Température** :
  - Moyenne, minimum, maximum par site/appareil/jour
  - Plage de variation (température_range)
  - Stabilité thermique (écart min-max)

- **Humidité** :
  - Moyenne, minimum, maximum par site/appareil/jour
  - Plage de variation (humidity_range)
  - Respect des seuils plancher/plafond

### Métriques de santé IoT

- **Connectivité** :
  - RSSI (Received Signal Strength Indicator)
  - Taux de disponibilité (uptime_ratio)
  - Synchronisation NTP

- **Performance système** :
  - Mémoire heap libre (free_heap)
  - Mémoire heap minimale (min_heap)
  - Temps de fonctionnement (uptime)

### Conformité métier

Les règles de conformité sont définies dans `seeds/conformity_rules.csv` :

| Type de métrique | Description | Exemple de règle |
|------------------|-------------|------------------|
| **temperature_range** | Plage température acceptable | 18°C - 24°C |
| **humidity_ceiling** | Seuil maximum humidité | ≤ 60% |
| **humidity_floor** | Seuil minimum humidité | ≥ 35% |
| **temperature_stability** | Variation maximale autorisée | ≤ 3°C |
| **uptime_ratio** | Disponibilité minimale | ≥ 95% |
| **data_validity** | Taux de données valides | ≥ 90% |

Chaque règle est associée à un **niveau de criticité** (LOW, MEDIUM, HIGH) pour prioriser les alertes.

---

## 🔍 Accès aux interfaces

| Interface | URL | Credentials | Description |
|-----------|-----|-------------|-------------|
| **Airflow Web UI** | http://localhost:8080 | airflow / airflow | Monitoring des DAGs et pipelines |
| **Flower (Celery)** | http://localhost:5555 | - | Monitoring des workers Celery |
| **PostgreSQL DataMart** | localhost:5433 | `DM_PG_USER` / `DM_PG_PASSWORD` | Connexion directe au DWH |
| **dbt Docs** | http://localhost:8081 | - | Documentation générée (si `dbt docs serve` actif) |

### Connexion au Data Warehouse

```bash
# Via psql
psql -h localhost -p 5433 -U datamart_admin -d datayoti_datamart

# Via DBeaver, pgAdmin, DataGrip, etc.
Host: localhost
Port: 5433
Database: datayoti_datamart
User: datamart_admin
Password: <DM_PG_PASSWORD>
```

---

## 📁 Structure du projet

```
datayoti-analytics/
│
├── 📄 .env.example                 # Template de configuration
├── 📄 .gitignore                   # Exclusions Git
├── 📄 docker-compose.yml           # Infrastructure complète
├── 📄 README.md                    # Cette documentation
│
├── 📂 airflow/                     # Apache Airflow
│   ├── 📂 config/
│   │   └── airflow.cfg             # Configuration Airflow
│   │
│   ├── 📂 dags/                    # Pipelines d'orchestration
│   │   ├── ingest_raw_iot_data.py  # Ingestion OLTP → Raw
│   │   ├── dim_reference_iot.py    # Construction dimensions
│   │   ├── daily_facts_sensor.py   # Agrégation quotidienne
│   │   ├── dbt_housekeeping.py     # Maintenance dbt
│   │   ├── clear_tables.py         # Utilitaires reset
│   │   └── utils/                  # Fonctions partagées
│   │
│   ├── 📂 logs/                    # Logs Airflow (ignorés par git)
│   └── 📂 plugins/                 # Plugins Airflow personnalisés
│
└── 📂 datayoti_dbt/                # Projet dbt
    │
    ├── 📄 dbt_project.yml          # Configuration projet
    ├── 📄 packages.yml             # Dépendances (dbt_utils, dbt_date)
    │
    ├── 📂 profiles/
    │   └── profiles.yml            # Connexion PostgreSQL
    │
    ├── 📂 models/                  # Modèles de transformation
    │   ├── 📂 raw/                 # DDL tables brutes
    │   │   ├── _raw.yml            # Documentation
    │   │   └── *.sql               # 4 modèles
    │   │
    │   ├── 📂 staging/             # Nettoyage et standardisation
    │   │   ├── _stg.yml            # Documentation + tests
    │   │   └── *.sql               # 5 modèles
    │   │
    │   ├── 📂 intermediate/        # Logique métier
    │   │   ├── _int.yml            # Documentation + tests
    │   │   └── *.sql               # 8 modèles
    │   │
    │   ├── 📂 marts/               # Star Schema final
    │   │   ├── _marts.yml          # Documentation + tests
    │   │   └── *.sql               # 8 modèles (4 dims + 3 facts + 1 view)
    │   │
    │   └── 📂 sources/
    │       └── raw_iot.yml         # Définition sources externes
    │
    ├── 📂 macros/                  # Macros SQL réutilisables
    │   ├── generate_schema_name.sql
    │   └── test_valid_mac_address.sql
    │
    ├── 📂 tests/                   # Tests personnalisés
    │   └── .gitkeep
    │
    ├── 📂 seeds/                   # Données de référence
    │   ├── _seeds.yml
    │   └── conformity_rules.csv    # Règles de conformité métier
    │
    ├── 📂 snapshots/               # Historisation SCD2
    │   ├── _snapshots.yml
    │   ├── sites_snapshot.sql
    │   ├── devices_snapshot.sql
    │   └── conformity_rules_snapshot.sql
    │
    ├── 📂 analyses/                # Analyses SQL ad-hoc
    │   └── .gitkeep
    │
    ├── 📂 target/                  # Artifacts compilés (ignoré par git)
    ├── 📂 logs/                    # Logs dbt (ignoré par git)
    └── 📂 dbt_packages/            # Packages installés (ignoré par git)
```

---

## 🚨 Dépannage

### Problèmes courants

#### ❌ Erreur : "Connection refused" sur OLTP

```bash
# Vérifier la connectivité réseau
ping <OLTP_PG_HOST>

# Vérifier que le service OLTP est accessible
docker ps  # sur la machine OLTP

# Tester la connexion PostgreSQL
psql -h <OLTP_PG_HOST> -p <OLTP_PG_PORT> -U <OLTP_PG_USER> -d <OLTP_PG_DATABASE>
```

**Solution** : Vérifier les variables `OLTP_PG_*` dans `.env` et les connexions Airflow

#### ❌ DAGs non visibles dans Airflow

```bash
# Vérifier les logs du dag-processor
docker-compose logs airflow-dag-processor

# Vérifier les erreurs de syntaxe Python
docker-compose exec airflow-scheduler python /opt/airflow/dags/<dag_file>.py
```

**Solution** : Corriger les erreurs de syntaxe, vérifier les imports

#### ❌ dbt : "Database Error" ou "Connection refused"

```bash
# Tester la configuration dbt
docker-compose exec airflow-scheduler bash
cd /opt/airflow/datayoti_dbt
dbt debug

# Vérifier le fichier profiles.yml
cat profiles/profiles.yml
```

**Solution** : 
- Vérifier que `host: datamart-db` (nom du service Docker)
- Vérifier `port: 5432` (port interne du conteneur)
- Vérifier les credentials dans profiles.yml

#### ❌ Erreurs de permissions Airflow

```bash
# Réinitialiser les permissions
docker-compose down
docker-compose up airflow-init
docker-compose up -d
```

#### ❌ Services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Vérifier les ressources système
docker stats

# Libérer de l'espace disque
docker system prune -a
```

### Commandes de diagnostic

```bash
# État complet de l'infrastructure
docker-compose ps

# Santé des services
docker-compose exec datamart-db pg_isready
docker-compose exec redis redis-cli ping

# Espace disque utilisé
docker system df

# Logs en temps réel (tous services)
docker-compose logs -f --tail=100
```

---

## 🔐 Sécurité et bonnes pratiques

### ⚠️ Important pour la production

1. **Changer TOUS les mots de passe** par défaut
2. **Régénérer** la clé Fernet Airflow :
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
3. **Ne JAMAIS commit** le fichier `.env` dans Git
4. **Utiliser des secrets managers** (AWS Secrets Manager, Vault, etc.)
5. **Activer SSL/TLS** pour les connexions PostgreSQL
6. **Restreindre l'accès réseau** aux ports exposés (firewall)
7. **Configurer des backups réguliers** du Data Warehouse
8. **Mettre à jour** régulièrement les images Docker

### Réseau Docker isolé

Tous les services communiquent via le réseau Docker `analytics-net`, isolé du réseau hôte.

### Persistance des données

Les volumes Docker assurent la persistance :
- `postgres-db-volume` : Base Airflow
- `datamart_data` : Data Warehouse PostgreSQL

---

## 📚 Ressources et références

### Documentation officielle

- **Apache Airflow** : https://airflow.apache.org/docs/
- **dbt** : https://docs.getdbt.com/
- **PostgreSQL** : https://www.postgresql.org/docs/
- **Docker Compose** : https://docs.docker.com/compose/

### Méthodologies

- **Kimball Dimensional Modeling** : Approche star schema
- **ELT vs ETL** : Load first, transform in database
- **SCD Type 2** : Historisation complète des changements
- **dbt best practices** : Layered transformations (staging → intermediate → marts)

### Dépendances dbt

- **dbt-utils** : Macros et tests génériques
- **dbt-date** : Génération de dimension calendrier

---

## 🗺️ Roadmap

### ✅ Fonctionnalités implémentées

- [x] Infrastructure Docker Compose complète
- [x] Orchestration Airflow avec CeleryExecutor
- [x] Ingestion incrémentale depuis OLTP
- [x] Modèle dimensionnel en étoile (4 dimensions, 3 faits)
- [x] Transformations dbt en 4 couches
- [x] Historisation SCD Type 2
- [x] Tests de qualité de données
- [x] Documentation inline complète
- [x] Métriques de conformité métier

### 🔄 En cours

- [ ] Tableaux de bord Grafana
- [ ] Alertes automatiques sur violations critiques
- [ ] Optimisation des performances (indexes, partitioning)

### 📋 À venir

- [ ] Tests de données étendus (dbt expectations)
- [ ] Documentation dbt déployée automatiquement
- [ ] CI/CD avec tests automatisés
- [ ] Monitoring avancé (Prometheus + Grafana)
- [ ] Data lineage visualization
- [ ] API REST pour accès programmatique
- [ ] Machine Learning pour prédictions

---

## 👨‍💻 Contribution

Ce projet est ouvert aux contributions. Pour proposer des améliorations :

1. Fork le repository
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

---

## 🙏 Remerciements

- **Apache Airflow** pour l'orchestration robuste
- **dbt Labs** pour le framework de transformation moderne
- **PostgreSQL Community** pour la base de données fiable
- **Kimball Group** pour la méthodologie dimensionnelle

---

**Projet DataYoti Analytics** - Une solution moderne de Data Warehouse pour l'IoT environnemental  
📧 Contact : [GitHub Issues](https://github.com/medkan01/datayoti-analytics/issues)