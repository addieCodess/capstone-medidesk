variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "medidesk-eks"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}
