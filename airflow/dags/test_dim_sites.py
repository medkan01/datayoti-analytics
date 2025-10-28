import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'datayoti',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
}

dag = DAG(
    'test_dim_sites',
    default_args=default_args,
    description='DAG to test the dim_sites table in the mart layer',
    schedule=None,
    catchup=False,
    tags=["dbt", "data-pipeline", "iot", "testing", "dim_sites"],
)

# Commande de base pour dbt
dbt_base_cmd = 'cd /opt/airflow/datayoti_dbt && /home/airflow/.local/bin/dbt'

# Tâche de vérification et d'installation des dépendances dbt
install_dbt_dependencies = BashOperator(
    task_id='install_dbt_dependencies',
    bash_command=f'{dbt_base_cmd} deps --profiles-dir profiles',
    dag=dag,
)

# Tâche de vérification de la configuration
check_dbt_environment = BashOperator(
    task_id='check_dbt_environment',
    bash_command=f'{dbt_base_cmd} debug --profiles-dir profiles',
    dag=dag,
)

# dbt run et test de staging.stg_sites pour s'assurer que les données sont présentes avant de tester dim_sites
run_stg_sites = BashOperator(
    task_id='run_stg_sites_model',
    bash_command=f'{dbt_base_cmd} run --select staging.stg_sites --profiles-dir profiles',
    dag=dag,
)

run_test_stg_sites = BashOperator(
    task_id='test_stg_sites_model',
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

# dbt run et test de la table int_sites_scd2 avant de tester dim_sites
run_int_sites_scd2 = BashOperator(
    task_id='run_int_sites_scd2_model',
    bash_command=f'{dbt_base_cmd} run --select intermediate.int_sites_scd2 --profiles-dir profiles',
    dag=dag,
)

test_int_sites_scd2 = BashOperator(
    task_id='test_int_sites_scd2_model',
    bash_command=f'{dbt_base_cmd} test --select intermediate.int_sites_scd2 --profiles-dir profiles',
    dag=dag,
)

# dbt run et test de la table dim_sites
run_dim_sites = BashOperator(
    task_id='run_dim_sites_model',
    bash_command=f'{dbt_base_cmd} run --select marts.dim_sites --profiles-dir profiles',
    dag=dag,
)

test_dim_sites = BashOperator(
    task_id='test_dim_sites_model',
    bash_command=f'{dbt_base_cmd} test --select marts.dim_sites --profiles-dir profiles',
    dag=dag,
)

# dbt run et test de la table staging.stg_devices nécessaire pour les dépendances de dim_sites
run_stg_devices = BashOperator(
    task_id='run_stg_devices_model',
    bash_command=f'{dbt_base_cmd} run --select staging.stg_devices --profiles-dir profiles',
    dag=dag,
)

test_stg_devices = BashOperator(
    task_id='test_stg_devices_model',
    bash_command=f'{dbt_base_cmd} test --select staging.stg_devices --profiles-dir profiles',
    dag=dag,
)

# dbt run et test de la table intermediate.int_devices nécessaire pour les dépendances de dim_sites
run_int_devices = BashOperator(
    task_id='run_int_devices_model',
    bash_command=f'{dbt_base_cmd} run --select intermediate.int_devices --profiles-dir profiles',
    dag=dag,
)

test_int_devices = BashOperator(
    task_id='test_int_devices_model',
    bash_command=f'{dbt_base_cmd} test --select intermediate.int_devices --profiles-dir profiles',
    dag=dag,
)

# dbt snapshot et run de la table intermediate.int_devices_scd2 nécessaire pour les dépendances de dim_sites
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

# dbt run de la table intermediate.int_devices_scd2 nécessaire pour les dépendances de dim_sites
run_int_devices_scd2 = BashOperator(
    task_id='run_int_devices_scd2_model',
    bash_command=f'{dbt_base_cmd} run --select intermediate.int_devices_scd2 --profiles-dir profiles',
    dag=dag,
)

test_int_devices_scd2 = BashOperator(
    task_id='test_int_devices_scd2_model',
    bash_command=f'{dbt_base_cmd} test --select intermediate.int_devices_scd2 --profiles-dir profiles',
    dag=dag,
)

# dbt run et test de la table marts.dim_devices nécessaire pour les dépendances de dim_sites
run_dim_devices = BashOperator(
    task_id='run_dim_devices_model',
    bash_command=f'{dbt_base_cmd} run --select marts.dim_devices --profiles-dir profiles',
    dag=dag,
)

test_dim_devices = BashOperator(
    task_id='test_dim_devices_model',
    bash_command=f'{dbt_base_cmd} test --select marts.dim_devices --profiles-dir profiles',
    dag=dag,
)

# Définition des dépendances entre les tâches
install_dbt_dependencies >> check_dbt_environment
check_dbt_environment >> run_stg_sites >> run_test_stg_sites
run_test_stg_sites >> run_sites_snapshot >> test_sites_snapshot
test_sites_snapshot >> run_int_sites_scd2 >> test_int_sites_scd2
test_int_sites_scd2 >> run_dim_sites >> test_dim_sites
test_dim_sites >> run_stg_devices >> test_stg_devices
test_stg_devices >> run_int_devices >> test_int_devices
test_int_devices >> run_devices_snapshot >> test_devices_snapshot
test_devices_snapshot >> run_int_devices_scd2 >> test_int_devices_scd2
test_int_devices_scd2 >> run_dim_devices >> test_dim_devices