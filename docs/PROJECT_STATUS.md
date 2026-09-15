# E-Commerce Data Platform

## 1. Project Overview

Personal end-to-end Data Engineering portfolio project demonstrating production-style data engineering practices.

### Goals

* Build a modular and maintainable Data Engineering platform.
* Practice modern Data Engineering development workflows.
* Demonstrate ingestion, transformation, orchestration, testing, monitoring, CI/CD, and environment management.
* Prepare the project for future cloud deployment on GCP.
* Maintain separate development and production configurations.

### Current Status

**Phase:** Local development environment and CI/CD foundation

**Status:** Core local pipeline is working. GCP deployment is intentionally postponed because the current GCP project does not have an active billing account.

---

# 2. Technology Stack

| Area             | Technology                   |
| ---------------- | ---------------------------- |
| Language         | Python 3.12                  |
| Database         | PostgreSQL 16                |
| Transformation   | dbt                          |
| Orchestration    | Apache Airflow 2.10.4        |
| Containerization | Docker / Docker Compose      |
| Testing          | pytest                       |
| Code Quality     | Ruff                         |
| CI/CD            | GitHub Actions               |
| Version Control  | Git / GitHub                 |
| Configuration    | YAML + environment variables |
| Future Cloud     | GCP                          |
| Future IaC       | Terraform                    |

---

# 3. Current Architecture

```text
CSV
 │
 ▼
Python Ingestion
 │
 ▼
PostgreSQL
 │
 ├── raw
 │    └── orders
 │
 ├── analytics
 │    ├── staging
 │    ├── intermediate
 │    └── marts
 │
 └── monitoring
      └── pipeline_runs
 │
 ▼
dbt
 │
 ├── staging
 ├── intermediate
 └── marts
 │
 ▼
Airflow
 │
 ├── ingest_orders
 ├── dbt_run
 └── dbt_test
```

Development workflow:

```text
feature/*
    │
    ▼
commit
    │
    ▼
push
    │
    ▼
GitHub Pull Request
    │
    ▼
GitHub Actions CI
    │
    ├── Ruff
    └── pytest
    │
    ▼
approval
    │
    ▼
main
```

---

# 4. Project Structure

```text
ecommerce-data-platform/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── src/
│   ├── ingestion/
│   │   └── orders.py
│   │
│   ├── transformation/
│   │
│   └── utils/
│       ├── config.py
│       └── database.py
│
├── tests/
│   ├── unit/
│   │   └── test_ingestion.py
│   │
│   └── integration/
│
├── dags/
│   └── ecommerce_pipeline.py
│
├── dbt/
│   ├── ecommerce/
│   │   ├── models/
│   │   │   ├── staging/
│   │   │   ├── intermediate/
│   │   │   └── marts/
│   │   └── tests/
│   │
│   └── profiles/
│       └── profiles.yml
│
├── config/
│   ├── dev.yaml
│   └── prod.yaml
│
├── infrastructure/
│   └── terraform/
│
├── scripts/
├── notebooks/
├── docs/
│
├── data/
│   └── raw/
│       └── orders.csv
│
├── Dockerfile
├── Dockerfile.airflow
├── docker-compose.yml
├── pyproject.toml
├── .env
├── .env.example
└── .gitignore
```

---

# 5. Local Environment

## Project Directory

Windows:

```powershell
C:\Users\akbar\data-engineering\projects\ecommerce-data-platform
```

Open the project:

```powershell
cd C:\Users\akbar\data-engineering\projects\ecommerce-data-platform
```

Activate Python virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Expected terminal:

```text
(.venv) PS C:\Users\akbar\data-engineering\projects\ecommerce-data-platform>
```

---

# 6. Environment Variables

Local secrets are stored in:

```text
.env
```

`.env` is intentionally excluded from Git.

Example structure:

```env
ENVIRONMENT=dev

DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce
DB_USER=ecommerce
DB_PASSWORD=<local-password>

AIRFLOW_DB_USER=airflow
AIRFLOW_DB_PASSWORD=<local-password>
AIRFLOW_DB_NAME=airflow
```

The repository contains:

```text
.env.example
```

with placeholders only.

Verify `.env` is ignored:

```powershell
git check-ignore .env
```

Expected:

```text
.env
```

