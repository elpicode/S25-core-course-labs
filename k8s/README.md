# Kubernetes Deployment Documentation

This directory contains the Kubernetes manifests for deploying our web application.

## Structure

- `deployment.yml`: Contains the deployment configuration with 3 replicas of nginx:alpine
- `service.yml`: Contains the service configuration to expose the application

## Current Deployment Status

```bash
$ kubectl get pods,svc
NAME                           READY   STATUS              RESTARTS   AGE
pod/web-app-559f47cd7d-7kg4t   1/1     Running             0          3m12s
pod/web-app-559f47cd7d-cjghl   0/1     ContainerCreating   0          3m12s
pod/web-app-559f47cd7d-qqwzx   1/1     Running             0          3m12s

NAME                      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/kubernetes        ClusterIP   10.96.0.1      <none>        443/TCP        25m
service/web-app-service   NodePort    10.97.23.108   <none>        80:30406/TCP   7m45s
```

## Service Information

The application is exposed through a NodePort service:
- Service Name: web-app-service
- Internal Port: 80
- NodePort: 30406
- Cluster IP: 10.97.23.108

To access the application, use:
```bash
minikube service web-app-service
```

## Deployment Steps

1. Apply the deployment:
```bash
kubectl apply -f deployment.yml
```

2. Apply the service:
```bash
kubectl apply -f service.yml
```

3. Check the status:
```bash
kubectl get pods,svc
```

4. Access the application:
```bash
minikube service web-app-service
```

## Cleanup

To remove the deployment and service:
```bash
kubectl delete -f deployment.yml
kubectl delete -f service.yml
```

## Notes

- The deployment uses the `nginx:alpine` image for a smaller footprint and faster pull times
- Three replicas are maintained for high availability
- The service is exposed via NodePort for external access
- Resource limits are set to ensure proper resource allocation:
  - Memory: 128Mi limit, 64Mi request
  - CPU: 500m limit, 250m request 

  ## Screenshots

  ![Screenshot 1](screenshots/Screenshot%202025-03-10%20at%2000.25.42.png)
  ![Screenshot 2](screenshots/Screenshot%202025-03-10%20at%2000.26.18.png)