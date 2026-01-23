variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "The Google Cloud region to deploy to"
  type        = string
  default     = "us-central1"
}

variable "agent_image" {
  description = "The container image URL for the Aices Plus One Agent"
  type        = string
  default     = "gcr.io/myp-project/aices-plus-one-agent:latest" 
}
