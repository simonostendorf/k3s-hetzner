# deploy upgrade-controller
To upgrade the kubernetes cluster, we need to deploy the upgrade-controller. This controller will check for new kubernetes versions and upgrade the cluster if a new version is available. You can deploy different update strategies to the cluster to keep a working cluster during the upgrade.

You can download the latest version of the upgrade-controller deployment into the `deployments/upgrade-controller` folder on your local machine:
```bash
wget https://github.com/rancher/system-upgrade-controller/releases/latest/download/system-upgrade-controller.yaml -O deployments/upgrade-controller/deployment.yml
```

You can deploy the upgrade-controller with the following command from your local machine:
```bash
kubectl apply -f deployments/upgrade-controller/deployment.yml
```