# Upgrade-Controller
To upgrade the kubernetes cluster, we need to deploy the upgrade-controller. This controller will check for new kubernetes versions and upgrade the cluster if a new version is available. You can deploy different update strategies to the cluster to keep a working cluster during the upgrade.

You can download the latest version of the upgrade-controller deployment into the `deployments/upgrade-controller` folder on your local machine:
```bash
curl https://github.com/rancher/system-upgrade-controller/releases/latest/download/system-upgrade-controller.yaml --create-dirs -L -o deployments/upgrade-controller/deployment.yml
```

You can deploy the upgrade-controller with the following command from your local machine:
```bash
kubectl apply -f deployments/upgrade-controller/deployment.yml
```

For the upgrade-controller to work, we need to create a configmap with the upgrade-strategy.  
Visit the official documentation for [example upgrade plans](https://github.com/rancher/system-upgrade-controller#example-plans).