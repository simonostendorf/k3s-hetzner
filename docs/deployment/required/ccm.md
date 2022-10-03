# Cloud-Controller-Manager
The first step is to deploy the cloud-controller-manager. This piece of software is needed to manage the cloud resources like loadbalancers, volumes and so on. This is the integration of the hetzner cloud api into the kubernets cluster. 

## Setup Secret
The first step is to create a kubernetes secret with our cloud api token that the cloud-controller-manager will use to authenticate against the hetzner cloud api.  
We have created the token in [the preparation step](../../../prerequisites/hetzner/#create-api-tokens).  
In my example configuration I have named the token `cloud-controller-manager` in the hetzner cloud. 

You also need the network-id from your private network. To get the id you can either copy the id from the hetzner cloud webinterface or copy the id from the following command:
```bash
hcloud network list #(1)!
```

1. The network id is the first column of the output.

Create a new deployment file:
```bash
mkdir -p deployments/ccm
nano deployments/ccm/secret.yml
```

And add the following content:
```yaml linenums="1"
apiVersion: v1
kind: Secret
metadata:
  name: hetzner-cloud-controller-manager
  namespace: kube-system
stringData:
  token: "CLOUD_API_TOKEN_HERE" #(1)!
  network: "NETWORK_ID_HERE" #(2)!
```

1. Replace `CLOUD_API_TOKEN_HERE` with the token you created in the prerequisite step. The token is named `cloud-controller-manager` in this example.
2. Replace `NETWORK_ID_HERE` with the network id you copied in the prerequisite step.

Apply the secret to the kubernetes cluster by running the following command on your local machine:
```bash
kubectl apply -f deployments/ccm/secret.yml
```

## Deploy CCM
Download the latest version of the cloud controller manager deployment into the `deployments/ccm` folder on your local machine:
```bash
curl https://github.com/hetznercloud/hcloud-cloud-controller-manager/releases/latest/download/ccm-networks.yaml --create-dirs -L -o deployments/ccm/deployment.yml
```

Edit the deployment file and replace the secret name and the pod ip range. You can use the following commands to do this:
```bash
sed -i 's/name: hcloud$/name: hetzner-cloud-controller-manager/' deployments/ccm/deployment.yml
sed -i 's/10.244.0.0/10.100.0.0/' deployments/ccm/deployment.yml
```

You can deploy the cloud controller manager with the following command from your local machine:
```bash
kubectl apply -f deployments/ccm/deployment.yml
```

After this step you should see pods comming up in the cluster. To validate the starting pods, run the following command:
```bash
kubectl get pods -n kube-system #(1)!
```

1. You have to use the kube-system namespace here, because the cloud-controller-manager is deployed in this namespace.