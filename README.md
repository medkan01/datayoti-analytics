# 📊 DataYoti Warehouse

> **Du signal à l'action** - Data Warehouse et Business Intelligence pour l'IoT environnemental

**DataYoti Warehouse** transforme les données IoT en insights actionnables. Cette solution complète de Data Warehouse implémente une architecture ELT moderne avec orchestration déclarative, permettant le monitoring qualité, la traçabilité et l'analyse de conformité des conditions environnementales.

## 🎯 Place dans l'écosystème DataYoti

```
┌─────────────────────────────────────────┐
│  1️⃣  Capteurs ESP32 (DHT22)            │  → datayoti-firmware
│      ↓ MQTT                             │
│  2️⃣  Infrastructure temps réel          │  → datayoti-realtime (Raspberry Pi)
│      ↓ Ingestion & monitoring (OLTP)    │
│  3️⃣  Data Warehouse + Analytics        │  ← VOUS ÊTES ICI
│      ↓ Dashboards & Conformité (OLAP)  │
│  4️⃣  Insights actionnables              │
└─────────────────────────────────────────┘
```

Ce composant assure :
- 📈 **Analyse** des tendances environnementales sur périodes étendues
- ✅ **Vérification** de la conformité par rapport aux règles métier
- 🏢 **Historisation** des changements de configuration (SCD Type 2)
- 📊 **Agrégation** des métriques par site, appareil et période
- 📉 **Production** de rapports de conformité décisionnels

---

## 🏗️ Architecture ELT

```
┌─────────────────────┐
│   OLTP Source       │  datayoti-realtime (Raspberry Pi)
│  (TimescaleDB)      │  (Données opérationnelles)
└──────────┬──────────┘
           │ Extract & Load (Airflow)
           ↓
┌─────────────────────┐
│   Raw Layer         │  Réplication des données
│  (PostgreSQL)       │  brutes pour analyse
└──────────┬──────────┘
           │ Transform (dbt)
           ↓
┌─────────────────────┐
│  Data Warehouse     │  Modèle dimensionnel
│  (Star Schema)      │  pour analytics
│  - 4 Dimensions     │
│  - 3 Faits          │
└─────────┬───────────┘
           │
           ↓
┌─────────────────────┐
│  Business Views     │  Insights actionnables
│  - Compliance       │  - Dashboards
│  - KPIs             │  - Alertes
└─────────────────────┘
```

### Stack technique

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Orchestration** | Apache Airflow 3.1.0 | Pipelines ELT automatisés |
| **Transformation** | dbt (Data Build Tool) | Transformations SQL testables |
| **Data Warehouse** | PostgreSQL 16 | Stockage OLAP dimensionnel |
| **Task Queue** | Celery + Redis | Exécution distribuée |
| **Infrastructure** | Docker Compose | Déploiement simplifié |


---

## 🌟 Fonctionnalités clés

### Monitoring et traçabilité

- 📊 **Référentiel** : Règles de conformité automatisées (température, humidité, stabilité, disponibilité)
- 📝 **Traçabilité** : Journal complet des non-conformités avec audit trail
- ⏱️ **Historisation** : SCD Type 2 pour suivi des changements dans le temps
- 🎯 **Priorisation** : Classement des risques par zone et niveau de criticité

### Modèle dimensionnel (Star Schema)

**Dimensions** :
- `dim_sites` : Sites de déploiement (SCD2)
- `dim_devices` : Appareils IoT ESP32 (SCD2)
- `dim_dates` : Calendrier analytique (1990-2050)
- `dim_conformity_rules` : Règles métier (SCD2)

**Faits** (grain quotidien) :
- `fct_daily_sensor_reading` : Métriques température/humidité
- `fct_daily_sensor_health` : Santé des capteurs (RSSI, uptime, heap)
- `fct_daily_site_compliance` : Conformité par site et par règle

### Pipeline dbt en 4 couches

