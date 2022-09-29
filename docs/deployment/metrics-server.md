# deploy metrics-server
Kubernetes uses the metrics-server for internal pod-metrics. It is not used for service metrics, these can later be added by other deployments like prometheus, node-exporter and grafana.

To deploy the metrics-server copy the high-available [deployment file](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/metrics-server/deployment.yml) to your local machine and apply it to the cluster with the following command:
```bash
kubectl apply -f deployments/metrics-server/deployment.yml
```
You can find new releases of the metrics-server [here](https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/high-availability.yaml).

After deploying the metrics-server the pods and nodes can collect internal metrics used in later steps for autoscaling nodes and pods. 
