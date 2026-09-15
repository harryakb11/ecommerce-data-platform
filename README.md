# E-commerce Data Platform

End-to-end data engineering portfolio project demonstrating:

- Python data ingestion
- PostgreSQL
- dbt
- Apache Airflow
- Docker
- pytest
- Ruff
- GitHub Actions
- Environment-based configuration

## Pipeline

CSV
→ Python ingestion
→ PostgreSQL raw
→ dbt staging
→ dbt intermediate
→ dbt mart
→ Airflow orchestration

## Development Workflow

feature branch
→ Pull Request
→ GitHub Actions CI
→ main