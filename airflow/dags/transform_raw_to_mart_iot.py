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
    description='Complete dbt data pipeline by layers',
    schedule="0 1 * * *",  # Tous les jours à 01:00 AM
    catchup=False,
    tags=["dbt", "data-pipeline", "iot", "transformation", "mart"],
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

# Tests des sources (vérifier que les tables raw existent)
check_raw_sources = BashOperator(
    task_id='check_raw_sources',
    bash_command=f'{dbt_base_cmd} test --select source:* --profiles-dir profiles',
    dag=dag,
)

# Exécution de la couche staging
run_staging = BashOperator(
    task_id='run_staging_models',
    bash_command=f'{dbt_base_cmd} run --select staging --profiles-dir profiles',
    dag=dag,
)

# Tests de la couche staging
test_staging = BashOperator(
    task_id='test_staging_models', 
    bash_command=f'{dbt_base_cmd} test --select staging --profiles-dir profiles',
    dag=dag,
)

# Exécution de la couche intermediate (si elle existe)
run_intermediate = BashOperator(
    task_id='run_intermediate_models',
    bash_command=f'{dbt_base_cmd} run --select intermediate --profiles-dir profiles',
    dag=dag,
)

# Tests de la couche intermediate
test_intermediate = BashOperator(
    task_id='test_intermediate_models',
    bash_command=f'{dbt_base_cmd} test --select intermediate --profiles-dir profiles', 
    dag=dag,
)

# Exécution de la couche marts (si elle existe)
run_marts = BashOperator(
    task_id='run_marts_models',
    bash_command=f'{dbt_base_cmd} run --select marts --profiles-dir profiles',
    dag=dag,
)

# Tests de la couche marts
test_marts = BashOperator(
    task_id='test_marts_models',
    bash_command=f'{dbt_base_cmd} test --select marts --profiles-dir profiles',
    dag=dag,
)

# Génération de la documentation
generate_docs = BashOperator(
    task_id='generate_dbt_docs',
    bash_command=f'{dbt_base_cmd} docs generate --profiles-dir profiles',
    dag=dag,
)

# Définition des dépendances
install_dbt_dependencies >> check_dbt_environment >> check_raw_sources >> run_staging >> test_staging
test_staging >> run_intermediate >> test_intermediate
test_intermediate >> run_marts >> test_marts >> generate_docs