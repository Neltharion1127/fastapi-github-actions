# FastAPI Production-Style Deployment on AWS

A minimal FastAPI service deployed using a **production-style AWS architecture**, focusing on **network isolation, secure ingress, and reproducible delivery** rather than application complexity.

This repository demonstrates how a simple API can be deployed and operated with realistic infrastructure choices commonly used in industry.

---

## Overview

This project implements a publicly accessible FastAPI service running on **AWS ECS Fargate**, fronted by an **Application Load Balancer (ALB)** with HTTPS enabled via **AWS Certificate Manager (ACM)**.

The system is intentionally small in scope, but designed to reflect **real-world cloud deployment patterns**, including private networking, health checks, and CI-based image delivery.

**Live endpoint:**  
https://api.jensending.top
https://web.jensending.top

The service is designed to be operationally lightweight and may be brought online as needed for demonstrations or validation, while preserving the full deployment setup.

A minimal frontend client is also used alongside this API to demonstrate end-to-end usage (e.g., login and authenticated requests). See the **Frontend** section below for where to view it.

---

## Architecture Summary

High-level request flow:

```
Client
  → Cloudflare DNS
  → AWS Application Load Balancer (HTTPS)
  → Target Group (HTTP, health-checked)
  → ECS Fargate task
      ├── FastAPI + Nginx (app container)
      ├── Valkey (Redis-compatible cache)
      └── PostgreSQL (database)
```

### Multi-Container ECS Task

All three containers run in the **same ECS task**, sharing `localhost` for inter-container communication:

| Container | Port | Purpose                       |
| --------- | ---- | ----------------------------- |
| app       | 80   | FastAPI + Nginx reverse proxy |
| valkey    | 6379 | Session/cache storage         |
| postgres  | 5432 | Application database          |

### Key Architecture Decisions

- **TLS termination at ALB**  
  HTTPS is terminated at the load balancer using ACM, keeping containers simple.

- **Public subnets with Public IP**  
  ECS tasks run in public subnets with public IP for direct internet access. Inbound traffic is still restricted to ALB only via security groups.

- **Fargate Spot (~70% cost savings)**  
  Uses spare AWS capacity at significant discount. Trade-off: tasks may be interrupted with 2-minute warning.

- **ARM64 architecture (~20% cost savings)**  
  Graviton processors are cheaper than x86. Images are built on Mac M-series and pushed to ECR.

- **Health-based routing**  
  ALB forwards traffic only to healthy targets using HTTP health checks.

- **Infrastructure as Code**  
  All AWS resources are managed via Terraform.

---

## Cost Optimization & Trade-offs

### Current Monthly Estimate: ~$29/month

| Component                    | Cost | Notes                             |
| ---------------------------- | ---- | --------------------------------- |
| Fargate Spot (0.5 vCPU, 1GB) | ~$4  | ARM64, 70% cheaper than On-Demand |
| ALB                          | ~$24 | Fixed cost + LCU                  |
| CloudWatch, ECR, etc.        | ~$1  | Minimal usage                     |

### Design Trade-offs

| Choice               | Benefit                   | Trade-off                                                |
| -------------------- | ------------------------- | -------------------------------------------------------- |
| **Public subnets**   | No VPC Endpoints needed   | ECS tasks have public IPs (mitigated by security groups) |
| **Fargate Spot**     | 70% compute savings       | Tasks may be interrupted (2-min warning)                 |
| **In-task Postgres** | Simple setup, no RDS cost | Data lost on restart (acceptable for demo)               |
| **1GB memory**       | Lower cost                | May OOM under heavy load                                 |

---

## AWS Components Used

- **Networking**
  - VPC with public and private subnets (multi-AZ)
  - Internet Gateway
  - S3 Gateway Endpoint (free, speeds up ECR pulls)

- **Compute**
  - ECS Fargate Spot (ARM64)
  - 3 containers per task (app, valkey, postgres)

- **Load Balancing**
  - Application Load Balancer
  - Target Group (IP mode, health-checked)

- **Security**
  - Security Groups (ALB → ECS only)
  - ECS tasks have public IPs but restricted inbound

- **Container Registry**
  - Amazon ECR

- **Observability**
  - CloudWatch Logs (7-day retention)

---

## Terraform

Infrastructure is defined in the `terraform/` directory:

```
terraform/
├── main.tf              # Provider configuration
├── vpc.tf               # VPC, subnets, route tables
├── endpoints.tf         # S3 Gateway Endpoint
├── security-groups.tf   # ALB and ECS security groups
├── alb.tf               # Application Load Balancer
├── iam.tf               # IAM roles for ECS
├── ecs.tf               # Cluster, task definition, service
└── output.tf            # Outputs (ALB DNS, etc.)
```

### Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## Continuous Integration & Delivery

This repository includes a **GitHub Actions pipeline** used for delivery rather than infrastructure provisioning.

### CI / CD Flow

1. Run tests and linting:
   - `pytest`
   - `ruff`
2. Build Docker image
3. Push image to Amazon ECR using **GitHub Actions OIDC**
4. Deploy updated image via ECS service rollout

The pipeline avoids long-lived AWS credentials by assuming an IAM role via OIDC.

---

## Application Endpoints

| Method | Path       | Description          |
| ------ | ---------- | -------------------- |
| GET    | `/health`  | ALB health check     |
| GET    | `/ready`   | Dependency readiness |
| GET    | `/hello`   | Example API endpoint |
| GET    | `/metrics` | In-process metrics   |

---

## Running Locally

### Option 1: Docker Compose (recommended)

```bash
docker-compose up --build
```

This starts all three containers (app, valkey, postgres) locally.

### Option 2: Direct Python

```bash
pip install uv
uv sync

# Start dependencies
docker-compose up valkey postgres -d

# Run app
uv run uvicorn app.main:app --reload
```

---

## Project Scope

This project is **not** intended to be a feature-rich application.

Its purpose is to demonstrate:

- Realistic AWS networking patterns
- Secure ingress with HTTPS
- Multi-container ECS Fargate tasks
- CI-driven image delivery
- Cost-conscious deployment (Fargate Spot, public subnets, ARM64)
- Infrastructure as Code with Terraform

The emphasis is on **system design, operational clarity, and cost optimization**.

---

## Frontend

This backend can be paired with a small frontend client to demonstrate end-to-end flows.

- Frontend repository: https://github.com/Neltharion1127/fastapi-frontend-github-actions
- Live demo (if running): https://web.jensending.top

The frontend is intentionally simple and exists only to showcase how the API is consumed from a browser client.

---

## License

MIT