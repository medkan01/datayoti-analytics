import pandas as pd
import logging
from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)

@dag(
    dag_id="debug_clear_schemas",
    description="DAG simple pour purger/supprimer facilement les différents schémas (raw, staging, intermediate, marts)",
    schedule=None,  # Manuel uniquement
    start_date=pd.Timestamp("2024-01-01"),
    catchup=False,
    tags=["debug", "cleanup", "purge", "drop"],
)
def debug_clear_schemas_dag():
    @task
    def clear_schemas():
        schemas = ["public", "raw", "staging", "intermediate", "marts", "snapshots"]
        pg_hook = PostgresHook(postgres_conn_id="olap_connection")
        for schema in schemas:
            drop_sql = f"DROP SCHEMA IF EXISTS {schema} CASCADE;"
            logger.info(f"Dropping schema: {schema}")
            pg_hook.run(drop_sql)

    clear_schemas_task = clear_schemas()

debug_clear_schemas_dag = debug_clear_schemas_dag()