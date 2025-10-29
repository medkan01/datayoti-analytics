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
    'transform_raw_to_mart_iot',
    default_args=default_args,
    description='Pipeline complet de validation des données IoT - staging → intermediate → marts',
    schedule="0 1 * * *",  # Tous les jours à 01:00 AM
    catchup=False,
    tags=["dbt", "iot", "data-quality", "end-to-end", "validation"],
)

# Commande de base pour dbt
dbt_base_cmd = 'cd /opt/airflow/datayoti_dbt && /home/airflow/.local/bin/dbt'

# =====================================================
# SETUP ET VÉRIFICATIONS INITIALES
# =====================================================

install_dbt_dependencies = BashOperator(
    task_id='install_dbt_dependencies',
    bash_command=f'{dbt_base_cmd} deps --profiles-dir profiles',
    dag=dag,
)

check_dbt_environment = BashOperator(
    task_id='check_dbt_environment',
    bash_command=f'{dbt_base_cmd} debug --profiles-dir profiles',
    dag=dag,
)

check_raw_sources = BashOperator(
    task_id='check_raw_sources',
    bash_command=f'{dbt_base_cmd} test --select source:* --profiles-dir profiles',
    dag=dag,
)

# =====================================================
# DIMENSION DATES (INDÉPENDANTE)
# =====================================================

run_dim_dates = BashOperator(
    task_id='run_dim_dates',
    bash_command=f'{dbt_base_cmd} run --select marts.dim_dates --profiles-dir profiles',
    dag=dag,
)

# =====================================================
# PIPELINE SITES
# =====================================================

run_stg_sites = BashOperator(
    task_id='run_stg_sites',
    bash_command=f'{dbt_base_cmd} run --select staging.stg_sites --profiles-dir profiles',
    dag=dag,
)

test_stg_sites = BashOperator(
    task_id='test_stg_sites',
    bash_command=f'{dbt_base_cmd} test --select staging.stg_sites --profiles-dir profiles',
    dag=dag,
)

run_sites_snapshot = BashOperator(
    task_id='run_sites_snapshot',
    bash_command=f'{dbt_base_cmd} snapshot --select sites_snapshot --profiles-dir profiles',
    dag=dag,
)

test_sites_snapshot = BashOperator(
    task_id='test_sites_snapshot',
    bash_command=f'{dbt_base_cmd} test --select sites_snapshot --profiles-dir profiles',
    dag=dag,
)

run_int_sites_scd2 = BashOperator(
    task_id='run_int_sites_scd2',
    bash_command=f'{dbt_base_cmd} run --select intermediate.int_sites_scd2 --profiles-dir profiles',
    dag=dag,
)

test_int_sites_scd2 = BashOperator(
    task_id='test_int_sites_scd2',
    bash_command=f'{dbt_base_cmd} test --select intermediate.int_sites_scd2 --profiles-dir profiles',
    dag=dag,
)

run_dim_sites = BashOperator(
    task_id='run_dim_sites',
    bash_command=f'{dbt_base_cmd} run --select marts.dim_sites --profiles-dir profiles',
    dag=dag,
)

test_dim_sites = BashOperator(
    task_id='test_dim_sites',
    bash_command=f'{dbt_base_cmd} test --select marts.dim_sites --profiles-dir profiles',
    dag=dag,
)

# =====================================================
# PIPELINE DEVICES
# =====================================================

run_stg_devices = BashOperator(
    task_id='run_stg_devices',
    bash_command=f'{dbt_base_cmd} run --select staging.stg_devices --profiles-dir profiles',
    dag=dag,
)

test_stg_devices = BashOperator(
    task_id='test_stg_devices',
    bash_command=f'{dbt_base_cmd} test --select staging.stg_devices --profiles-dir profiles',
    dag=dag,
)

run_int_devices = BashOperator(
    task_id='run_int_devices',
    bash_command=f'{dbt_base_cmd} run --select intermediate.int_devices --profiles-dir profiles',
    dag=dag,
)

test_int_devices = BashOperator(
    task_id='test_int_devices',
    bash_command=f'{dbt_base_cmd} test --select intermediate.int_devices --profiles-dir profiles',
    dag=dag,
)

run_devices_snapshot = BashOperator(
    task_id='run_devices_snapshot',
    bash_command=f'{dbt_base_cmd} snapshot --select devices_snapshot --profiles-dir profiles',
    dag=dag,
)

test_devices_snapshot = BashOperator(
    task_id='test_devices_snapshot',
    bash_command=f'{dbt_base_cmd} test --select devices_snapshot --profiles-dir profiles',
    dag=dag,
)

run_int_devices_scd2 = BashOperator(
    task_id='run_int_devices_scd2',
    bash_command=f'{dbt_base_cmd} run --select intermediate.int_devices_scd2 --profiles-dir profiles',
    dag=dag,
)

test_int_devices_scd2 = BashOperator(
    task_id='test_int_devices_scd2',
    bash_command=f'{dbt_base_cmd} test --select intermediate.int_devices_scd2 --profiles-dir profiles',
    dag=dag,
)

run_dim_devices = BashOperator(
    task_id='run_dim_devices',
    bash_command=f'{dbt_base_cmd} run --select marts.dim_devices --profiles-dir profiles',
    dag=dag,
)

test_dim_devices = BashOperator(
    task_id='test_dim_devices',
    bash_command=f'{dbt_base_cmd} test --select marts.dim_devices --profiles-dir profiles',
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

# =====================================================
# DOCUMENTATION
# =====================================================

generate_docs = BashOperator(
    task_id='generate_dbt_docs',
    bash_command=f'{dbt_base_cmd} docs generate --profiles-dir profiles',
    dag=dag,
)

# =====================================================
# DÉFINITION DES DÉPENDANCES
# =====================================================

# Setup initial
install_dbt_dependencies >> check_dbt_environment >> check_raw_sources

# Dimension dates (indépendante)
check_raw_sources >> run_dim_dates

# Pipeline Sites
check_raw_sources >> run_stg_sites >> test_stg_sites
test_stg_sites >> run_sites_snapshot >> test_sites_snapshot
test_sites_snapshot >> run_int_sites_scd2 >> test_int_sites_scd2
[run_dim_dates, test_int_sites_scd2] >> run_dim_sites >> test_dim_sites

# Pipeline Devices (dépend des sites)
test_dim_sites >> run_stg_devices >> test_stg_devices
test_stg_devices >> run_int_devices >> test_int_devices
test_int_devices >> run_devices_snapshot >> test_devices_snapshot
test_devices_snapshot >> run_int_devices_scd2 >> test_int_devices_scd2
test_int_devices_scd2 >> run_dim_devices >> test_dim_devices

# Pipeline Sensor Data (parallélisé)
[test_dim_devices] >> run_stg_sensor_data >> test_stg_sensor_data
[test_dim_devices] >> run_stg_device_heartbeats >> test_stg_device_heartbeats

# Agrégations intermédiaires
test_stg_sensor_data >> run_int_daily_sensor_reading >> test_int_daily_sensor_reading
test_stg_device_heartbeats >> run_int_daily_sensor_health >> test_int_daily_sensor_health

# Tables de faits finales
[test_int_daily_sensor_reading, test_dim_sites] >> run_fct_daily_sensor_reading >> test_fct_daily_sensor_reading
[test_int_daily_sensor_health, test_dim_sites] >> run_fct_daily_sensor_health >> test_fct_daily_sensor_health

# Documentation finale
[test_fct_daily_sensor_reading, test_fct_daily_sensor_health] >> generate_docs