# Cluster-Autoscaler
In the whole setup we didnt setup agent (worker) nodes for the cluster. This is because we want to use the cluster-autoscaler to scale the cluster up and down based on the current workload. In this step we will create the configuration for our agent nodes and the corresponding deployment for the cluster-autoscaler.

## Create cloud-init Configuration
The cluster-autoscaler will create new vms inside the hetzner cloud. To configure the new vms we need to create a cloud-init configuration. The cloud-init configuration will install needed packages, do needed configuration, install k3s and join the cluster. 

Create a new file for the cloud-init configuration and edit the file contents:
```bash
mkdir -p deployments/cluster-autoscaler
nano deployments/cluster-autoscaler/cloud-init.yml
```

Create the following cloud-init configuration:

!!! danger "Replace values"
    Please replace `YOUR_TIMEZONE` with your timezone used for the servers before.
    You also have to replace `YOUR_HETZNER_TOKEN` with your hetzner token. In this example the token is named `cluster-autoscaler`
    Also replace `YOUR_NETWORK_ID` with your network id of the private network. You looked up the network id in a previous step but you can also look it up with `hcloud network list`.
    Replace `YOUR_K3S_TOKEN` with your k3s token, created in the [k3s-setup step](../../installation/k3s/#token).

```yaml linenums="1" hl_lines="6 9 11"
#cloud-config
runcmd:
- apt update
- apt upgrade -y
- apt install apparmor apparmor-utils python3-pip -y
- timedatectl set-timezone YOUR_TIMEZONE
- pip install hcloud
- wget https://github.com/simonostendorf/k3s-hetzner/tree/main/scripts/setup-agent-nodes.py -o setup-agent-nodes.py
- python3 setup-agent-nodes.py --token YOUR_HETZNER_TOKEN --server_name $(hostname -f) --network_id YOUR_NETWORK_ID
- sleep 20
- curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="v1.25.0-rc1+k3s1" K3S_TOKEN="YOUR_K3S_TOKEN" K3S_URL="https://10.0.0.100:6443" INSTALL_K3S_EXEC="agent --node-name="$(hostname -f)" --kubelet-arg="cloud-provider=external" --node-ip=$(hostname -I | awk '{print $2}') --node-external-ip=$(hostname -I | awk '{print $1}') --flannel-iface=ens10" sh -
```

The cluster autoscaler needs the cloud-init configuration as base64 encoded string. You can encode the file with the following command:
```bash
openssl enc -base64 -in deployments/cluster-autoscaler/cloud-init.yml -out deployments/cluster-autoscaler/cloud-init.yml.b64
```

## Create Secret
You have to create a new secret for the cluster autoscaler. The secret will contain the hetzner cloud token that the cluster autoscaler can create servers inside the hetzner cloud. The secret will also contain the base64 encoded cloud-init configuration.

Create a new deployment file:
```bash
mkdir -p deployments/cluster-autoscaler
nano deployments/cluster-autoscaler/secret.yml
```

And add the following content:
```yaml linenums="1"
apiVersion: v1
kind: Secret
metadata:
  name: hetzner-cluster-autoscaler
  namespace: kube-system
stringData:
  token: "CLOUD_API_TOKEN_HERE" #(1)!
  cloud-init: "CLOUD_INIT_HERE" #(2)!
```

1. Replace `CLOUD_API_TOKEN_HERE` with the token you created in the prerequisite step. The token is named `cluster-autoscaler` in this example.
2. Replace `CLOUD_INIT_HERE` with the base64 encoded cloud-init configuration. You can read the file with `cat deployments/cluster-autoscaler/cloud-init.yml.b64` and copy the content.

You can print your base64 encoded cloud-init configuration without newlines with the following command:
```bash
cat deployments/cluster-autoscaler/cloud-init.yml.b64 | awk '{ printf("%s", $0) }'
``` 

Apply the secret to the kubernetes cluster by running the following command on your local machine:
```bash
kubectl apply -f deployments/cluster-autoscaler/secret.yml
```

## Create autoscaler Image
As described in [the preparation step](../../prerequisites/local-machine/#go) we need to create a custom image for the cluster-autoscaler using go. 
Clone the autoscaler git repository into a new folder using the following command:
```bash
git clone https://github.com/kubernetes/autoscaler
cd autoscaler/cluster-autoscaler
```

Start the build process with the following commands:

!!! danger "Replace values"
    You have to replace `DOCKER_USERNAME` with your docker username, created in the [prerequisite step](../../prerequisites/container-registry/#create-account).

```bash
make build-in-docker
docker build -t DOCKER_USERNAME/k8s-cluster-autoscaler:latest -f Dockerfile.amd64 .
```

Push the created docker-image to your docker registry with the following command:

!!! danger "Replace values"
    You have to replace `DOCKER_USERNAME` with your docker username, created in the [prerequisite step](../../prerequisites/container-registry/#create-account).

```bash
docker push DOCKER_USERNAME/k8s-cluster-autoscaler:latest
```

Go back to your old working directory with the following command:
```bash
cd ../..
```

## Create Registry Secret
To pull the custom image from the docker registry we need to create a secret inside the cluster to get access to the container registry.  
You can create the secret from the commandline with the following command:

!!! danger "Replace values"
    You have to replace `DOCKER_USERNAME` with your docker username, created in the [prerequisite step](../../prerequisites/container-registry/#create-account).
    You have to replace `DOCKER_TOKEN` with your docker token, created in the [prerequisite step](../../prerequisites/container-registry/#create-token). Be shure to change the read-only token (named `k8s-hetzner` in this example)

```bash
kubectl create secret docker-registry -n kube-system dockerhub --docker-server=docker.io --docker-username=DOCKER_USERNAME --docker-password=DOCKER_TOKEN
```

## Configure Deployment
To deploy the cluster autoscaler you have to create a deployment file. You can download the latest deployment file with the following command:
```bash
curl https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/hetzner/examples/cluster-autoscaler-run-on-master.yaml --create-dirs -L -o deployments/cluster-autoscaler/deployment.yml
```

Edit the file with the following command:
```bash
nano deployments/cluster-autoscaler/deployment.yml
```

Change the file contents to the following:
```yaml linenums="1"
# Uder spec.template.spec.containers[0].image replace the image with your own image
DOCKER_USERNAME/k8s-cluster-autoscaler:latest #(1)!

# Under spec.template.spec.containers[0].command add the following arguments: (after line 168 in this example)
            - --nodes=1:10:CX21:HEL1:k8s-agent-hel1 #(2)!
            - --nodes=1:10:CX21:FSN1:k8s-agent-fsn1 #(3)!
            - --nodes=1:10:CX21:NBG1:k8s-agent-nbg1 #(4)!
            - --scale-down-delay-after-add=30m0s #(5)!
            - --scale-down-unneeded-time=30m0s #(6)!
            - --scale-down-unready-time=10m0s #(7)!

# Under spec.template.spec.containers[0].env replace the secret name with: (line 173 in this example)
name: hetzner-cluster-autoscaler

# Under spec.template.spec.containers[0].env replace the secret value with: (line 176 in this example)
            valueFrom:
                secretKeyRef:
                  name: hetzner-cluster-autoscaler
                  key: cloud-init

# Under spec.template.spec.imagePullSecrets set the secret name with: (line 187 in this example)
name: dockerhub

# Under spec.template.spec.containers[0].env add the secret value with: (eg. after line 180 in this example)
          - name: HCLOUD_IMAGE
            value: debian-11

# Under spec.template.spec.containers[0].env add the secret value with: (eg. after line 180 in this example)
          - name: HCLOUD_PUBLIC_IPV4 #(8)!
            value: false
```

1. Replace `DOCKER_USERNAME` with your docker username, created in the [prerequisite step](../../prerequisites/container-registry/#create-account).
2. Configure the Node pools you want to use here. Example: 1 to 10 servers of type cx21 in hel-1
3. Configure the Node pools you want to use here. Example: 1 to 10 servers of type cx21 in fsn-1
4. Configure the Node pools you want to use here. Example: 1 to 10 servers of type cx21 in nbg-1
5. Configure the scale down timer here
6. Configure the scale down timer here
7. Configure the scale down timer here
8. Set this to true if you want to use public ipv4 addresses

!!! todo "ToDo"
    Maybe `HCLOUD_PLACEMENT_GROUP` is a possible option, but its not tested yet. 

The default configuration will create 3 agent pools with minimal 1 node and maximal 10 nodes. The nodes will be created with the CX21 server type and will be located in the FSN1 / HEL1 and NBG1 datacenter. 

## Deploy Workload
You can apply the cluster autoscaler with the following command:
```bash
kubectl apply -f deployments/cluster-autoscaler/deployment.yml
```