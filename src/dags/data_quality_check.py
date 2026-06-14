"""Data quality check DAG - runs Great Expectations-style checks."""
from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import logging

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "data-quality-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
    "email_on_failure": False,
}

def check_row_count(**context):
    logger.info("Checking row count...")
    row_count = 500  # In production: query actual table
    assert row_count > 0, "Table is empty!"
    assert row_count < 1_000_000, "Unexpectedly large row count"
    logger.info("Row count check passed: %d rows", row_count)

def check_null_values(**context):
    logger.info("Checking for null values in critical columns...")
    null_rates = {"id": 0.0, "value": 0.02, "created_at": 0.0}
    for col, rate in null_rates.items():
        assert rate < 0.05, f"Null rate too high in column {col}: {rate:.1%}"
    logger.info("Null value checks passed")

def check_data_freshness(**context):
    from datetime import datetime, timezone
    logger.info("Checking data freshness...")
    # In production: query max(updated_at) from table
    hours_since_update = 2
    assert hours_since_update < 24, f"Data is {hours_since_update}h old - stale!"
    logger.info("Freshness check passed: updated %dh ago", hours_since_update)

def generate_quality_report(**context):
    ti = context["ti"]
    report = {
        "dag_run_id": context["run_id"],
        "checks": ["row_count", "null_values", "freshness"],
        "status": "PASSED",
        "timestamp": str(context["execution_date"]),
    }
    logger.info("Quality report: %s", report)

with DAG(
    dag_id="data_quality_checks",
    default_args=DEFAULT_ARGS,
    description="Daily data quality validation pipeline",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
    tags=["quality", "monitoring"],
) as dag:
    check_rows = PythonOperator(task_id="check_row_count", python_callable=check_row_count)
    check_nulls = PythonOperator(task_id="check_null_values", python_callable=check_null_values)
    check_fresh = PythonOperator(task_id="check_data_freshness", python_callable=check_data_freshness)
    report = PythonOperator(task_id="generate_report", python_callable=generate_quality_report)

    [check_rows, check_nulls, check_fresh] >> report