1. **Raw** : Tables DDL pour ingestion Airflow
2. **Staging** : Nettoyage et standardisation
3. **Intermediate** : Logique métier et SCD2
4. **Marts** : Modèle dimensionnel final

---

## 🚀 Installation rapide

### Prérequis

- **Docker** et **Docker Compose** installés
- **4 GB RAM** minimum
- **2 CPUs** minimum
- Environnement **datayoti-realtime** en fonctionnement sur Raspberry Pi (source OLTP)

### Installation en 3 étapes

```bash
# 1. Cloner et configurer
git clone https://github.com/medkan01/datayoti-warehouse.git
cd datayoti-warehouse
cp .env.example .env
# Éditer .env avec vos paramètres

# 2. Démarrer l'infrastructure
docker-compose up -d

# 3. Attendre l'initialisation (~2 min)
docker-compose logs -f airflow-init
```

### Configuration minimale (.env)

```bash
# Data Warehouse (OLAP)
DM_PG_USER=datamart_admin
DM_PG_PASSWORD=VotreMotDePasseDW123!
DM_PG_DATABASE=datayoti_datamart
DM_PG_PORT=5433

# Source OLTP (datayoti-realtime sur Raspberry Pi)
OLTP_PG_HOST=192.168.x.x  # IP du Raspberry Pi
OLTP_PG_PORT=5432
OLTP_PG_USER=mqtt_ingestor
OLTP_PG_PASSWORD=MotDePasseOLTP123!
OLTP_PG_DATABASE=datayoti_db

# Airflow
AIRFLOW_UID=50000
AIRFLOW__CORE__FERNET_KEY=<générer avec commande ci-dessous>
```

**Générer la clé Fernet** :
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Configuration Airflow

1. Accéder à **http://localhost:8080** (airflow / airflow)
2. Configurer les connexions (Admin → Connections) :

**OLTP (source)** :
```
Connection Id: oltp_connection
Type: Postgres
Host: <OLTP_PG_HOST>
Database: <OLTP_PG_DATABASE>
Login: <OLTP_PG_USER>
Password: <OLTP_PG_PASSWORD>
Port: <OLTP_PG_PORT>
```

**OLAP (destination)** :
```
Connection Id: olap_connection
Type: Postgres
Host: datamart-db
Database: public
Login: <DM_PG_USER>
Password: <DM_PG_PASSWORD>
Port: 5432
```

3. Activer et déclencher le DAG `ingest_raw_iot_data`

---

## 📋 Pipelines de données

### DAGs Airflow

| DAG | Fréquence | Description |
|-----|-----------|-------------|
| `ingest_raw_iot_data` | @daily | Ingestion OLTP → Raw layer |
| `dim_reference_iot` | @daily | Construction dimensions |
| `daily_facts_sensor` | @daily | Agrégation faits quotidiens |
| `dbt_housekeeping` | @weekly | Maintenance dbt |

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

## 🛠️ Développement

### Commandes dbt

```bash
# Accéder au conteneur
docker-compose exec airflow-scheduler bash
cd /opt/airflow/datayoti_dbt

# Exécuter les transformations
dbt run                              # Tous les modèles
dbt run --select staging.*           # Couche staging uniquement
dbt run --select +fct_daily_sensor_reading  # Avec dépendances

# Tests de qualité
dbt test                             # Tous les tests
dbt test --select dim_sites          # Tests d'un modèle

# Documentation
dbt docs generate
dbt docs serve --port 8081

# Snapshots (SCD2)
dbt snapshot

# Seeds (données de référence)
dbt seed
```

### Commandes Airflow

```bash
# Lister les DAGs
docker-compose exec airflow-scheduler airflow dags list

# Déclencher manuellement
docker-compose exec airflow-scheduler airflow dags trigger ingest_raw_iot_data

# Voir les exécutions
docker-compose exec airflow-scheduler airflow dags list-runs -d ingest_raw_iot_data

# Tester une tâche
docker-compose exec airflow-scheduler airflow tasks test ingest_raw_iot_data bootstrap_raw_schema 2025-11-03
```

