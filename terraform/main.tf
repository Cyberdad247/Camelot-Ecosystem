# CAMELOT-OS Infrastructure-as-Code
# Terraform configuration for AWS/GCP multi-region deployment
# Supports both Docker-free (QR Pill) and Kubernetes deployments

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "camelot-terraform-state"
    key            = "camelot-os/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CAMELOT-OS"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Date        = formatdate("YYYY-MM-DD", timestamp())
    }
  }
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

# ── Variables ────────────────────────────────────────────────────────────

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "gcp_project" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "cluster_size" {
  description = "Number of CAMELOT-OS instances"
  type        = number
  default     = 3
}

variable "instance_type" {
  description = "Compute instance type"
  type        = string
  default     = "t3.2xlarge"
}

variable "enable_kubernetes" {
  description = "Enable Kubernetes (true) or use QR Pill orchestration (false)"
  type        = bool
  default     = false
}

variable "qr_pill_mode" {
  description = "QR Pill deployment mode: systemd, bare-metal, or custom"
  type        = string
  default     = "systemd"
}

# ── AWS VPC & Networking ─────────────────────────────────────────────────

resource "aws_vpc" "camelot" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "camelot-vpc"
  }
}

resource "aws_internet_gateway" "camelot" {
  vpc_id = aws_vpc.camelot.id

  tags = {
    Name = "camelot-igw"
  }
}

resource "aws_subnet" "camelot_primary" {
  vpc_id                  = aws_vpc.camelot.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "camelot-subnet-1"
  }
}

resource "aws_subnet" "camelot_secondary" {
  vpc_id                  = aws_vpc.camelot.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true

  tags = {
    Name = "camelot-subnet-2"
  }
}

resource "aws_subnet" "camelot_tertiary" {
  vpc_id                  = aws_vpc.camelot.id
  cidr_block              = "10.0.3.0/24"
  availability_zone       = "${var.aws_region}c"
  map_public_ip_on_launch = true

  tags = {
    Name = "camelot-subnet-3"
  }
}

resource "aws_route_table" "camelot" {
  vpc_id = aws_vpc.camelot.id

  route {
    cidr_block      = "0.0.0.0/0"
    gateway_id      = aws_internet_gateway.camelot.id
  }

  tags = {
    Name = "camelot-rt"
  }
}

resource "aws_route_table_association" "camelot_1" {
  subnet_id      = aws_subnet.camelot_primary.id
  route_table_id = aws_route_table.camelot.id
}

resource "aws_route_table_association" "camelot_2" {
  subnet_id      = aws_subnet.camelot_secondary.id
  route_table_id = aws_route_table.camelot.id
}

resource "aws_route_table_association" "camelot_3" {
  subnet_id      = aws_subnet.camelot_tertiary.id
  route_table_id = aws_route_table.camelot.id
}

# ── Security Groups ──────────────────────────────────────────────────────

resource "aws_security_group" "camelot_nodes" {
  name        = "camelot-nodes"
  description = "Security group for CAMELOT-OS nodes"
  vpc_id      = aws_vpc.camelot.id

  # Consensus port
  ingress {
    from_port   = 8443
    to_port     = 8443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
    description = "Consensus"
  }

  # Agent network
  ingress {
    from_port   = 8400
    to_port     = 8410
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
    description = "Agent network"
  }

  # Metrics
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
    description = "Prometheus metrics"
  }

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "camelot-nodes"
  }
}

resource "aws_security_group" "camelot_storage" {
  name        = "camelot-storage"
  description = "Security group for Redis/Qdrant"
  vpc_id      = aws_vpc.camelot.id

  # Redis
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.camelot_nodes.id]
    description     = "Redis"
  }

  # Qdrant
  ingress {
    from_port       = 6333
    to_port         = 6333
    protocol        = "tcp"
    security_groups = [aws_security_group.camelot_nodes.id]
    description     = "Qdrant"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "camelot-storage"
  }
}

# ── EC2 Instances (QR Pill Orchestration) ────────────────────────────────

resource "aws_instance" "camelot_node" {
  count                = var.cluster_size
  ami                  = data.aws_ami.ubuntu.id
  instance_type        = var.instance_type
  key_name             = aws_key_pair.camelot.key_name
  iam_instance_profile = aws_iam_instance_profile.camelot_node.name

  vpc_security_group_ids = [
    aws_security_group.camelot_nodes.id,
    aws_security_group.camelot_storage.id,
  ]

  subnet_id = count.index == 0 ? aws_subnet.camelot_primary.id : (
    count.index == 1 ? aws_subnet.camelot_secondary.id : aws_subnet.camelot_tertiary.id
  )

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 100
    delete_on_termination = true
    encrypted             = true
  }

  # Deploy CAMELOT-OS via QR Pill
  user_data = base64encode(templatefile("${path.module}/scripts/qr_pill_deploy.sh", {
    node_id           = "node_${count.index + 1}"
    cluster_nodes     = join(",", aws_instance.camelot_node[*].private_ip)
    environment       = var.environment
    qr_pill_mode      = var.qr_pill_mode
    metrics_enabled   = true
  }))

  tags = {
    Name = "camelot-node-${count.index + 1}"
    Role = "camelot-instance"
  }

  depends_on = [
    aws_internet_gateway.camelot
  ]
}

