# Helm Chart Documentation

This document provides information about the Helm chart created for the Python application.

## Chart Structure

The Helm chart is located in the `k8s/app-python` directory and has the following structure:

- `Chart.yaml`: Contains metadata about the chart and its dependencies
- `values.yaml`: Contains the default configuration values
- `templates/`: Contains the Kubernetes manifest templates
  - `deployment.yaml`: Template for the Kubernetes Deployment
  - `service.yaml`: Template for the Kubernetes Service
  - `hooks/`: Contains Helm hooks
    - `pre-install-hook.yaml`: Hook that runs before installation
    - `post-install-hook.yaml`: Hook that runs after installation
- `charts/`: Contains dependency charts (sub-charts)
  - `monitoring-0.1.0.tgz`: Packaged Prometheus monitoring chart

## Configuration

The chart is configured with the following values:

- `replicaCount`: 3
- `image.repository`: python-app
- `image.tag`: latest
- `service.type`: NodePort
- `service.port`: 5000
- `monitoring.enabled`: true (controls whether the monitoring sub-chart is deployed)

## Chart Dependencies

The app-python chart includes a dependency on a monitoring chart, which deploys Prometheus for monitoring the application. The dependency is defined in the `Chart.yaml` file:

```yaml
dependencies:
  - name: monitoring
    version: 0.1.0
    repository: file://../monitoring
    condition: monitoring.enabled
```

The `condition: monitoring.enabled` allows us to control whether the monitoring sub-chart is deployed through the values.yaml file. When `monitoring.enabled` is set to `true`, the monitoring chart will be deployed alongside the application.

We can also override values for the monitoring chart through the app-python values.yaml file:

```yaml
monitoring:
  enabled: true
  service:
    type: ClusterIP
  resources:
    limits:
      memory: "256Mi"
```

## Helm Chart Hooks

The chart includes two hooks:

1. **Pre-install Hook**: Runs a Pod before the chart is installed that sleeps for 20 seconds
2. **Post-install Hook**: Runs a Pod after the chart is installed that sleeps for 20 seconds

Both hooks have a delete policy of `hook-succeeded,hook-failed`, which means they will be deleted after they complete, regardless of whether they succeed or fail.

### Hook Implementation Details

**Pre-install Hook:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: {{ .Release.Name }}-pre-install-hook
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": hook-succeeded,hook-failed
spec:
  restartPolicy: Never
  containers:
  - name: pre-install-job
    image: busybox
    command: 
    - "/bin/sh"
    - "-c" 
    - |
      echo "Starting pre-install hook for {{ .Release.Name }}"
      echo "Chart: {{ .Chart.Name }}"
      echo "Version: {{ .Chart.Version }}"
      echo "Sleeping for 20 seconds..."
      sleep 20
      echo "Pre-install hook completed successfully"
```

**Post-install Hook:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: {{ .Release.Name }}-post-install-hook
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": hook-succeeded,hook-failed
spec:
  restartPolicy: Never
  containers:
  - name: post-install-job
    image: busybox
    command: 
    - "/bin/sh"
    - "-c" 
    - |
      echo "Starting post-install hook for {{ .Release.Name }}"
      echo "Chart: {{ .Chart.Name }}"
      echo "Version: {{ .Chart.Version }}"
      echo "Sleeping for 20 seconds..."
      sleep 20
      echo "Post-install hook completed successfully"
```

## Helm Chart Hooks Troubleshooting

### Command: `helm lint app-python`
```
==> Linting app-python
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

### Command: `helm install --dry-run helm-hooks app-python`
```
NAME: helm-hooks
LAST DEPLOYED: Mon Mar 10 02:35:57 2025
NAMESPACE: default
STATUS: pending-install
REVISION: 1
HOOKS:
---
# Source: app-python/templates/hooks/post-install-hook.yaml
apiVersion: v1
kind: Pod
metadata:
  name: helm-hooks-post-install-hook
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": hook-succeeded,hook-failed
spec:
  restartPolicy: Never
  containers:
  - name: post-install-job
    image: busybox
    command: 
    - "/bin/sh"
    - "-c" 
    - |
      echo "Starting post-install hook for helm-hooks"
      echo "Chart: app-python"
      echo "Version: 0.1.0"
      echo "Sleeping for 20 seconds..."
      sleep 20
      echo "Post-install hook completed successfully"
