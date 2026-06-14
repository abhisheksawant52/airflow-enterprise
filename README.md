# Airflow Enterprise

Production-ready **Apache Airflow** deployment for enterprise data pipelines. Includes DAGs, Docker Compose local dev setup, Kubernetes/Helm production deployment via Terraform, and CI validation.

## Quick Start (Local)

```bash
git clone https://github.com/abhisheksawant52/airflow-enterprise.git
cd airflow-enterprise

# Start all services
docker compose up airflow-init
docker compose up -d

# Open UI
open http://localhost:8080
# Login: admin / admin
```

## What's Included

- **ETL Pipeline DAG** - extract, validate, transform, load with branching and retries
- **Data Quality DAG** - row count, null checks, freshness validation
- **Docker Compose** - local dev environment (Airflow + PostgreSQL)
- **Terraform** - deploy Airflow to Kubernetes via official Helm chart
- **GitHub Actions** - DAG syntax validation and linting on every push

## Production Deploy (Kubernetes)

```bash
cd terraform
terraform init
terraform apply -var="admin_password=<secure-password>"

# Access UI
terraform output port_forward_command
# Run the command, then open http://localhost:8080
```

## Adding DAGs

Add `.py` files to `src/dags/`. They are automatically picked up by Airflow.

## GitHub Actions

Validates all DAGs on push to `src/dags/`. No secrets required for linting.

## Cleanup

```bash
docker compose down -v          # local
cd terraform && terraform destroy  # Kubernetes
```