Check tracked environment files:

```powershell
git ls-files | Select-String "\.env"
```

Only `.env.example` should be tracked.

**Never commit `.env`.**

---

# 7. Docker Environment

Services:

```text
ecommerce-postgres
ecommerce-airflow
```

Check running containers:

```powershell
docker ps
```

Start services:

```powershell
docker compose up -d
```

Check service status:

```powershell
docker compose ps
```

View Airflow logs:

```powershell
docker logs ecommerce-airflow
```

View PostgreSQL logs:

```powershell
docker logs ecommerce-postgres
```

Stop services:

```powershell
docker compose down
```

## Important

Do **not** use:

```powershell
docker compose down -v
```

unless intentionally deleting Docker volumes.

The PostgreSQL data is stored in the Docker volume:

```text
postgres_data
```

Removing the volume can delete the local database data.

---

# 8. PostgreSQL

Two databases are currently used:

```text
ecommerce
airflow
```

### ecommerce

Application/data database.

Contains:

```text
raw
analytics
monitoring
```

### airflow

Airflow metadata database.

Airflow has been migrated from SQLite to PostgreSQL.

Verify Airflow database connection:

```powershell
docker exec ecommerce-airflow airflow db check
```

Expected:

```text
Connection successful.
```

Check PostgreSQL:

```powershell
docker exec ecommerce-postgres pg_isready -U ecommerce -d ecommerce
```

Expected:

```text
accepting connections
```

---

# 9. Data Pipeline

## Source

Sample data:

```text
data/raw/orders.csv
```

## Python Ingestion

Main ingestion script:

```text
src/ingestion/orders.py
```

Run locally:

```powershell
python src/ingestion/orders.py
```

The ingestion process:

1. Creates `raw` schema if necessary.
2. Creates `raw.orders` if necessary.
3. Reads the CSV.
4. Inserts/updates records.
5. Uses `order_id` as the primary key.
6. Uses `ON CONFLICT` for idempotent ingestion.
7. Generates a `job_id`.
8. Records pipeline execution in `monitoring.pipeline_runs`.

### Idempotency

Running the ingestion multiple times should not create duplicate orders.

The load uses:

```sql
ON CONFLICT (order_id)
DO UPDATE
```

This allows the same source data to be processed repeatedly.

---

# 10. dbt

dbt project:

```text
dbt/ecommerce
```

Local dbt profile:

```text
C:\Users\akbar\.dbt\profiles.yml
```

The local profile connects to:

```text
localhost:5432
```

Airflow's profile is different because Airflow runs inside Docker.

Airflow dbt profile:

```text
dbt/profiles/profiles.yml
```

It connects to the PostgreSQL Docker service:

```text
postgres:5432
```

## dbt Commands

From:

```powershell
cd dbt\ecommerce
```

Check connection:

```powershell
dbt debug
```

Run models:

```powershell
dbt run
```

Run tests:

```powershell
dbt test
```

Run everything:

```powershell
dbt build
```

---

# 11. dbt Data Layers

## Staging

```text
stg_orders
```

Purpose:

* Clean source structure.
* Cast data types.
* Provide a consistent interface to raw data.

Source:

```text
raw.orders
```

## Intermediate

```text
int_orders
```

Purpose:

* Business transformations.
* Derived metrics.

Example:

```text
gross_amount = quantity * unit_price
```

## Mart

```text
fct_orders
```

Purpose:

* Business-facing analytical dataset.
* Excludes cancelled orders.

Current expected result:

```text
raw.orders        = 10 rows
analytics.fct_orders = 9 rows
```

---

# 12. dbt Testing

Current tests include:

### Generic tests

* `order_id` not null
* `order_id` unique

### Singular tests

```text
assert_positive_order_quantity.sql
assert_positive_unit_price.sql
```

Run:

```powershell
dbt test
```

Expected:

```text
PASS
```

---

# 13. Airflow

DAG:

```text
dags/ecommerce_pipeline.py
```

DAG ID:

```text
ecommerce_pipeline
```

Current pipeline:

```text
ingest_orders
      │
      ▼
   dbt_run
      │
      ▼
  dbt_test
```

Airflow runs the same ingestion and transformation flow automatically.

List DAGs:

```powershell
docker exec ecommerce-airflow airflow dags list
```

