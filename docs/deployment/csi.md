# cloud storage interface
To use hetzner cloud volumes as persistent volume claims in kubernetes, we need to deploy the cloud-volume driver. The driver will than handle the volumes claims and create the volumes in hetzner cloud.  
You can find more about the driver on the official [hetzner-csi](https://github.com/hetznercloud/csi-driver) github repository. 

## setup secret
Similar to the ccm in step [3.1.1](#311-setup-secret), we need to create a secret for the cloud-volume driver. Replace the `CLOUD_API_TOKEN_HERE` in the [secret file](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/csi/secret.yml) with the token you created in [step the preparation](../../prerequisites/hetzner/#create-api-tokens) (in this example named as `container-storage-interface`).

Apply the secret to the kubernetes cluster by running the following command on your local machine:
```bash
kubectl apply -f deployments/csi/secret.yml
```

## deploy hcloud-csi
Download the latest version of the storage driver deployment into the `deployments/csi` folder on your local machine:
```bash
wget https://raw.githubusercontent.com/hetznercloud/csi-driver/v1.6.0/deploy/kubernetes/hcloud-csi.yml -O deployments/csi/deployment.yml
```

Edit the deployment file and replace the secret name. You can use the following command to do this:
```bash
sed -i 's/^.\{18\}name: hcloud-csi$/                  name: hetzner_container_storage_interface/' deployments/csi/deployment.yml
```

You can deploy the cloud controller manager with the following command from your local machine:
```bash
kubectl apply -f deployments/csi/deployment.yml
```

After this step you should see pods comming up in the cluster. To validate the starting pods, run the following command:
```bash
kubectl get pods -n kube-system
```
You have to use the kube-system namespace here, because the volume-driver is deployed in this namespace.