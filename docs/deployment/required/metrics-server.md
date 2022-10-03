# Deploy Metrics-Server
Kubernetes uses the metrics-server for internal pod-metrics. It is not used for service metrics, these can later be added by other deployments like prometheus, node-exporter and grafana.

To deploy the metrics-server download the high-available deployment file to your local machine with the following command:
```bash
curl https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/high-availability.yaml --create-dirs -L -o deployments/metrics-server/deployment.yml
```

Deploy the metrics-server with the following command:
```bash
kubectl apply -f deployments/metrics-server/deployment.yml
```

After deploying the metrics-server the pods and nodes can collect internal metrics used in later steps for autoscaling nodes and pods. 