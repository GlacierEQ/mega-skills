---
name: docker-devops
description: >
  Use when working with Docker, Docker Compose, container management, health checks,
  deployments, CI/CD pipelines, infrastructure automation, Kubernetes, Docker Swarm,
  container orchestration, image building, multi-stage builds, Docker networks, Docker
  volumes, bind mounts, named volumes, container security, vulnerability scanning, secrets
  management, environment variables, container monitoring, log aggregation, resource limits,
  memory constraints, CPU limits, restart policies, container labeling, container profiling,
  service mesh, load balancing, reverse proxy, nginx, traefik, port mapping, port forwarding,
  Docker registry, container registry, GitHub Actions, GitLab CI, Jenkins, Travis CI,
  CircleCI, build automation, test automation, deployment automation, blue-green deployment,
  rolling update, canary deployment, infrastructure as code, terraform, ansible, pulumi,
  cloud deployment, AWS ECS, Google Cloud Run, Azure Container Instances, container
  networking, overlay networks, bridge networks, host networking, container storage,
  persistent volumes, container backups, container recovery, disaster recovery, high
  availability, scaling, auto-scaling, container profiling, performance monitoring,
  Prometheus, Grafana, ELK stack, container forensics, container debugging, or any
  container-based infrastructure and deployment automation.
---

# Docker & DevOps Skill — Container Infrastructure & Deployment

## Keywords
`docker` `docker compose` `container` `health check` `deployment` `ci/cd` `infrastructure`
`kubernetes` `docker swarm` `container orchestration` `image building` `multi-stage build`
`docker network` `docker volume` `bind mount` `named volume` `container security`
`vulnerability scanning` `secrets management` `environment variables` `container monitoring`
`log aggregation` `resource limits` `memory limits` `cpu limits` `restart policy`
`container labeling` `service mesh` `load balancing` `reverse proxy` `nginx` `traefik`
`port mapping` `docker registry` `github actions` `gitlab ci` `jenkins` `build automation`
`test automation` `deployment automation` `blue-green deployment` `rolling update`
`canary deployment` `infrastructure as code` `terraform` `ansible` `pulumi` `cloud deployment`
`aws ecs` `google cloud run` `azure container instances` `container networking` `overlay network`
`bridge network` `persistent volume` `container backup` `disaster recovery` `high availability`
`auto-scaling` `prometheus` `grafana` `elk stack` `container debugging` `dockerfile`
`dockerignore` `compose file` `service definition` `volume definition` `network definition`
`build context` `layer caching` `image optimization` `container runtime` `containerd` `runc`

## Docker Commands

### Container Management
```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Stop container
docker stop <container_id>

# Start container
docker start <container_id>

# Restart container
docker restart <container_id>

# Remove container
docker rm <container_id>

# View logs
docker logs <container_id>
docker logs -f <container_id>  # Follow logs
docker logs --tail 100 <container_id>  # Last 100 lines

# Execute command in container
docker exec -it <container_id> /bin/bash

# Copy files
docker cp <container_id>:/path/to/file /local/path

# Inspect container
docker inspect <container_id>

# Resource usage
docker stats <container_id>
```

### Image Management
```bash
# List images
docker images

# Pull image
docker pull <image:tag>

# Build image
docker build -t <name:tag> .

# Remove image
docker rmi <image_id>

# Tag image
docker tag <image_id> <new_name:tag>

# Push image
docker push <name:tag>

# Save image to tar
docker save <image:tag> > image.tar

# Load image from tar
docker load < image.tar
```

### Docker Compose
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Build services
docker-compose build

# Restart services
docker-compose restart

# View status
docker-compose ps

# Execute in service
docker-compose exec <service> /bin/bash

# Scale service
docker-compose up -d --scale <service>=3
```

## Health Checks

### Container Health
```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' <container>

# View health logs
docker inspect --format='{{.State.Health.Log}}' <container>

# Check ports
docker port <container>

# Check resource usage
docker stats <container>