Check Airflow metadata DB:

```powershell
docker exec ecommerce-airflow airflow db check
```

Check dbt inside Airflow:

```powershell
docker exec ecommerce-airflow dbt --version
```

Airflow UI:

```text
http://localhost:8080
```

---

# 14. Pipeline Monitoring

Monitoring table:

```text
monitoring.pipeline_runs
```

The ingestion process records:

```text
job_id
pipeline_name
start_time
end_time
status
rows_processed
error_message
```

Query recent executions:

```powershell
docker exec ecommerce-postgres psql -U ecommerce -d ecommerce -c "SELECT job_id, pipeline_name, status, rows_processed FROM monitoring.pipeline_runs ORDER BY start_time DESC LIMIT 5;"
```

Expected successful execution:

```text
status = SUCCESS
```

---

# 15. Configuration Management

Configuration files:

```text
config/dev.yaml
config/prod.yaml
```

Environment is selected using:

```env
ENVIRONMENT=dev
```

Python configuration loader:

```text
src/utils/config.py
```

Database connection logic:

```text
src/utils/database.py
```

The application loads environment-specific configuration instead of hardcoding environment-specific settings throughout the code.

Secrets are provided through environment variables.

---

# 16. Testing & Code Quality

Testing framework:

```text
pytest
```

Run:

```powershell
pytest
```

Code quality:

```text
Ruff
```

Run linting:

```powershell
ruff check .
```

Run formatting check:

```powershell
ruff format --check .
```

Format code:

```powershell
ruff format .
```

Auto-fix lint issues where possible:

```powershell
ruff check . --fix
```

---

# 17. GitHub Actions CI

Workflow:

```text
.github/workflows/ci.yml
```

CI currently performs:

```text
Checkout repository
        ↓
Python 3.12
        ↓
Install dependencies
        ↓
Ruff check
        ↓
Ruff format check
        ↓
pytest
```

The workflow runs on:

```text
main
develop
feature/*
```

Pull requests targeting:

```text
main
develop
```

The CI workflow has previously completed successfully on GitHub.

---

# 18. Git Workflow

Branch convention:

```text
feature/<description>
```

Example:

```powershell
git checkout -b feature/new-feature
```

Check status:

```powershell
git status
```

Check branches:

```powershell
git branch -vv
```

Add changes:

```powershell
git add .
```

Commit:

```powershell
git commit -m "type: description"
```

Push:

```powershell
git push -u origin feature/<branch-name>
```

Create a Pull Request on GitHub.

After CI passes and the PR is approved, merge into `main`.

---

# 19. Main Branch Protection

`main` is protected by the GitHub repository ruleset:

```text
Protect main
```

Current intended rules:

* Pull Request required
* 1 approval required
* Dismiss stale approvals
* Required CI status check
* Branch must be up to date
* Block deletion
* Block force pushes

**Block force pushes was temporarily disabled during the Git history cleanup and has now been re-enabled.**

---

# 20. Git Secret Cleanup

A database password had previously been committed to GitHub.

The history was rewritten to remove the exposed password.

Clean history now includes:

```text
8b988dc  chore: secure database configuration
4ee0418  docs: add project overview
e079a21  ci: add automated code quality and tests
dc6ab13  initialize data engineering project
```

The old exposed commits were removed from the active `main` and feature branch histories.

Current repository configuration uses environment variables instead of hardcoded passwords.

**Do not reintroduce credentials into tracked files.**

---

# 21. GCP Status

GCP deployment is currently postponed.

A GCP trial/personal project was available, but bucket creation failed because the project does not currently have an active billing account.

Example command that was attempted:

```powershell
gcloud storage buckets create gs://ecommerce-data-dev --location=asia-southeast2
```

The operation failed because billing was unavailable.

Therefore:

```text
Local development       ✅
Docker                   ✅
PostgreSQL               ✅
dbt                      ✅
Airflow                  ✅
Testing                  ✅
Ruff                     ✅
GitHub Actions            ✅
Git workflow              ✅
GCP infrastructure        ⏸️ postponed
Terraform                 ⏸️ postponed
Cloud deployment          ⏸️ postponed
```

Do not spend time debugging GCP resources until billing is available.

---

# 22. Important Commands Quick Reference

## Start project

