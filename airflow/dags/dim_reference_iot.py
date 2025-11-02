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
    'dim_reference_iot',
    default_args=default_args,
    description='Construire et maintenir le référentiel analytique IoT stable avec dbt, incluant des tests de qualité des données et des validations de bout en bout.',
    schedule="0 1 * * 0",  # Tous les dimanches à 01:00 AM
    catchup=False,
    tags=['datayoti', 'dbt', 'iot', 'data-quality', 'dimension', 'reference', 'slow-changing'],
)

# Commande de base pour dbt
dbt_base_cmd = 'cd /opt/airflow/datayoti_dbt && /home/airflow/.local/bin/dbt'

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
# PIPELINE RÈGLES MÉTIER
# =====================================================

run_conformity_rules_seed = BashOperator(
    task_id='run_conformity_rules_seed',
    bash_command=f'{dbt_base_cmd} seed --select conformity_rules --profiles-dir profiles',
    dag=dag,
)

run_stg_conformity_rules = BashOperator(
    task_id='run_stg_conformity_rules',
    bash_command=f'{dbt_base_cmd} run --select staging.stg_conformity_rules --profiles-dir profiles',
    dag=dag,
)

test_stg_conformity_rules = BashOperator(
    task_id='test_stg_conformity_rules',
    bash_command=f'{dbt_base_cmd} test --select staging.stg_conformity_rules --profiles-dir profiles',
    dag=dag,
)

run_int_conformity_rules = BashOperator(
    task_id='run_int_conformity_rules',
    bash_command=f'{dbt_base_cmd} run --select intermediate.int_conformity_rules --profiles-dir profiles',
    dag=dag,
)

test_int_conformity_rules = BashOperator(
    task_id='test_int_conformity_rules',
    bash_command=f'{dbt_base_cmd} test --select intermediate.int_conformity_rules --profiles-dir profiles',
    dag=dag,
)

run_conformity_rules_snapshot = BashOperator(
    task_id='run_conformity_rules_snapshot',
    bash_command=f'{dbt_base_cmd} snapshot --select conformity_rules_snapshot --profiles-dir profiles',
    dag=dag,
)

test_conformity_rules_snapshot = BashOperator(
    task_id='test_conformity_rules_snapshot',
    bash_command=f'{dbt_base_cmd} test --select conformity_rules_snapshot --profiles-dir profiles',
    dag=dag,
)

run_int_conformity_rules_scd2 = BashOperator(
    task_id='run_int_conformity_rules_scd2',
    bash_command=f'{dbt_base_cmd} run --select intermediate.int_conformity_rules_scd2 --profiles-dir profiles',
    dag=dag,
)

test_int_conformity_rules_scd2 = BashOperator(
    task_id='test_int_conformity_rules_scd2',
    bash_command=f'{dbt_base_cmd} test --select intermediate.int_conformity_rules_scd2 --profiles-dir profiles',
    dag=dag,
)

run_dim_conformity_rules = BashOperator(
    task_id='run_dim_conformity_rules',
    bash_command=f'{dbt_base_cmd} run --select marts.dim_conformity_rules --profiles-dir profiles',
    dag=dag,
)

test_dim_conformity_rules = BashOperator(
    task_id='test_dim_conformity_rules',
    bash_command=f'{dbt_base_cmd} test --select marts.dim_conformity_rules --profiles-dir profiles',
    dag=dag,
)



# =====================================================
# DÉFINITION DES DÉPENDANCES
# =====================================================

# Pipeline Dates
run_dim_dates

# Pipeline Sites
run_stg_sites >> test_stg_sites
test_stg_sites >> run_sites_snapshot >> test_sites_snapshot
test_sites_snapshot >> run_int_sites_scd2 >> test_int_sites_scd2
[run_dim_dates, test_int_sites_scd2] >> run_dim_sites >> test_dim_sites

# Pipeline Devices (dépend des sites)
test_dim_sites >> run_stg_devices >> test_stg_devices
test_stg_devices >> run_int_devices >> test_int_devices
test_int_devices >> run_devices_snapshot >> test_devices_snapshot
test_devices_snapshot >> run_int_devices_scd2 >> test_int_devices_scd2
test_int_devices_scd2 >> run_dim_devices >> test_dim_devices

# Pipeline Règles Métier (dépend des sites)
test_dim_sites >> run_conformity_rules_seed
run_conformity_rules_seed >> run_stg_conformity_rules >> test_stg_conformity_rules
test_stg_conformity_rules >> run_int_conformity_rules >> test_int_conformity_rules
test_int_conformity_rules >> run_conformity_rules_snapshot >> test_conformity_rules_snapshot
test_conformity_rules_snapshot >> run_int_conformity_rules_scd2 >> test_int_conformity_rules_scd2
test_int_conformity_rules_scd2 >> run_dim_conformity_rules >> test_dim_conformity_rules