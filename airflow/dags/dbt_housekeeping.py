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
    'dbt_housekeeping',
    default_args=default_args,
    description='Tâches de maintenance et de documentation pour les projets dbt IoT, incluant la génération de documentation et la vérification de l\'environnement dbt.',
    schedule="0 1 * * 0",  # Tous les dimanches à 01:00 AM
    catchup=False,
    tags=['datayoti', 'dbt', 'iot', 'maintenance', 'documentation'],
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

install_dbt_dependencies >> check_dbt_environment >> generate_docs