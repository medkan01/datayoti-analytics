import pandas as pd
import logging
from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)

def get_max_timestamp(
        olap_hook: PostgresHook,
        table_name: str,
        timestamp_column: str
    ):
    """Récupérer le timestamp maximum déjà présent dans OLAP pour une table donnée."""
    max_ts_query = f"SELECT COALESCE(MAX({timestamp_column}), '1900-01-01 00:00:00') as max_ts FROM {table_name};"
    max_ts_result = olap_hook.get_first(max_ts_query)
    return max_ts_result[0] if max_ts_result else '1900-01-01 00:00:00'

def incremental_append(
        oltp_hook: PostgresHook,
        olap_hook: PostgresHook,
        source_table: str,
        target_table: str,
        timestamp_column: str
    ):
    max_timestamp = get_max_timestamp(olap_hook, target_table, timestamp_column)
    logger.info(f"Incremental key for {source_table} is {timestamp_column} > {max_timestamp}")

    query = f"""
        SELECT *
        FROM {source_table}
        WHERE {timestamp_column} > '{max_timestamp}'
        ORDER BY {timestamp_column};
    """

    df = oltp_hook.get_pandas_df(sql=query, coerce_float=False, dtype=str)
    logger.info(f"Extracted {len(df)} new rows from {source_table}.")

    if len(df) > 0:
        olap_hook.insert_rows(
            table=target_table,
            rows=df.values.tolist(),
            target_fields=list(df.columns),
        )
        logger.info(f"Inserted {len(df)} new rows into {target_table}.")

    return len(df)

