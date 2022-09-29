# cluster-autoscaler
In the whole setup we didnt setup agent (worker) nodes for the cluster. This is because we want to use the cluster-autoscaler to scale the cluster up and down based on the current workload. In this step we will create the configuration for our agent nodes and the corresponding deployment for the cluster-autoscaler.

## create cloud-init configuration
The cluster-autoscaler will create new vms inside the hetzner cloud. To configure the new vms we need to create a cloud-init configuration. The cloud-init configuration will install needed packages, do needed configuration, install k3s and join the cluster. 

Copy the [cloud-init-config](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/cluster-autoscaler/cloud-init.yml) to your local machine and edit the parameters to fit your needs.  
You definitly have to edit the following parameters:
  * NOT NEEDED IN CURRENT CONFIG (`HETZNER_TOKEN_HERE` insert your hetzner cloud token for the cluster autoscaler here)
  * `K3S_TOKEN_HERE` insert your k3s token here

The cluster autoscaler needs the cloud-init configuration as base64 encoded string. You can encode the file with the following command:
```bash
openssl enc -base64 -in deployments/cluster-autoscaler/cloud-init.yml -out deployments/cluster-autoscaler/cloud-init.yml.b64
```

## create secret
Copy the [secret file](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/cluster-autoscaler/secret.yml) to your local machine and insert your hetzner cloud token at `HETZNER_TOKEN_HERE`.

Apply the secret to the cluster with the following command:
```bash
kubectl apply -f deployments/cluster-autoscaler/secret.yml
```

## create autoscaler image
As described in [the preparation step](../../prerequisites/local-machine/#go) we need to create a custom image for the cluster-autoscaler using go. 
Clone the autoscaler git repository into a new folder using the following command:
```bash
git clone https://github.com/kubernetes/autoscaler
cd autoscaler/cluster-autoscaler
```

Start the build process with the following commands:
Replace `USERNAME` with your docker username. 
```bash
make build-in-docker
docker build -t DOCKER_USERNAME/k8s-cluster-autoscaler:latest -f Dockerfile.amd64 .
```

Push the created docker-image to your docker registry with the following command (also replace `DOCKER_USERNAME` with your username):
```bash
docker push DOCKER_USERNAME/k8s-cluster-autoscaler:latest
```
The docker registry was created in the [preparation step](../../prerequisites/container-registry/#create-account).

## create repository secret
To pull the custom image from the docker registry we need to create a secret inside the cluster to get access to the container repository.  
You can create the secret from the commandline with the following command:
```bash
kubectl create secret docker-registry -n kube-system dockerhub --docker-server=docker.io --docker-username=DOCKER_USERNAME --docker-password=DOCKER_PASSWORD --docker-email=DOCKER_EMAIL
```
Replace `DOCKER_USERNAME` with your username, `DOCKER_PASSWORD` with your password and `DOCKER_EMAIL` with your email address used inside docker.

## configure deployment
Copy the [deployment file](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/cluster-autoscaler/deployment.yml) to your local machine and edit the following parameters:

  * `DOCKER_USERNAME` insert your docker username here
  * `--nodes=1:10:CX21:FSN1:k8s-agent-fsn1` is the node configuration. You can find more information [here](https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/hetzner/README.md)
  * `INSERT_YOUR_BASE64_CLOUDINIT_HERE` insert your base64 encoded cloud-init configuration here
  * `HETZNER_NETWORK_ID_HERE` insert your private network id from the hetzner cloud here. The network id needs to be inserted as string. 

If you want to disable the public ipv4 and/or ipv6 use the aspects `HCLOUD_PUBLIC_IPV4` and `HCLOUD_PUBLIC_IPV6` and set them to `false`.
Maybe `HCLOUD_PLACEMENT_GROUP` is a possible option, but its not tested yet. 

The default configuration will create 3 agent pools with minimal 1 node and maximal 10 nodes. The nodes will be created with the CX21 server type and will be located in the FSN1 / HEL1 and NBG1 datacenter. 

## deploy workload
You can apply the cluster autoscaler with the following command:
```bash
kubectl apply -f deployments/cluster-autoscaler/deployment.yml
```