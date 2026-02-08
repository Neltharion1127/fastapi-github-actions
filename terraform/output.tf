output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}
output "alb_zone_id" {
  description = "ALB Zone ID (for Route53)"
  value       = aws_lb.main.zone_id
}
output "ecs_cluster_name" {
  description = "ECS Cluster name"
  value       = aws_ecs_cluster.main.name
}
output "ecs_service_name" {
  description = "ECS Service name"
  value       = aws_ecs_service.app.name
}