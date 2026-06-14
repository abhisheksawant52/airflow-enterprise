"""
Enterprise ETL Pipeline DAG - Extracts, transforms, and loads data.
Demonstrates production Airflow patterns: sensors, branching, retries, SLAs.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
import logging
import random

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
}

def extract_data(**context):
    logger.info("Extracting data from source systems...")
    records = [{"id": i, "value": __import__("random").uniform(1, 100)} for i in range(100)]
    context["ti"].xcom_push(key="raw_records", value=records)
    logger.info("Extracted %d records", len(records))
    return len(records)

def validate_data(**context):
    records = context["ti"].xcom_pull(key="raw_records", task_ids="extract")
    if not records:
        raise ValueError("No records extracted")
    invalid = [r for r in records if r["value"] < 0]
    if len(invalid) > len(records) * 0.1:
        return "handle_invalid_data"
    return "transform_data"

def transform_data(**context):
    records = context["ti"].xcom_pull(key="raw_records", task_ids="extract")
    transformed = [{"id": r["id"], "value": round(r["value"] * 1.1, 2), "processed": True} for r in records]
    context["ti"].xcom_push(key="transformed_records", value=transformed)
    logger.info("Transformed %d records", len(transformed))

def load_data(**context):
    records = context["ti"].xcom_pull(key="transformed_records", task_ids="transform_data")
    logger.info("Loading %d records to data warehouse...", len(records))
    # In production: insert into database/data warehouse
    logger.info("Load complete")

def handle_invalid(**context):
    logger.warning("High rate of invalid data detected - alerting team")

with DAG(
    dag_id="enterprise_etl_pipeline",
    default_args=DEFAULT_ARGS,
    description="Production ETL pipeline with branching and retries",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
    tags=["etl", "production"],
    max_active_runs=1,
) as dag:
    start = EmptyOperator(task_id="start")
    extract = PythonOperator(task_id="extract", python_callable=extract_data)
    validate = BranchPythonOperator(task_id="validate", python_callable=validate_data)
    transform = PythonOperator(task_id="transform_data", python_callable=transform_data)
    load = PythonOperator(task_id="load_data", python_callable=load_data)
    invalid_handler = PythonOperator(task_id="handle_invalid_data", python_callable=handle_invalid)
    end = EmptyOperator(task_id="end", trigger_rule="none_failed_min_one_success")

    start >> extract >> validate >> [transform, invalid_handler]
    transform >> load >> end
    invalid_handler >> end
