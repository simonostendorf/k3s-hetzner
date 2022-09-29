# cloud-controller-manager
The first step is to deploy the cloud-controller-manager. This is needed to manage the cloud resources like loadbalancers, volumes and so on. This is the integration of the hetzner cloud api into the kubernets cluster. 

## setup secret
The first step is to create a kubernetes secret with our cloud api token that the cloud-controller-manager will use to authenticate against the hetzner cloud api.  
We have created the token in [the preparation step](../../prerequisites/hetzner/#create-api-tokens).  
In my example configuration I have named the token `cloud-controller-manager` in the hetzner cloud. 

You also need the network-id from your private network. To get the id you can either copy the id from the hetzner cloud webinterface or copy the id from the following command:
```bash
hcloud network list
```

Copy the [secrets file](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/ccm/secret.yml) for the cloud-controller-manager to your local machine and replace the `CLOUD_API_TOKEN_HERE` with the token you created in [the preparation step](../../prerequisites/hetzner/#create-api-tokens) (in this example named as `cloud-controller-manager`) and the `NETWORK_ID_HERE` with the id of your private network as explaned above.  

Apply the secret to the kubernetes cluster by running the following command on your local machine:
```bash
kubectl apply -f deployments/ccm/secret.yml
```

## deploy ccm
Download the latest version of the cloud controller manager deployment into the `deployments/ccm` folder on your local machine:
```bash
wget https://github.com/hetznercloud/hcloud-cloud-controller-manager/releases/latest/download/ccm-networks.yaml -O deployments/ccm/deployment.yml
```

Edit the deployment file and replace the secret name and the pod ip range. You can use the following commands to do this:
```bash
sed -i 's/name: hcloud$/name: hetzner_cloud_controller_manager/' deployments/ccm/deployment.yml
sed -i 's/10.244.0.0/10.100.0.0/' deployments/ccm/deployment.yml
```

You can deploy the cloud controller manager with the following command from your local machine:
```bash
kubectl apply -f deployments/ccm/deployment.yml
```

After this step you should see pods comming up in the cluster. To validate the starting pods, run the following command:
```bash
kubectl get pods -n kube-system
```
You have to use the kube-system namespace here, because the cloud-controller-manager is deployed in this namespace.