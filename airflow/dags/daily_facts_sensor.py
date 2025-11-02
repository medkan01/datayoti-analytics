import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'datayoti',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_facts_sensor',
    default_args=default_args,
    description='Produire les tables de faits quotidiennes pour les capteurs IoT en utilisant dbt, avec des tests de qualité des données et des validations de bout en bout.',
    schedule="0 1 * * *",  # Tous les jours à 01:00 AM
    catchup=False,
    tags=['datayoti', 'dbt', 'iot', 'data-quality', 'fact', 'daily'],
)

# Commande de base pour dbt
dbt_base_cmd = 'cd /opt/airflow/datayoti_dbt && /home/airflow/.local/bin/dbt'

# =====================================================
# SETUP ET VÉRIFICATIONS INITIALES
# =====================================================

check_raw_sources = BashOperator(
    task_id='check_raw_sources',
    bash_command=f'{dbt_base_cmd} test --select source:* --profiles-dir profiles',
    dag=dag,
)

# =====================================================
# PIPELINE SENSOR DATA
# =====================================================

run_stg_sensor_data = BashOperator(
    task_id='run_stg_sensor_data',
    bash_command=f'{dbt_base_cmd} run --select staging.stg_sensor_data --profiles-dir profiles',
    dag=dag,
)

test_stg_sensor_data = BashOperator(
    task_id='test_stg_sensor_data',
    bash_command=f'{dbt_base_cmd} test --select staging.stg_sensor_data --profiles-dir profiles',
    dag=dag,
)

run_stg_device_heartbeats = BashOperator(
    task_id='run_stg_device_heartbeats',
    bash_command=f'{dbt_base_cmd} run --select staging.stg_device_heartbeats --profiles-dir profiles',
    dag=dag,
)

test_stg_device_heartbeats = BashOperator(
    task_id='test_stg_device_heartbeats',
    bash_command=f'{dbt_base_cmd} test --select staging.stg_device_heartbeats --profiles-dir profiles',
    dag=dag,
)

# =====================================================
# AGRÉGATIONS INTERMÉDIAIRES
# =====================================================

run_int_daily_sensor_reading = BashOperator(
    task_id='run_int_daily_sensor_reading',
    bash_command=f'{dbt_base_cmd} run --select intermediate.int_daily_sensor_reading --profiles-dir profiles',
    dag=dag,
)

test_int_daily_sensor_reading = BashOperator(
    task_id='test_int_daily_sensor_reading',
    bash_command=f'{dbt_base_cmd} test --select intermediate.int_daily_sensor_reading --profiles-dir profiles',
    dag=dag,
)

run_int_daily_sensor_health = BashOperator(
    task_id='run_int_daily_sensor_health',
    bash_command=f'{dbt_base_cmd} run --select intermediate.int_daily_sensor_health --profiles-dir profiles',
    dag=dag,
)

test_int_daily_sensor_health = BashOperator(
    task_id='test_int_daily_sensor_health',
    bash_command=f'{dbt_base_cmd} test --select intermediate.int_daily_sensor_health --profiles-dir profiles',
    dag=dag,
)

run_int_daily_site_env = BashOperator(
    task_id='run_int_daily_site_env',
    bash_command=f'{dbt_base_cmd} run --select intermediate.int_daily_site_env --profiles-dir profiles',
    dag=dag,
)

test_int_daily_site_env = BashOperator(
    task_id='test_int_daily_site_env',
    bash_command=f'{dbt_base_cmd} test --select intermediate.int_daily_site_env --profiles-dir profiles',
    dag=dag,
)

# =====================================================
# TABLES DE FAITS FINALES
# =====================================================

run_fct_daily_sensor_reading = BashOperator(
    task_id='run_fct_daily_sensor_reading',
    bash_command=f'{dbt_base_cmd} run --select marts.fct_daily_sensor_reading --profiles-dir profiles',
    dag=dag,
)

test_fct_daily_sensor_reading = BashOperator(
    task_id='test_fct_daily_sensor_reading',
    bash_command=f'{dbt_base_cmd} test --select marts.fct_daily_sensor_reading --profiles-dir profiles',
    dag=dag,
)

run_fct_daily_sensor_health = BashOperator(
    task_id='run_fct_daily_sensor_health',
    bash_command=f'{dbt_base_cmd} run --select marts.fct_daily_sensor_health --profiles-dir profiles',
    dag=dag,
)

test_fct_daily_sensor_health = BashOperator(
    task_id='test_fct_daily_sensor_health',
    bash_command=f'{dbt_base_cmd} test --select marts.fct_daily_sensor_health --profiles-dir profiles',
    dag=dag,
)

run_fct_daily_site_compliance = BashOperator(
    task_id='run_fct_daily_site_compliance',
    bash_command=f'{dbt_base_cmd} run --select marts.fct_daily_site_compliance --profiles-dir profiles',
    dag=dag,
)

test_fct_daily_site_compliance = BashOperator(
    task_id='test_fct_daily_site_compliance',
    bash_command=f'{dbt_base_cmd} test --select marts.fct_daily_site_compliance --profiles-dir profiles',
    dag=dag,
)

run_vw_daily_site_compliance_summary = BashOperator(
    task_id='run_vw_daily_site_compliance_summary',
    bash_command=f'{dbt_base_cmd} run --select marts.vw_daily_site_compliance_summary --profiles-dir profiles',
    dag=dag,
)

test_vw_daily_site_compliance_summary = BashOperator(
    task_id='test_vw_daily_site_compliance_summary',
    bash_command=f'{dbt_base_cmd} test --select marts.vw_daily_site_compliance_summary --profiles-dir profiles',
    dag=dag,
)

# =====================================================
# DÉFINITION DES DÉPENDANCES
# =====================================================

# Vérification des sources brutes
check_raw_sources

# Pipeline Sensor Data (qui sera parallelisé avec le pipeline de santé des appareils)
check_raw_sources >>run_stg_sensor_data >> test_stg_sensor_data
test_stg_sensor_data >> run_int_daily_sensor_reading >> test_int_daily_sensor_reading
test_int_daily_sensor_reading >> run_fct_daily_sensor_reading >> test_fct_daily_sensor_reading

# Pipeline Device Heartbeats
check_raw_sources >> run_stg_device_heartbeats >> test_stg_device_heartbeats
test_stg_device_heartbeats >> run_int_daily_sensor_health >> test_int_daily_sensor_health
test_int_daily_sensor_health >> run_fct_daily_sensor_health >> test_fct_daily_sensor_health

# Pipeline Site Environment (dépend des lectures de capteurs)
test_int_daily_sensor_reading >> run_int_daily_site_env >> test_int_daily_site_env

# Pipeline Conformité Site (dépend de l'environnement site)
test_int_daily_site_env >> run_fct_daily_site_compliance >> test_fct_daily_site_compliance

# Vue de synthèse conformité (dépend du fait de conformité)
test_fct_daily_site_compliance >> run_vw_daily_site_compliance_summary >> test_vw_daily_site_compliance_summary