---

## 📊 Métriques de conformité

Les règles sont définies dans `datayoti_dbt/seeds/conformity_rules.csv` :

| Type de règle | Description | Exemple |
|---------------|-------------|---------|
| `temperature_range` | Plage acceptable | 18°C - 24°C |
| `humidity_ceiling` | Seuil maximum | ≤ 60% |
| `humidity_floor` | Seuil minimum | ≥ 35% |
| `temperature_stability` | Variation max | ≤ 3°C |
| `uptime_ratio` | Disponibilité min | ≥ 95% |

Chaque règle a un **niveau de criticité** (LOW, MEDIUM, HIGH) pour prioriser les alertes.

---

## 🔍 Interfaces disponibles

| Interface | URL | Credentials | Usage |
|-----------|-----|-------------|-------|
| **Airflow** | http://localhost:8080 | airflow / airflow | Orchestration |
| **Flower** | http://localhost:5555 | - | Monitoring Celery |
| **PostgreSQL DW** | localhost:5433 | voir `.env` | Connexion directe |
| **dbt Docs** | http://localhost:8081 | - | Documentation (si actif) |

---

## � Dépannage

### Erreur "Connection refused" sur OLTP

```bash
# Vérifier connectivité
ping <OLTP_PG_HOST>

# Tester connexion PostgreSQL
psql -h <OLTP_PG_HOST> -p <OLTP_PG_PORT> -U <OLTP_PG_USER> -d <OLTP_PG_DATABASE>
```

### DAGs non visibles

```bash
# Logs du dag-processor
docker-compose logs airflow-dag-processor

# Vérifier syntaxe Python
docker-compose exec airflow-scheduler python /opt/airflow/dags/<dag_file>.py
```

### dbt : "Database Error"

```bash
# Tester configuration dbt
docker-compose exec airflow-scheduler bash
cd /opt/airflow/datayoti_dbt
dbt debug
```

**Vérifier** :
- `host: datamart-db` (nom du service Docker)
- `port: 5432` (port interne conteneur)
- Credentials dans `profiles/profiles.yml`

---

## 📁 Structure simplifiée

```
datayoti-warehouse/
├── docker-compose.yml              # Infrastructure
├── .env.example                    # Template config
├── airflow/
│   ├── dags/                       # Pipelines Airflow
│   └── config/                     # Configuration
└── datayoti_dbt/
    ├── models/                     # Transformations dbt
    │   ├── raw/                    # Couche 1: DDL
    │   ├── staging/                # Couche 2: Nettoyage
    │   ├── intermediate/           # Couche 3: Logique métier
    │   └── marts/                  # Couche 4: Star Schema
    ├── seeds/                      # Données référence
    │   └── conformity_rules.csv
    ├── snapshots/                  # Historisation SCD2
    └── profiles/                   # Connexion DB
```

---

## � Sécurité

⚠️ **En production** :
1. Changer **tous** les mots de passe par défaut
2. Régénérer la clé Fernet Airflow
3. Ne **jamais** commiter `.env`
4. Utiliser des secrets managers (Vault, AWS Secrets)
5. Activer SSL/TLS pour PostgreSQL
6. Configurer des backups réguliers

---

## � Ressources

- 📖 [Apache Airflow](https://airflow.apache.org/docs/)
- 📖 [dbt Documentation](https://docs.getdbt.com/)
- 📖 [Kimball Dimensional Modeling](https://www.kimballgroup.com/)
- 🔗 [Firmware ESP32](../datayoti-firmware)
- 🔗 [Infrastructure temps réel](../datayoti-realtime)

---

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

## 👨‍� Contact

- **LinkedIn** : [Mehdi Akniou](https://linkedin.com/in/mehdi-akniou)
- **Email** : contact@mehdi-akniou.com
- **GitHub** : [@medkan01](https://github.com/medkan01)

---

**DataYoti Warehouse** - Du signal à l'action 📊

*Data Warehouse et Business Intelligence pour l'IoT environnemental*