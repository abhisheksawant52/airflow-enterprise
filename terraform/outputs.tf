output "namespace" { value = kubernetes_namespace.airflow.metadata[0].name }
output "release_name" { value = helm_release.airflow.name }
output "port_forward_command" { value = "kubectl port-forward svc/airflow-webserver 8080:8080 -n ${var.namespace}" }
output "access_url" { value = "http://localhost:8080 (after port-forward) - login: admin / ${var.admin_password}" }