# ── ElastiCache Redis Cluster ────────────────────────────────────────────

resource "aws_elasticache_subnet_group" "camelot" {
  name       = "camelot-redis-subnet"
  subnet_ids = [
    aws_subnet.camelot_primary.id,
    aws_subnet.camelot_secondary.id,
    aws_subnet.camelot_tertiary.id,
  ]
}

resource "aws_elasticache_replication_group" "camelot" {
  replication_group_description = "CAMELOT-OS Redis Cluster (L1)"
  engine                         = "redis"
  engine_version                 = "7.0"
  node_type                      = "cache.r6g.xlarge"
  num_cache_clusters             = 3
  automatic_failover_enabled     = true
  multi_az_enabled               = true
  port                           = 6379

  parameter_group_name = aws_elasticache_parameter_group.camelot.name
  subnet_group_name    = aws_elasticache_subnet_group.camelot.name
  security_group_ids   = [aws_security_group.camelot_storage.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  backup_retention_days = 30
  backup_window         = "03:00-05:00"
  maintenance_window    = "sun:05:00-sun:06:00"

  auto_minor_version_upgrade = true
  notification_topic_arn     = aws_sns_topic.camelot_alerts.arn

  tags = {
    Name = "camelot-redis-cluster"
  }
}

resource "aws_elasticache_parameter_group" "camelot" {
  family = "redis7"
  name   = "camelot-redis-params"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "timeout"
    value = "300"
  }
}

# ── GCP Memorystore (Alternative Redis) ──────────────────────────────────

resource "google_redis_instance" "camelot" {
  count           = var.gcp_project != "" ? 1 : 0
  name            = "camelot-redis"
  tier            = "STANDARD_HA"
  memory_size_gb  = 50
  redis_version   = "7.0"
  region          = var.gcp_region

  authorized_network = google_compute_network.camelot[0].id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  backup_configuration {
    start_time = "03:00"
  }
}

resource "google_compute_network" "camelot" {
  count                   = var.gcp_project != "" ? 1 : 0
  name                    = "camelot-network"
  auto_create_subnetworks = false
}

# ── Qdrant Vector Database (GCP) ─────────────────────────────────────────

resource "google_compute_instance_group_manager" "qdrant" {
  count              = var.gcp_project != "" ? 1 : 0
  name               = "camelot-qdrant-group"
  base_instance_name = "camelot-qdrant"
  zone               = "${var.gcp_region}-a"
  target_size        = 3

  version {
    instance_template = google_compute_instance_template.qdrant[0].id
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.qdrant[0].id
    initial_delay_sec = 300
  }
}

resource "google_compute_instance_template" "qdrant" {
  count             = var.gcp_project != "" ? 1 : 0
  name_prefix       = "camelot-qdrant-"
  machine_type      = "n1-standard-4"
  can_ip_forward    = false

  disk {
    source_image = "debian-cloud/debian-11"
    disk_size_gb = 100
  }

  network_interface {
    network = google_compute_network.camelot[0].name
  }

  service_account {
    scopes = ["cloud-platform"]
  }
}

resource "google_compute_health_check" "qdrant" {
  count = var.gcp_project != "" ? 1 : 0
  name  = "camelot-qdrant-health"

  http_health_check {
    port = 6333
  }
}

# ── SNS Topic for Alerts ─────────────────────────────────────────────────

resource "aws_sns_topic" "camelot_alerts" {
  name              = "camelot-alerts"
  kms_master_key_id = "alias/aws/sns"

  tags = {
    Name = "camelot-alerts"
  }
}

resource "aws_sns_topic_subscription" "camelot_ops" {
  topic_arn = aws_sns_topic.camelot_alerts.arn
  protocol  = "email"
  endpoint  = "ops@company.com"
}

# ── IAM Roles & Policies ─────────────────────────────────────────────────

resource "aws_iam_role" "camelot_node" {
  name = "camelot-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "camelot_node" {
  name   = "camelot-node-policy"
  role   = aws_iam_role.camelot_node.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::camelot-backups",
          "arn:aws:s3:::camelot-backups/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "arn:aws:secretsmanager:${var.aws_region}:*:secret:camelot/*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.camelot_alerts.arn
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "camelot_node" {
  name = "camelot-node-profile"
  role = aws_iam_role.camelot_node.name
}

# ── SSH Key Pair ─────────────────────────────────────────────────────────

resource "aws_key_pair" "camelot" {
  key_name   = "camelot-deploy-key"
  public_key = file("~/.ssh/camelot_deploy.pub")
}

# ── Data Sources ─────────────────────────────────────────────────────────

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ── Outputs ──────────────────────────────────────────────────────────────

output "instance_ips" {
  description = "Private IPs of CAMELOT-OS instances"
  value       = aws_instance.camelot_node[*].private_ip
}

output "instance_public_ips" {
  description = "Public IPs of CAMELOT-OS instances"
  value       = aws_instance.camelot_node[*].public_ip
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = var.gcp_project != "" ? null : aws_elasticache_replication_group.camelot.primary_endpoint_address
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.camelot.id
}

output "deployment_mode" {
  description = "Deployment mode (Kubernetes or QR Pill)"
  value       = var.enable_kubernetes ? "Kubernetes" : "QR Pill (${var.qr_pill_mode})"
}