# Check environment
docker exec <container> env
```

### Service Health
```bash
# HTTP health check
curl -f http://localhost:8080/health || exit 1

# TCP health check
nc -zv localhost 5432

# Check service status
systemctl status <service_name>

# Check container logs for errors
docker logs <container> 2>&1 | grep -i error
```

## Dockerfiles

### Python Application (Multi-stage)
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "app.py"]
```

### Node.js Application
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
```

### Go Application
```dockerfile
FROM golang:1.21-alpine as builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

FROM alpine:latest

WORKDIR /root/

COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]
```

## Docker Compose Files

### Multi-Service Application
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"
    networks:
      - frontend
      - backend

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - backend

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - frontend

networks:
  frontend:
  backend:

volumes:
  postgres_data:
```

## Deployment

### Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml myapp

# List services
docker service ls

# Scale service
docker service scale myapp_app=3

# Update service
docker service update --image myapp:latest myapp_app

# Remove stack
docker stack rm myapp
```

### Kubernetes
```bash
# Apply configuration
kubectl apply -f deployment.yaml

# Get pods
kubectl get pods

# Get services
kubectl get services

# View logs
kubectl logs -f <pod_name>

# Execute in pod
kubectl exec -it <pod_name> -- /bin/bash

# Scale deployment
kubectl scale deployment myapp --replicas=3

# Rollout status
kubectl rollout status deployment/myapp

# Rollback
kubectl rollout undo deployment/myapp
```

## CI/CD

### GitHub Actions
```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .
      
      - name: Run tests
        run: docker run --rm myapp:${{ github.sha }} npm test
      
      - name: Push to registry
        if: github.ref == 'refs/heads/main'
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag myapp:${{ github.sha }} myapp:latest
          docker push myapp:latest
```

## Monitoring

### Resource Usage
```bash
# All containers
docker stats

# Specific container
docker stats <container>

# Disk usage
docker system df

# Clean up
docker system prune -a

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune
```

### Logs
```bash
# View logs
docker logs <container>

# Follow logs
docker logs -f <container>

# Tail logs
docker logs --tail 100 <container>

# Search logs
docker logs <container> 2>&1 | grep "error"

# JSON logs
docker logs <container> 2>&1 | jq .
```

## Networking

### Network Management
```bash
# List networks
docker network ls

# Create network
docker network create mynet

# Connect container
docker network connect mynet <container>

# Disconnect container
docker network disconnect mynet <container>

# Inspect network
docker network inspect mynet
```

### Port Mapping
```bash
# Map port
docker run -p 8080:80 <image>

# Map multiple ports
docker run -p 8080:80 -p 8443:443 <image>

# Map to specific interface
docker run -p 127.0.0.1:8080:80 <image>

# Map UDP port
docker run -p 5353:53/udp <image>
```

## Volumes

### Volume Management
```bash
# List volumes
docker volume ls

# Create volume
docker volume create mydata

# Remove volume
docker volume rm mydata

# Mount volume
docker run -v mydata:/app/data <image>

# Bind mount
docker run -v /host/path:/container/path <image>

# Read-only mount
docker run -v /host/path:/container/path:ro <image>
```

## Security

### Best Practices
```bash
# Scan image for vulnerabilities
docker scan <image>

# Run as non-root user
docker run --user 1000:1000 <image>

# Read-only filesystem
docker run --read-only <image>

# Drop capabilities
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE <image>

# No new privileges
docker run --security-opt=no-new-privileges <image>

# Resource limits
docker run --memory=512m --cpus=1.0 <image>
```

## Integration

### With Quantum Nexus
- Deploy MCP server
- Containerize legal tools
- Health monitoring

### With Aspen Grove
- Deploy connectors
- Container orchestration
- Service mesh

### With Mastermind
- Deploy runtime
- Container health checks
- Resource monitoring

### With Brain
- Deploy brain server
- Monitor intelligence feeds
- Scale decision engine
