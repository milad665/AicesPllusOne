terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable necessary APIs
resource "google_project_service" "cloudrun" {
  service = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager" {
  service = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifactregistry" {
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "aices-repo"
  description   = "Aices Plus One Docker Repository"
  format        = "DOCKER"
  depends_on    = [google_project_service.artifactregistry]
}

# 1. Cloud Storage Bucket for Architecture Data
resource "google_storage_bucket" "architecture_store" {
  name          = "aices-plus-one-storage-${var.project_id}"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true
  
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# 2. Secret for API Key
resource "google_secret_manager_secret" "api_key" {
  secret_id = "aices-plus-one-gemini-key"
  replication {
    auto {}
  }
  depends_on = [google_project_service.secretmanager]
}

# Note: We create the secret, but the value must be added manually or via a separate process
# to avoid storing it in Terraform state.

# 3. Service Account for Cloud Run
resource "google_service_account" "agent_sa" {
  account_id   = "aices-agent-sa"
  display_name = "Aices Plus One Agent Service Account"
}

# 4. Cloud Run Service (Agent)
resource "google_cloud_run_v2_service" "agent_service" {
  name     = "aices-plus-one-agent"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.agent_sa.email

    containers {
      image = var.agent_image
      
      ports {
        container_port = 8001
      }

      env {
        name  = "STORAGE_TYPE"
        value = "gcs"
      }
      
      env {
        name  = "GCS_BUCKET_NAME"
        value = google_storage_bucket.architecture_store.name
      }
      
      env {
        name  = "RUN_MODE"
        value = "api"
      }
      
      env {
        name = "GOOGLE_API_KEY"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.api_key.secret_id
            version = "latest"
          }
        }
      }
      
      resources {
        limits = {
          cpu    = "1000m"
          memory = "1Gi"
        }
      }
    }
  }

  depends_on = [google_project_service.cloudrun]
}

# Allow unauthenticated access to the Agent (Public Web UI)
# In production, you might want to restrict this or use IAP
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.agent_service.location
  service  = google_cloud_run_v2_service.agent_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
