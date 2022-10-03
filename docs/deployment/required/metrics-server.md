# Deploy Metrics-Server
Kubernetes uses the metrics-server for internal pod-metrics. It is not used for service metrics, these can later be added by other deployments like prometheus, node-exporter and grafana.

To deploy the metrics-server download the high-available deployment file to your local machine with the following command:
```bash
curl https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/high-availability.yaml --create-dirs -L -o deployments/metrics-server/deployment.yml
```

Change the deployment file with the following commands to fit our needs:
```bash
sed -z --in-place 's|replicas: 2|replicas: 3|g' deployments/metrics-server/deployment.yml
sed -z --in-place 's|    spec:\n      affinity:|    spec:\n      tolerations:\n        - key: CriticalAddonsOnly\n          operator: Exists\n      affinity:|g' deployments/metrics-server/deployment.yml
sed -z --in-place 's|            topologyKey: kubernetes.io/hostname\n      containers:|            topologyKey: kubernetes.io/hostname\n        nodeAffinity:\n          requiredDuringSchedulingIgnoredDuringExecution:\n            nodeSelectorTerms:\n              - matchExpressions:\n                  - key: node-role.kubernetes.io/master\n                    operator: Exists\n      containers:|g' deployments/metrics-server/deployment.yml
sed -z --in-place 's|apiVersion: policy/v1beta1|apiVersion: policy/v1|g' deployments/metrics-server/deployment.yml
```

Deploy the metrics-server with the following command:
```bash
kubectl apply -f deployments/metrics-server/deployment.yml
```

After deploying the metrics-server the pods and nodes can collect internal metrics used in later steps for autoscaling nodes and pods. 