@dag(
    dag_id="ingest_raw_iot_data",
    description="DAG pour ingérer les données brutes IoT depuis la base OLTP vers la base OLAP.",
    schedule="@daily",
    start_date=pd.Timestamp("2024-01-01"),
    catchup=False,
    tags=["raw", "ingestion", "iot"],
)
def ingest_raw_iot_data_dag():
    @task()
    def bootstrap_raw_schema():
        """Créer les tables raw dans la base OLAP si elles n'existent pas déjà."""
        logger.info("Ensuring raw tables exist in OLAP database.")
        
        olap_hook = PostgresHook(postgres_conn_id="olap_connection")
        
        # Créer le schéma raw s'il n'existe pas
        olap_hook.run("CREATE SCHEMA IF NOT EXISTS raw;")
        
        # Table raw_sites
        create_raw_sites = """
        CREATE TABLE IF NOT EXISTS raw.raw_sites (
            id TEXT,
            site_ref TEXT,
            site_name TEXT,
            description TEXT,
            created_at TEXT,
            updated_at TEXT
        );
        """
        
        # Table raw_devices
        create_raw_devices = """
        CREATE TABLE IF NOT EXISTS raw.raw_devices (
            id TEXT,
            device_mac_addr TEXT,
            site_ref TEXT,
            created_at TEXT,
            updated_at TEXT
        );
        """
        
        # Table raw_device_heartbeats
        create_raw_device_heartbeats = """
        CREATE TABLE IF NOT EXISTS raw.raw_device_heartbeats (
            time TEXT,
            device_mac_addr TEXT,
            rssi TEXT,
            free_heap TEXT,
            uptime TEXT,
            min_heap TEXT,
            ntp_sync TEXT,
            reception_time TEXT
        );
        """
        
        # Table raw_sensor_data
        create_raw_sensor_data = """
        CREATE TABLE IF NOT EXISTS raw.raw_sensor_data (
            time TEXT,
            device_mac_addr TEXT,
            temperature TEXT,
            humidity TEXT,
            reception_time TEXT
        );
        """
        
        # Exécuter les requêtes de création
        tables_to_create = [
            ("raw.raw_sites", create_raw_sites),
            ("raw.raw_devices", create_raw_devices),
            ("raw.raw_device_heartbeats", create_raw_device_heartbeats),
            ("raw.raw_sensor_data", create_raw_sensor_data)
        ]
        
        for table_name, create_query in tables_to_create:
            try:
                olap_hook.run(create_query)
                logger.info(f"Table {table_name} created or already exists.")
            except Exception as e:
                logger.error(f"Error creating table {table_name}: {str(e)}")
                raise
        
        logger.info("All raw tables ensured in OLAP database.")

    @task()
    def ingest_site_data():
        logger.info("Starting incremental ingestion of 'sites' table from OLTP database.")

        # Créer les hooks à l'intérieur de la tâche
        oltp_hook = PostgresHook(postgres_conn_id="oltp_connection")
        olap_hook = PostgresHook(postgres_conn_id="olap_connection")

        # Récupérer le timestamp maximum déjà présent dans OLAP
        max_ts = get_max_timestamp(olap_hook, "raw.raw_sites", "updated_at")
        logger.info(f"Maximum updated_at in OLAP: {max_ts}")

        # Extraire les données depuis OLTP où updated_at > max_ts
        query = f"SELECT * FROM sites WHERE updated_at > '{max_ts}' ORDER BY updated_at;"
        
        # Récupérer les données dans un DataFrame pandas avec tous les types de données en tant que chaînes
        df_sites = oltp_hook.get_pandas_df(sql=query, coerce_float=False, dtype=str)
        
        logger.info(f"Extracted {len(df_sites)} new/updated rows from sites table.")

        # Traiter les données (upsert)
        if len(df_sites) > 0:
            for _, row in df_sites.iterrows():
                # Vérifier si l'enregistrement existe déjà
                check_query = f"SELECT COUNT(*) FROM raw.raw_sites WHERE site_ref = '{row['site_ref']}';"
                exists = olap_hook.get_first(check_query)[0] > 0
                
                if exists:
                    # Mettre à jour l'enregistrement existant
                    update_query = f"""
                    UPDATE raw.raw_sites
                    SET site_name = '{row['site_name']}',
                        description = '{row['description']}',
                        updated_at = '{row['updated_at']}'
                    WHERE site_ref = '{row['site_ref']}';
                    """
                    olap_hook.run(update_query)
                else:
                    # Insérer un nouveau site
                    olap_hook.insert_rows(
                        table="raw.raw_sites",
                        rows=[row.values.tolist()],
                        target_fields=list(df_sites.columns),
                    )
            
            logger.info(f"Processed {len(df_sites)} sites (upsert completed).")
        else:
            logger.info("No new/updated sites data to process.")

        return len(df_sites)
    
    @task()
    def ingest_device_data():
        logger.info("Starting incremental ingestion of 'devices' table from OLTP database.")

        # Créer les hooks à l'intérieur de la tâche
        oltp_hook = PostgresHook(postgres_conn_id="oltp_connection")
        olap_hook = PostgresHook(postgres_conn_id="olap_connection")
    
        # Récupérer le timestamp maximum déjà présent dans OLAP
        max_ts = get_max_timestamp(olap_hook, "raw.raw_devices", "updated_at")
        logger.info(f"Maximum updated_at in OLAP: {max_ts}")

        # Extraire les données depuis OLTP où updated_at > max_ts
        query = f"SELECT * FROM devices WHERE updated_at > '{max_ts}' ORDER BY updated_at;"
        
        # Récupérer les données dans un DataFrame pandas avec tous les types de données en tant que chaînes
        df_devices = oltp_hook.get_pandas_df(sql=query, coerce_float=False, dtype=str)
        
        logger.info(f"Extracted {len(df_devices)} new/updated rows from devices table.")

        # Traiter les données (upsert)
        if len(df_devices) > 0:
            for _, row in df_devices.iterrows():
                # Vérifier si l'enregistrement existe déjà
                check_query = f"SELECT COUNT(*) FROM raw.raw_devices WHERE device_mac_addr = '{row['device_mac_addr']}';"
                exists = olap_hook.get_first(check_query)[0] > 0
                
                if exists:
                    # Mettre à jour l'enregistrement existant
                    update_query = f"""
                    UPDATE raw.raw_devices
                    SET site_ref = '{row['site_ref']}',
                        updated_at = '{row['updated_at']}'
                    WHERE device_mac_addr = '{row['device_mac_addr']}';
                    """
                    olap_hook.run(update_query)
                else:
                    # Insérer un nouveau device
                    olap_hook.insert_rows(
                        table="raw.raw_devices",
                        rows=[row.values.tolist()],
                        target_fields=list(df_devices.columns),
                    )
            
            logger.info(f"Processed {len(df_devices)} devices (upsert completed).")
        else:
            logger.info("No new/updated devices data to process.")

        return len(df_devices)
    
    @task()
    def ingest_device_heartbeats():
        logger.info("Starting incremental ingestion of 'device_heartbeats' table from OLTP database.")

        # Créer les hooks à l'intérieur de la tâche
        oltp_hook = PostgresHook(postgres_conn_id="oltp_connection")
        olap_hook = PostgresHook(postgres_conn_id="olap_connection")

        count = incremental_append(
            oltp_hook=oltp_hook,
            olap_hook=olap_hook,
            source_table="device_heartbeats",
            target_table="raw.raw_device_heartbeats",
            timestamp_column="reception_time"
        )

        logger.info(f"Inserted {count} new rows into device_heartbeats table.")
        return count

    @task()
    def ingest_sensor_data():
        """Ingestion incrémentale des données de capteurs basée sur reception_time."""
        logger.info("Starting incremental ingestion of 'sensor_data' table from OLTP database.")

        # Créer les hooks à l'intérieur de la tâche
        oltp_hook = PostgresHook(postgres_conn_id="oltp_connection")
        olap_hook = PostgresHook(postgres_conn_id="olap_connection")

        count = incremental_append(
            oltp_hook=oltp_hook,
            olap_hook=olap_hook,
            source_table="sensor_data",
            target_table="raw.raw_sensor_data",
            timestamp_column="reception_time"
        )

        logger.info(f"Inserted {count} new rows into sensor_data table.")
        return count
    
    # Définir les tâches du DAG
    bootstrap = bootstrap_raw_schema()

    d_devices = ingest_device_data()
    d_sites = ingest_site_data()
    d_heartbeats = ingest_device_heartbeats()
    d_sensor_data = ingest_sensor_data()
    
    # Définir les dépendances entre les tâches (pour l'ingestion, pas de dépendance stricte car données encore brutes)
    bootstrap >> [d_sites, d_devices, d_heartbeats, d_sensor_data]

# Define the DAG
ingest_raw_iot_data_dag_instance = ingest_raw_iot_data_dag()