---
# Source: app-python/templates/hooks/pre-install-hook.yaml
apiVersion: v1
kind: Pod
metadata:
  name: helm-hooks-pre-install-hook
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": hook-succeeded,hook-failed
spec:
  restartPolicy: Never
  containers:
  - name: pre-install-job
    image: busybox
    command: 
    - "/bin/sh"
    - "-c" 
    - |
      echo "Starting pre-install hook for helm-hooks"
      echo "Chart: app-python"
      echo "Version: 0.1.0"
      echo "Sleeping for 20 seconds..."
      sleep 20
      echo "Pre-install hook completed successfully"
```

### Command: `kubectl get po`
```
NAME                                           READY   STATUS    RESTARTS   AGE
app-with-monitoring-app-python-684d585dcf-n869j   1/1     Running   0          38s
app-with-monitoring-app-python-684d585dcf-qm944   1/1     Running   0          38s
app-with-monitoring-app-python-684d585dcf-w4fz9   1/1     Running   0          38s
app-with-monitoring-b5749c5d7-kszr5               1/1     Running   0          38s
helm-hooks-app-python-d88bd8b59-86lkf      1/1     Running   0          36s
helm-hooks-app-python-d88bd8b59-8pm76      1/1     Running   0          36s
helm-hooks-app-python-d88bd8b59-gqnnh      1/1     Running   0          36s
my-release-my-app-76754f6d4-nwkxk          1/1     Running   0          76m
python-app-app-python-6c9b49c556-h72dt     1/1     Running   0          4m17s
python-app-app-python-6c9b49c556-jwzjc     1/1     Running   0          4m19s
python-app-app-python-6c9b49c556-jx2f9     1/1     Running   0          4m14s
web-app-559f47cd7d-7kg4t                   1/1     Running   0          139m
web-app-559f47cd7d-cjghl                   1/1     Running   0          139m
web-app-559f47cd7d-qqwzx                   1/1     Running   0          139m
```

### Command: `kubectl describe po helm-hooks-pre-install-hook`
```
Name:             helm-hooks-pre-install-hook
Namespace:        default
Priority:         0
Service Account:  default
Node:             minikube/192.168.49.2
Start Time:       Mon, 10 Mar 2025 02:37:39 +0300
Labels:           <none>
Annotations:      helm.sh/hook: pre-install
                  helm.sh/hook-weight: 0
Status:           Succeeded
IP:               10.244.0.47
IPs:
  IP:  10.244.0.47