```powershell
cd C:\Users\akbar\data-engineering\projects\ecommerce-data-platform
.\.venv\Scripts\Activate.ps1
docker compose up -d
```

## Check containers

```powershell
docker compose ps
docker ps
```

## Run Python ingestion

```powershell
python src/ingestion/orders.py
```

## Run dbt

```powershell
cd dbt\ecommerce
dbt debug
dbt run
dbt test
```

## Run tests

From project root:

```powershell
pytest
ruff check .
ruff format --check .
```

## Check Airflow

```powershell
docker exec ecommerce-airflow airflow db check
docker exec ecommerce-airflow airflow dags list
docker exec ecommerce-airflow dbt --version
```

## PostgreSQL health

```powershell
docker exec ecommerce-postgres pg_isready -U ecommerce -d ecommerce
```

## Check Git

```powershell
git status
git branch -vv
git log --oneline --decorate --all -8
```

## Check secrets are not tracked

```powershell
git ls-files .env
git check-ignore .env
```

---

# 23. Current Known State

The following are intentionally **not completed yet**:

* GCP infrastructure
* Terraform
* Cloud Storage
* BigQuery
* Cloud-based data pipeline
* Production deployment
* GitHub Actions deployment to GCP
* Workload Identity Federation
* DEV/PROD cloud environments
* Data warehouse optimization
* Advanced data quality framework
* Observability/dashboarding
* Incremental dbt models
* CI/CD deployment pipeline

These should be implemented in later phases.

---

# 24. Next Session — Where to Continue

Before starting new development, perform an environment/workflow verification.

### Step 1 — Git

```powershell
git status
git branch -vv
git log --oneline --decorate --all -8
```

Expected:

```text
working tree clean
```

### Step 2 — Secret check

```powershell
git ls-files .env
git check-ignore .env
git ls-files | Select-String "\.env"
```

Expected:

* `.env` is not tracked.
* `.env` is ignored.
* `.env.example` is tracked.

### Step 3 — Docker

```powershell
docker compose ps
docker compose config
```

Do not share the full `docker compose config` output because it may contain resolved credentials.

### Step 4 — PostgreSQL

```powershell
docker exec ecommerce-postgres pg_isready -U ecommerce -d ecommerce
```

### Step 5 — Data

```powershell
docker exec ecommerce-postgres psql -U ecommerce -d ecommerce -c "SELECT COUNT(*) FROM raw.orders;"
```

Expected:

```text
10
```

```powershell
docker exec ecommerce-postgres psql -U ecommerce -d ecommerce -c "SELECT COUNT(*) FROM analytics.fct_orders;"
```

Expected:

```text
9
```

### Step 6 — dbt

```powershell
cd dbt\ecommerce
dbt debug
dbt run
dbt test
```

### Step 7 — Airflow

Open:

```text
http://localhost:8080
```

Trigger:

```text
ecommerce_pipeline
```

Verify:

```text
ingest_orders → dbt_run → dbt_test
```

All tasks should succeed.

### Step 8 — CI

Check GitHub Actions and confirm the latest CI run is successful.

---

# 25. Development Principles

The project should continue following these principles:

1. **No secrets in Git.**
2. **Use environment variables for credentials.**
3. **Keep configuration separate from application logic.**
4. **Make ingestion idempotent.**
5. **Keep raw data separate from transformed data.**
6. **Use dbt for SQL transformations and data tests.**
7. **Use Airflow for orchestration, not business logic.**
8. **Keep Python code modular and reusable.**
9. **Run tests and linting before merging.**
10. **Use Pull Requests for changes to `main`.**
11. **Prefer small, focused commits.**
12. **Avoid destructive Docker commands unless necessary.**
13. **Keep development and production configurations separate.**
14. **Do not introduce cloud dependencies until the local pipeline is stable.**
15. **Build toward reproducible infrastructure and deployment.**

---

# 26. Resume Point

When continuing this project, start with:

```text
Environment & Workflow Verification
        ↓
Confirm local pipeline
        ↓
Confirm Git/GitHub state
        ↓
Confirm Airflow
        ↓
Confirm CI
        ↓
Choose next development phase
```

**Current stopping point:**
Local Data Engineering platform + CI/CD foundation completed. GCP deployment intentionally postponed.
