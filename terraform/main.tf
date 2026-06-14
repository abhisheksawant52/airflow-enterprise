terraform {
  required_version = ">= 1.5.0"
  required_providers {
    helm       = { source = "hashicorp/helm", version = "~> 2.13" }
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.30" }
  }
}

resource "kubernetes_namespace" "airflow" {
  metadata {
    name = var.namespace
    labels = { "app.kubernetes.io/managed-by" = "terraform" }
  }
}

resource "helm_release" "airflow" {
  name       = "airflow"
  repository = "https://airflow.apache.org"
  chart      = "airflow"
  version    = var.chart_version
  namespace  = kubernetes_namespace.airflow.metadata[0].name
  timeout    = 600

  set { name = "executor", value = var.executor }
  set { name = "webserver.service.type", value = "LoadBalancer" }
  set { name = "webserver.defaultUser.enabled", value = "true" }
  set { name = "webserver.defaultUser.username", value = "admin" }
  set { name = "webserver.defaultUser.password", value = var.admin_password }
  set { name = "dags.persistence.enabled", value = "true" }
  set { name = "dags.persistence.size", value = "5Gi" }
  set { name = "logs.persistence.enabled", value = "true" }
  set { name = "logs.persistence.size", value = "10Gi" }

  depends_on = [kubernetes_namespace.airflow]
}
