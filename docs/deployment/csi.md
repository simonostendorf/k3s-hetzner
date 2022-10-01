# Cloud Storage Interface
To use hetzner cloud volumes as persistent volume claims in kubernetes, we need to deploy the cloud-volume driver. The driver will than handle the volume claims and create the volumes in hetzner cloud.  
You can find more about the driver on the official [hetzner-csi](https://github.com/hetznercloud/csi-driver) github repository. 

## Setup Secret
Similar to the cloud-controller-manager in a previous step, we have to create a secret for the cloud-storage-interface. 
We have created the token in [the preparation step](../../prerequisites/hetzner/#create-api-tokens).  
In my example configuration I have named the token `cloud-storage-interface` in the hetzner cloud. 

Create a new deployment file:
```bash
mkdir -p deployments/csi
nano deployments/csi/secret.yml
```

And add the following content:
```yaml linenums="1"
apiVersion: v1
kind: Secret
metadata:
  name: hetzner-container-storage-interface
  namespace: kube-system
stringData:
  token: "CLOUD_API_TOKEN_HERE" #(1)!
```

1. Replace `CLOUD_API_TOKEN_HERE` with the token you created in the prerequisite step. The token is named `cloud-storage-interface` in this example.

Apply the secret to the kubernetes cluster by running the following command on your local machine:
```bash
kubectl apply -f deployments/csi/secret.yml
```

## Deploy hcloud-csi
Download the latest version of the storage driver deployment into the `deployments/csi` folder on your local machine:
```bash
curl https://raw.githubusercontent.com/hetznercloud/csi-driver/v1.6.0/deploy/kubernetes/hcloud-csi.yml --create-dirs -o deployments/csi/deployment.yml
```

Edit the deployment file and replace the secret name. You can use the following command to do this:
```bash
sed -i 's/^.\{18\}name: hcloud-csi$/                  name: hetzner-container-storage-interface/' deployments/csi/deployment.yml
```

You can deploy the storage-interface with the following command from your local machine:
```bash
kubectl apply -f deployments/csi/deployment.yml
```

After this step you should see pods comming up in the cluster. To validate the starting pods, run the following command:
```bash
kubectl get pods -n kube-system #(1)!
```

1. You have to use the kube-system namespace here, because the storage-interface is deployed in this namespace.