Containers:
  pre-install-job:
    Container ID:  docker://d61a3a80accf3c6652ac3afcfd2117af3bfb5925d3a7b06dd463e817d7714e5f
    Image:         busybox
    Image ID:      docker-pullable://busybox@sha256:498a000f370d8c37927118ed80afe8adc38d1edcbfc071627d17b25c88efcab0
    Port:          <none>
    Host Port:     <none>
    Command:
      /bin/sh
      -c
      echo "Starting pre-install hook for helm-hooks"
      echo "Chart: app-python"
      echo "Version: 0.1.0"
      echo "Sleeping for 20 seconds..."
      sleep 20
      echo "Pre-install hook completed successfully"
      
    State:          Terminated
      Reason:       Completed
      Exit Code:    0
      Started:      Mon, 10 Mar 2025 02:37:42 +0300
      Finished:     Mon, 10 Mar 2025 02:38:02 +0300
    Ready:          False
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-sj8p7 (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   False 
  Initialized                 True 
  Ready                       False 
  ContainersReady             False 
  PodScheduled                True 
Volumes:
  kube-api-access-sj8p7:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  66s   default-scheduler  Successfully assigned default/helm-hooks-pre-install-hook to minikube
  Normal  Pulling    65s   kubelet            Pulling image "busybox"
  Normal  Pulled     63s   kubelet            Successfully pulled image "busybox" in 2.26s (2.26s including waiting). Image size: 4269694 bytes.
  Normal  Created    63s   kubelet            Created container: pre-install-job
  Normal  Started    63s   kubelet            Started container pre-install-job
```

### Command: `kubectl describe po helm-hooks-post-install-hook`
```
Name:             helm-hooks-post-install-hook
Namespace:        default
Priority:         0
Service Account:  default
Node:             minikube/192.168.49.2
Start Time:       Mon, 10 Mar 2025 02:38:05 +0300
Labels:           <none>
Annotations:      helm.sh/hook: post-install
                  helm.sh/hook-weight: 0
Status:           Succeeded
IP:               10.244.0.48
IPs:
  IP:  10.244.0.48
Containers:
  post-install-job:
    Container ID:  docker://5203487109e6c2f1449a37b042273067ddafd2d728799be51335403395baac1d
    Image:         busybox
    Image ID:      docker-pullable://busybox@sha256:498a000f370d8c37927118ed80afe8adc38d1edcbfc071627d17b25c88efcab0
    Port:          <none>
    Host Port:     <none>
    Command:
      /bin/sh
      -c
      echo "Starting post-install hook for helm-hooks"
      echo "Chart: app-python"
      echo "Version: 0.1.0"
      echo "Sleeping for 20 seconds..."
      sleep 20
      echo "Post-install hook completed successfully"
      
    State:          Terminated
      Reason:       Completed
      Exit Code:    0
      Started:      Mon, 10 Mar 2025 02:38:11 +0300
      Finished:     Mon, 10 Mar 2025 02:38:32 +0300
    Ready:          False
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-s59fb (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   False 
  Initialized                 True 
  Ready                       False 
  ContainersReady             False 
  PodScheduled                True 
Volumes:
  kube-api-access-s59fb:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  45s   default-scheduler  Successfully assigned default/helm-hooks-post-install-hook to minikube
  Normal  Pulling    43s   kubelet            Pulling image "busybox"
  Normal  Pulled     41s   kubelet            Successfully pulled image "busybox" in 2.441s (2.441s including waiting). Image size: 4269694 bytes.
  Normal  Created    40s   kubelet            Created container: post-install-job
  Normal  Started    38s   kubelet            Started container post-install-job
```

## Troubleshooting

When setting up your Helm chart, it's important to ensure that the port configuration in your values.yaml matches the port that your application actually uses. In this case, the Flask application runs on port 5000 by default, so we needed to update the service.port value from 80 to 5000.

### Hook Delete Policy

Both hooks have been configured with a delete policy of `hook-succeeded,hook-failed`, which is implemented through the annotation `helm.sh/hook-delete-policy: hook-succeeded,hook-failed`. This ensures that hook resources are deleted after they have completed, regardless of whether they succeeded or failed. This keeps the cluster clean and prevents unused resources from accumulating.

## Checking Chart Dependencies

You can check the dependencies of a chart using the `helm dependency list` command:

```
$ helm dependency list app-python
NAME            VERSION REPOSITORY              STATUS
monitoring      0.1.0   file://../monitoring    ok
```

## Deployment Status with Dependencies

```bash
$ kubectl get pods,svc
NAME                                                   READY   STATUS    RESTARTS   AGE
pod/app-with-monitoring-app-python-684d585dcf-n869j    1/1     Running   0          38s
pod/app-with-monitoring-app-python-684d585dcf-qm944    1/1     Running   0          38s
pod/app-with-monitoring-app-python-684d585dcf-w4fz9    1/1     Running   0          38s
pod/app-with-monitoring-b5749c5d7-kszr5                1/1     Running   0          38s
pod/helm-hooks-app-python-d88bd8b59-86lkf              1/1     Running   0          36s
pod/helm-hooks-app-python-d88bd8b59-8pm76              1/1     Running   0          36s
pod/helm-hooks-app-python-d88bd8b59-gqnnh              1/1     Running   0          36s
pod/my-release-my-app-76754f6d4-nwkxk                  1/1     Running   0          76m
pod/python-app-app-python-6c9b49c556-h72dt             1/1     Running   0          4m17s
pod/python-app-app-python-6c9b49c556-jwzjc             1/1     Running   0          4m19s
pod/python-app-app-python-6c9b49c556-jx2f9             1/1     Running   0          4m14s
pod/web-app-559f47cd7d-7kg4t                           1/1     Running   0          139m
pod/web-app-559f47cd7d-cjghl                           1/1     Running   0          139m
pod/web-app-559f47cd7d-qqwzx                           1/1     Running   0          139m

NAME                                TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
service/app-with-monitoring         ClusterIP   10.108.253.136   <none>        9090/TCP         42s
service/app-with-monitoring-app-python  NodePort    10.110.125.1     <none>        5000:32116/TCP   42s
service/helm-hooks-app-python       NodePort    10.106.236.169   <none>        5000:31208/TCP   57m
service/kubernetes                  ClusterIP   10.96.0.1        <none>        443/TCP          157m
service/my-release-my-app           ClusterIP   10.100.101.151   <none>        80:TCP           71m
service/python-app-app-python       NodePort    10.111.33.217    <none>        5000:32441/TCP   3m
service/web-app-service             NodePort    10.97.23.108     <none>        80:30406/TCP     140m
```

## Accessing the Applications

### Python Application
To access the Python application, run the following command:

```bash
minikube service app-with-monitoring-app-python
```

### Prometheus Monitoring
To access the Prometheus monitoring interface, run:

```bash
kubectl port-forward svc/app-with-monitoring 9090:9090
```

Then open your browser to `http://localhost:9090`. 