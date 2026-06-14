variable "namespace" { type = string; default = "airflow"; description = "Kubernetes namespace for Airflow" }
variable "chart_version" { type = string; default = "1.14.0"; description = "Apache Airflow Helm chart version" }
variable "executor" { type = string; default = "KubernetesExecutor"; description = "Airflow executor type" }
variable "admin_password" { type = string; default = "airflow123"; description = "Admin UI password"; sensitive = true }
