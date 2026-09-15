from datetime import UTC, datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="ecommerce_pipeline",
    description="E-commerce ingestion and transformation pipeline",
    start_date=datetime(2026, 1, 1, tzinfo=UTC),
    schedule=None,
    catchup=False,
    tags=["ecommerce", "portfolio"],
) as dag:
    ingest_orders = BashOperator(
        task_id="ingest_orders",
        bash_command=(
            "cd /opt/airflow && export PYTHONPATH=/opt/airflow && python src/ingestion/orders.py"
        ),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "cd /opt/airflow/dbt/ecommerce && dbt run --profiles-dir /opt/airflow/dbt/profiles"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "cd /opt/airflow/dbt/ecommerce && dbt test --profiles-dir /opt/airflow/dbt/profiles"
        ),
    )

    ingest_orders >> dbt_run >> dbt_test
