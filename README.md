# FastAPI Production-Style Deployment on AWS

A minimal FastAPI service deployed using a **production-style AWS architecture**, focusing on **network isolation, secure ingress, and reproducible delivery** rather than application complexity.

This repository demonstrates how a simple API can be deployed and operated with realistic infrastructure choices commonly used in industry.

---

## Overview

This project implements a publicly accessible FastAPI service running on **AWS ECS Fargate**, fronted by an **Application Load Balancer (ALB)** with HTTPS enabled via **AWS Certificate Manager (ACM)**.

The system is intentionally small in scope, but designed to reflect **real-world cloud deployment patterns**, including private networking, health checks, and CI-based image delivery.

**Live endpoint:**  
https://api.jensending.top

The service is designed to be operationally lightweight and may be brought online as needed for demonstrations or validation, while preserving the full deployment setup.

---

## Architecture Summary

High-level request flow:

```
Client
  → Cloudflare DNS
  → AWS Application Load Balancer (HTTPS)
  → Target Group (HTTP, health-checked)
  → ECS Fargate task (FastAPI)
```

### Key Architecture Decisions

- **TLS termination at ALB**  
  HTTPS is terminated at the load balancer using ACM, keeping containers simple and avoiding certificate management inside ECS.

- **Private subnets for application workloads**  
  ECS tasks run without public IPs. Inbound traffic is only allowed from the ALB.

- **Explicit ingress / egress separation**  
  Public access is handled by the ALB, while outbound access from private subnets is provided via a NAT Gateway.

- **Health-based routing**  
  ALB forwards traffic only to healthy targets using HTTP health checks.

---

## AWS Components Used

- **Networking**
  - VPC with public and private subnets (multi-AZ)
  - Internet Gateway (ingress for ALB)
  - NAT Gateway (egress for ECS tasks)

- **Compute**
  - ECS Fargate
  - ECS Service with rolling deployments

- **Load Balancing**
  - Application Load Balancer
  - Target Group (IP mode)

- **Security**
  - Security Groups with least-privilege rules
  - No public IPs on application containers

- **Container Registry**
  - Amazon ECR

- **Observability**
  - CloudWatch Logs via `awslogs` driver

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
|--------|------------|----------------------|
| GET    | `/health`  | ALB health check     |
| GET    | `/hello`   | Example API endpoint |
| GET    | `/metrics` | In-process metrics   |

---

## Running Locally

```bash
pip install uv
uv sync
uv run uvicorn app.main:app --reload
```

---

## Project Scope

This project is **not** intended to be a feature-rich application.

Its purpose is to demonstrate:

- Realistic AWS networking patterns
- Secure ingress with HTTPS
- Containerized workloads on ECS Fargate
- CI-driven image delivery
- Cost-aware deployment decisions

The emphasis is on **system design and operational clarity**, rather than application logic.

---

## Notes on Cost Management

---

## License

MIT