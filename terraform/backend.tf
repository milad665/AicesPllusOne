terraform {
  backend "gcs" {
    bucket  = "aices-plus-one-terraform-state"
    prefix  = "terraform/state"
  }
}
