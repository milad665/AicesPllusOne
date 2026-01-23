# Grant Access to Secret Manager (to read API Key)
resource "google_secret_manager_secret_iam_member" "agent_secret_access" {
  secret_id = google_secret_manager_secret.api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_sa.email}"
}

# Grant Access to Storage Bucket (to read/write architecture data)
resource "google_storage_bucket_iam_member" "agent_storage_access" {
  bucket = google_storage_bucket.architecture_store.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.agent_sa.email}"
}
