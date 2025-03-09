# Metrics Collection Setup

This document outlines the setup and configuration of metrics collection using Prometheus in our environment.

## Table of Contents
- [Prometheus Setup](#prometheus-setup)
- [Service Configurations](#service-configurations)
- [Dashboard Setup](#dashboard-setup)
- [Metrics Gathering](#metrics-gathering)

## Prometheus Setup

### Overview
Prometheus is an open-source systems monitoring and alerting toolkit that collects and stores time-series data. In our setup, we've configured Prometheus to scrape metrics from various services in our environment.

### Configuration
The Prometheus configuration file (`prometheus.yml`) is set up to scrape metrics from the following services:
- Prometheus itself
- Loki
- Python Flask application
- Docker containers
- Promtail
- Grafana

### Docker Compose Integration
We've added Prometheus to our Docker Compose setup with the following configuration:
```yaml
prometheus:
  image: prom/prometheus:v2.43.0
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--web.console.libraries=/usr/share/prometheus/console_libraries'
    - '--web.console.templates=/usr/share/prometheus/consoles'
  networks:
    - logging-network
  deploy:
    resources:
      limits:
        memory: 512M
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```


## Service Configurations

### Memory Limits
We've configured memory limits for all services to ensure proper resource allocation:
- Loki: 512MB
- Promtail: 256MB
- Grafana: 512MB
- Python App: 256MB
- Demo App (Nginx): 128MB
- Prometheus: 512MB

### Log Rotation
All services have been configured with log rotation to prevent disk space issues:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

This configuration ensures that:
- Logs are rotated when they reach 10MB in size
- A maximum of 3 log files are kept per service

## Dashboard Setup

### Prometheus Data Source
We've added Prometheus as a data source in Grafana with the following configuration:
```yaml
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    version: 1
    editable: true
    isDefault: false
```


## Metrics Gathering

### Python Application Metrics
We've instrumented the Python Flask application to expose Prometheus metrics. The following metrics are collected:
- `app_index_request_count`: Counter for requests to the index page
- `app_health_request_count`: Counter for requests to the health endpoint
- `app_error_count`: Counter for errors, with labels for error types
- `app_request_latency_seconds`: Histogram for request latency, with labels for endpoints

The metrics are accessible at the `/metrics` endpoint of the application (http://localhost:5001/metrics).

You can generate traffic to see the metrics in action by running:
```bash
# Generate index page requests
for i in {1..10}; do curl -s http://localhost:5001/ > /dev/null; done

# Generate health check requests
for i in {1..5}; do curl -s http://localhost:5001/health > /dev/null; done

# Generate 404 errors
curl -s http://localhost:5001/nonexistent > /dev/null
```

### Service Metrics
Prometheus is configured to collect metrics from all services in our environment, providing visibility into:
- Container health and resource usage
- Application performance and request statistics
- Error rates and status codes
- System-level metrics for each container

## Conclusion

We've successfully set up a comprehensive monitoring solution with Prometheus for metrics collection and Grafana for visualization. This setup allows us to monitor the health and performance of all our services in real-time.

The combination of Prometheus for metrics and Loki for logs provides a complete observability solution for our application stack. 

## Screenshots

### Grafana Dashboards

![Screenshot 1](screenshots/Screenshot%202025-03-09%20at%2022.28.37.png)
![Screenshot 2](screenshots/Screenshot%202025-03-09%20at%2022.28.41.png)
![Screenshot 3](screenshots/Screenshot%202025-03-09%20at%2022.32.25.png)
![Screenshot 4](screenshots/Screenshot%202025-03-09%20at%2022.32.40.png)
![Screenshot 5](screenshots/Screenshot%202025-03-09%20at%2022.51.54.png)
![Screenshot 6](screenshots/Screenshot%202025-03-09%20at%2022.51.58.png)


### Prometheus Targets

![Screenshot 7](screenshots/Screenshot%202025-03-09%20at%2023.11.05.png)
![Screenshot 8](screenshots/Screenshot%202025-03-09%20at%2023.11.13.png)