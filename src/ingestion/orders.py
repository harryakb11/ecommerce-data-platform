import csv
import uuid
from datetime import UTC, datetime
from pathlib import Path

from src.utils.database import get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "orders.csv"

PIPELINE_NAME = "ecommerce_orders_ingestion"


def create_raw_table(connection):
    """Create the raw orders table if it does not exist."""

    query = """
    CREATE SCHEMA IF NOT EXISTS raw;

    CREATE TABLE IF NOT EXISTS raw.orders (
        order_id INTEGER PRIMARY KEY,
        order_date DATE,
        customer_id VARCHAR(50),
        product_id VARCHAR(50),
        quantity INTEGER,
        unit_price NUMERIC(18, 2),
        status VARCHAR(50)
    );
    """

    with connection.cursor() as cursor:
        cursor.execute(query)

    connection.commit()


def load_orders(connection):
    """Load orders CSV into PostgreSQL idempotently."""

    with open(CSV_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        rows = [
            (
                int(row["order_id"]),
                row["order_date"],
                row["customer_id"],
                row["product_id"],
                int(row["quantity"]),
                float(row["unit_price"]),
                row["status"],
            )
            for row in reader
        ]

    query = """
    INSERT INTO raw.orders (
        order_id,
        order_date,
        customer_id,
        product_id,
        quantity,
        unit_price,
        status
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (order_id)
    DO UPDATE SET
        order_date = EXCLUDED.order_date,
        customer_id = EXCLUDED.customer_id,
        product_id = EXCLUDED.product_id,
        quantity = EXCLUDED.quantity,
        unit_price = EXCLUDED.unit_price,
        status = EXCLUDED.status;
    """

    with connection.cursor() as cursor:
        cursor.executemany(query, rows)

    connection.commit()

    return len(rows)


def log_pipeline_run(
    connection,
    job_id,
    start_time,
    end_time,
    status,
    rows_processed=0,
    error_message=None,
):
    """Write pipeline execution details to the monitoring table."""

    query = """
    INSERT INTO monitoring.pipeline_runs (
        job_id,
        pipeline_name,
        start_time,
        end_time,
        status,
        rows_processed,
        error_message
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                job_id,
                PIPELINE_NAME,
                start_time,
                end_time,
                status,
                rows_processed,
                error_message,
            ),
        )

    connection.commit()


def run():
    """Run the orders ingestion pipeline."""

    job_id = str(uuid.uuid4())
    start_time = datetime.now(UTC)
    connection = get_connection()

    row_count = 0

    try:
        create_raw_table(connection)

        row_count = load_orders(connection)

        end_time = datetime.now(UTC)

        log_pipeline_run(
            connection=connection,
            job_id=job_id,
            start_time=start_time,
            end_time=end_time,
            status="SUCCESS",
            rows_processed=row_count,
        )

        print(f"Successfully loaded {row_count} orders. job_id={job_id}")

    except Exception as error:
        end_time = datetime.now(UTC)

        log_pipeline_run(
            connection=connection,
            job_id=job_id,
            start_time=start_time,
            end_time=end_time,
            status="FAILED",
            rows_processed=row_count,
            error_message=str(error),
        )

        raise

    finally:
        connection.close()


if __name__ == "__main__":
    run()
