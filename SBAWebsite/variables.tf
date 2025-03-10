variable "resource_group" {
  default = "wbensoltanaRG"
}

variable "location" {
  default = "francecentral"
}

variable "acr_name" {
  default = "wbensoltanaregistry"
}

variable "container_name" {
  default = "djangoazure-container"
}

variable "image_name" {
  default = "djangoazure"
}

variable "dns_label" {
  default = "djangoazure"
}

variable "cpu" {
  default = 2
}

variable "memory" {
  default = 4
}

variable "port" {
  default = 8001
}
