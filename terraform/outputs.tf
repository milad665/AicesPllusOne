output "agent_service_url" {
  value       = google_cloud_run_v2_service.agent_service.uri
  description = "The URL of the deployed Agent service"
}

output "storage_bucket_name" {
  value       = google_storage_bucket.architecture_store.name
  description = "The name of the GCS bucket created"
}

output "secret_id" {
  value = google_secret_manager_secret.api_key.name
  description = "The resource name of the API Key secret (Add version manually)"
}
