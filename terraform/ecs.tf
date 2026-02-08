# ecs.tf - ECS Cluster, Task Definition, Service

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/fastapi-app"
  retention_in_days = 7

  tags = {
    Name = "fastapi-app-logs"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "fastapi-cluster"

  setting {
    name  = "containerInsights"
    value = "disabled"
  }

  tags = {
    Name = "fastapi-cluster"
  }
}

# Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "fastapi-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    # App
    {
      name      = "app"
      image     = "229828754047.dkr.ecr.eu-west-2.amazonaws.com/fastapi-nginx:latest"
      essential = true
      portMappings = [
        {
          containerPort = 80
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "REDIS_URL", value = "redis://localhost:6379/0" },
        { name = "DATABASE_URL", value = "postgresql+psycopg://app:app@localhost:5432/app" },
        { name = "JWT_SECRET", value = "change-me-in-production" },
        { name = "REFRESH_COOKIE_SECURE", value = "true" },
        { name = "REFRESH_COOKIE_SAMESITE", value = "lax" },
        { name = "ALLOWED_ORIGINS", value = "https://web.jensending.top" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/fastapi-app"
          "awslogs-region"        = "eu-west-2"
          "awslogs-stream-prefix" = "app"
        }
      }
      dependsOn = [
        { containerName = "valkey", condition = "START" },
        { containerName = "postgres", condition = "START" }
      ]
    },

    # Valkey
    {
      name      = "valkey"
      image     = "valkey/valkey:8"
      essential = true
      portMappings = [
        {
          containerPort = 6379
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/fastapi-app"
          "awslogs-region"        = "eu-west-2"
          "awslogs-stream-prefix" = "valkey"
        }
      }
    },
    # Postgres
    {
      name      = "postgres"
      image     = "postgres:16"
      essential = true
      portMappings = [
        {
          containerPort = 5432
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "POSTGRES_USER", value = "app" },
        { name = "POSTGRES_PASSWORD", value = "app" },
        { name = "POSTGRES_DB", value = "app" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/fastapi-app"
          "awslogs-region"        = "eu-west-2"
          "awslogs-stream-prefix" = "postgres"
        }
      }
    }
  ])

  tags = {
    Name = "fastapi-app-task"
  }
}

resource "aws_ecs_service" "app" {
  name            = "fastapi-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 80
  }

  depends_on = [aws_lb_listener.https]

  tags = {
    Name = "fastapi-service"
  }
}