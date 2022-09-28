# High-Available k3s-Cluster using Hetzner Cloud

# Introduction
In this repo you find a step by step solution to deploy a high-available, auto scalable and loadbalanced [k3s](https://k3s.io/) cluster to servers inside the Hetzner-Cloud.  
This repo covers:
* Setting up all prerequisites on the hetzner cloud and local machine
* Installation and configuration of the hetzner cloud components (placement groups, networks, servers, load balancers)
* Configuration of hetzner load balancer to load balance the kubernetes api and the default service ingress
* Installation and configuration of k3s servers (controlplane) and agents (workers)
* Setup Hetzner Cloud Controller Manager to interact with hetzner cloud api
* Setup Hetzner Storage Driver to use hetzner cloud volumes as persistent volume claim
* Setup system-upgrade controller to do easy updates with predefined update plans
* Setup traefik as ingress-controller
* Setup cert-manager to get certificates from lets encrypt
* Deploy metrics-server to collect metrics from pods and nodes
* Setup cluster autoscaler with hetzner cloud provider to autoscale worker nodes if running out of compute power
* Give an example for horizontal pod autoscaling to start new pods if compute power from one pod exceeded

# ToDo
* Deploy kube-prometheus-stack (prometheus, grafana, alertmanager, node-exporter etc.) to collect and visualize metrics from nodes and pods
* Setup vertical pod autoscaler to automaticly update pod resources requests and limits
* Setup goldilocks as dashboard for the vertical pod autoscaler
* Setup argo-cd to automaticly deploy workloads as part of the ci/cd pipeline

# Steps
1. [Prerequisites](#1-prerequisites)  
1.1. [Hetzner](#11-hetzner)  
1.1.1. [create cloud account](#111-create-cloud-account)  
1.1.2. [create project](#112-create-project)  
1.1.3. [create API token(s)](#113-create-api-tokens)  
1.1.4. [upload ssh-key(s)](#114-upload-ssh-keys)  
1.2. [container repository](#12-container-repository)  
1.2.1. [create account](#121-create-account)  
1.2.2. [create token](#122-create-token)  
1.3. [dns provider](#13-dns-provider)  
1.3.1. [create account](#131-create-account)  
1.3.2. [setup sites and dns records](#132-setup-sites-and-dns-records)  
1.3.3. [create token](#133-create-token)  
1.4. [Local machine](#14-local-machine)  
1.4.1. [hcloud](#141-hcloud)  
1.4.1.1. [install hcloud](#1411-install-hcloud)  
1.4.1.2. [setup hcloud context](#1412-setup-hcloud-context)  
1.4.2. [Helm](#142-helm)  
1.4.3. [kubectl](#143-kubectl)  
2. [Installation](#2-installation)  
2.1. [Hetzner](#21-hetzner)  
2.1.1. [create placement groups](#211-create-placement-groups)  
2.1.2. [create private network](#212-create-private-network)  
2.1.3. [create servers](#213-create-servers)  
2.1.4. [create load balancers](#214-create-load-balancers)  
2.2. [servers](#22-servers)  
2.2.1. [install updates](#221-install-updates)  
2.2.2. [set timezone](#222-set-timezone)  
2.2.3. [install packages](#223-install-packages)  
2.3. [k3s](#23-k3s)  
2.3.1. [control-plane](#231-control-plane)  
2.3.1.1. [install first server](#2311-install-first-server)  
2.3.1.2. [install other servers](#2312-install-other-servers)  
2.3.2. [setup kubectl](#232-setup-kubectl)  
3. [Deployments](#3-deployments)  
3.1. [cloud-controller-manager](#31-cloud-controller-manager)  
3.1.1. [setup secret](#311-setup-secret)  
3.1.2. [deploy ccm](#312-deploy-ccm)  
3.2. [cloud-volume driver](#32-cloud-volume-driver)  
3.2.1. [setup secret](#321-setup-secret)  
3.2.2. [deploy hcloud-csi](#322-deploy-hcloud-csi)  
3.3. [deploy upgrade-controller](#33-deploy-upgrade-controller)  
3.4. [traefik](#34-traefik)  
3.4.1. [prerequisites](#341-prerequisites)  
3.4.2. [configure helm values](#342-configure-helm-values)  
3.4.3. [deploy workload](#343-deploy-workload)  
3.4.4. [setup default middleware](#344-setup-default-middleware)  
3.4.5. [dashboard](#345-dashboard)  
3.4.5.1. [create basic auth](#3451-create-basic-auth)  
3.4.5.2. [setup middleware](#3452-setup-middleware)  
3.4.5.3. [create IngressRoute](#34543-create-ingressroute)  
3.5. [cert-manager](#35-cert-manager)  
3.5.1. [prerequisites](#351-prerequisites)  
3.5.2. [configure helm values](#352-configure-helm-values)  
3.5.3. [deploy workload](#353-deploy-workload)  
3.5.4. [certificates](#354-certificates)  
3.5.4.1. [create Cloudflare token](#3541-create-cloudflare-token)  
3.5.4.2. [letsencrypt staging](#3542-letsencrypt-staging)  
3.5.4.2.1. [create CertificateIssuer](#35421-create-certificateissuer)  
3.5.4.2.2. [create Certificate](#35422-create-certificate)  
3.5.4.2.3. [add certificate to traefik](#35423-add-certificate-to-traefik)  
3.5.4.3. [letsencrypt production](#3543-letsencrypt-production)  
3.5.4.3.1. [create CertificateIssuer](#35431-create-certificateissuer)  
3.5.4.3.2. [create Certificate](#35432-create-certificate)  
3.5.4.3.3. [add certificate to traefik](#35433-add-certificate-to-traefik)  
3.6. [deploy metrics-server](#36-deploy-metrics-server)  
3.7. [cluster-autoscaler](#37-cluster-autoscaler)  
3.7.1. [create cloud-init configuration](#371-create-cloud-init-configuration)  
3.7.2. [create secret](#372-create-secret)  
3.7.3. [create autoscaler image](#373-create-autoscaler-image)  
3.7.4. [create repository secret](#374-create-repository-secret)  
3.7.5. [configure deployment](#375-configure-deployment)  
3.7.6. [deploy workload](#376-deploy-workload)  
3.8. [example horizontal pod autoscaler](#38-example-horizontal-pod-autoscaler)  
3.8.1. [example application](#381-example-application)  
3.8.2. [scale pods](#382-scale-pods)  
3.8.3. [delete deployment](#383-delete-deployment)  

# 1. Prerequisites
## 1.1. Hetzner
### 1.1.1. create cloud account
Create an account at the Hetzner Cloud Hosting portal.  
You can use [my ref-link](https://hetzner.cloud/?ref=QVP9EsLHwtNY) to get 20€ for free if you want. 

### 1.1.2. create project
The autoscale cluster should sit in a **plain cloud project**.  
Login at [console.hetzner.cloud/projects](https://console.hetzner.cloud/projects) and create new project.  
The name of the project doesn't matter.  

<img src="./docs/img/112-create-project.png" width=50%>

### 1.1.3. create API token(s)
Open the project and go to security and the api-tokens tab.  
Here you have to create **at least one api-token**.  
I created several ones to keep the different services seperated and logged what which service does. 
I created the following tokens:
* `command-line-interface` (used for hcloud cli application on local machine)
* `container-storage-interface` (used for persistent volume driver)
* `cloud-controller-manager` (used for cloud-controller-manager)
* `cluster-autoscaler` (used for cluster autoscaler)  

All tokens need read and write access.  
Save them in a **secure place** you will need them later and cant view them another time inside the webpanel.

<img src="./docs/img/113-create-api-tokens.png" width=50%>

### 1.1.4. upload ssh-key(s)
Stay inside the security part of the hetzner webinterface and open the tab for the ssh-keys.  
Click add to upload your ssh-key(s). Paste your public key to the window.  
They will be later added to the servers when we create them. 
If you want to create a new ssh-key you can use `ssh-keygen`. 

## 1.2. container repository
You need an account at a container repository. You can use for example the [docker-hub](https://hub.docker.com/) or the [github-container-repository]().  
In this example, I will use the docker-hub. 

### 1.2.1. create account
First, create an account at your container-repository provider.  
If you want to use a docker-hub account, you can register [here](https://hub.docker.com/signup).

<img src="./docs/img/121-create-account.png" width=30%>

### 1.2.2. create token
If you want to use private repositories you have to create an access token to pull the private images from the kubernetes host.  

If you use docker, move to your [security-profile-page](https://hub.docker.com/settings/security) and create an access-token.  
You can name the token whatever you want. The token only needs read access to pull the images. Be shure to save the token in a save place because you need it later in the setup.  

<img src="./docs/img/122-create-token.png" width=40%>

## 1.3. dns provider
To use ssl-certificates later, we will use the cert-manager from kubernetes with lets-encrypt certificates. To use this, we need a dns provider for our domain that supports dns01-validation via acme. You can find supported dns providers in the [documentation from the kubernetes cert-manager](https://cert-manager.io/docs/configuration/acme/dns01/#supported-dns01-providers).  
In this tutorial i will use [CloudFlare](https://cloudflare.com)

### 1.3.1. create account
First, you have to create an account at your dns-provider.  
If you want to use CloudFlare, you can create an account [here](https://dash.cloudflare.com/sign-up). 

<img src="./docs/img/131-create-account.png" width=40%>

### 1.3.2. setup sites and dns records
After creating an account you have to add your domain as a new site to your dns provider.  
After that you can import your old dns entries or add new ones.  
As final step you need to change the nameservers from your domain. You can do this normally in the control panel from your domain hoster.  
Because these steps are different from dns provider to dns provider and different from domain hoster to domain hoster, I will skip this part in this tutorial. 

### 1.3.3. create token
To use the dns01-challenge, the acme client will create a txt dns-record for you to validate that you own the requested domain. To change the dns settings (add an entry) you have to create an access token for the acme client.  

If you use CloudFlare, move to your [api-token-profile-page](https://dash.cloudflare.com/profile/api-tokens) and create a new api-token. Dont use the global api token, you need a new api-token for your specific dns-zone.   
As token-template you can use the edit-dns-zone setting. In the next step you have to select your site you have created in step [1.3.2](#132-setup-sites-and-dns-records). Remember to save the token, it will not be shown again. 

## 1.4. local machine
In the last preparation step, we have to setup our local machine. As local machine you need a linux-host. You can install it directy to your host, use a virtual machine or - as i do - use wsl, the windows subsystem for linux.  

### 1.4.1. hcloud
To control the hetzner cloud from the command line you need hcloud, a tool by hetzner. You can find more information [here](https://github.com/hetznercloud/cli).

#### 1.4.1.1. install hcloud
You can install hcloud with [homebrew](https://brew.sh/).  
Run `brew install hcloud` to install hcloud to your system. 

#### 1.4.1.2. setup hcloud context
To communicate with your hetzner cloud project from step [1.1.2](#112-create-project) you created an api-token in step [1.1.3](#113-create-api-tokens). In my example i named it `command-line-interface`.  
To link the cloud project with the hcloud application by using the api-token, you have to create an hcloud-context. You can manage different cloud-projects with different contexts.  
To create a new context type `hcloud context create [NAME]` and paste your previously saved api-token.  
You can see all contexts with `hcloud context list` and set your used context with `hcloud context use [NAME]`. 

### 1.4.2. Helm
To install packages to kubernetes you need helm on your local machine.  
To install helm, visit the [official installation manual](https://helm.sh/docs/intro/install/#from-script). 

### 1.4.3. kubectl
To administrate the kubernetes cluster you also need kubectl, a command line interface to control kubernetes clusters.  
You can visit the [kubernets documentation](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-kubectl-binary-with-curl-on-linux) for installation steps.  

# 2. Installation
In this step we will install the kubernetes cluster and all needed components.

## 2.1. Hetzner
To provide servers, a network-connection and load-balancers we will use the hetzner cloud. In this step we will create all parts for the hetzner infrastructure. 

### 2.1.1. create placement groups
To separate all servers from each other, we will create placement groups for the servers. One placement group will be for one server-role for one location.  
To create all placement groups, run the following commands on your local machine:  
```bash
hcloud placement-group create --type spread --name k8s-control_plane-hel1 --label k8s-role=control_plane --label location=hel1

hcloud placement-group create --type spread --name k8s-control_plane-fsn1 --label k8s-role=control_plane --label location=fsn1

hcloud placement-group create --type spread --name k8s-control_plane-nbg1 --label k8s-role=control_plane --label location=nbg1
```
The commands will create a placement group for each hetzner location with the name `k8s-control_plane-[LOCATION]` and the labels `k8s-role=control_plane` and `location=[LOCATION]`.  

To create the placement groups for all agents, run these commands on your local machine:
```bash
hcloud placement-group create --type spread --name k8s-agent-hel1 --label k8s-role=agent --label location=hel1

hcloud placement-group create --type spread --name k8s-agent-fsn1 --label k8s-role=agent --label location=fsn1

hcloud placement-group create --type spread --name k8s-agent-nbg1 --label k8s-role=agent --label location=nbg1
```
The commands will create a placement group for each hetzner location with the name `k8s-agent-[LOCATION]` and the labels `k8s-role=agent` and `location=[LOCATION]` similar to the commands for the controlplane.

### 2.1.2. create private network
To create the private network for the servers run the following command on your local machine:
```bash
hcloud network create --name k8s --ip-range 10.0.0.0/8 --label k8s-role=control_plane-agent --label location=hel1-fsn1-nbg1
```
The command will create a network with the name `k8s` and the labels `k8s-role=control_plane-agent` and `location=hel1-fsn1-nbg1`.

To create the separate subnets inside this network, run the following commands on your local machine:
```bash
hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.0.0.0/24 # load_balancer control_plane and agent

hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.1.0.0/24 # control_plane hel1

hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.1.1.0/24 # control_plane fsn1

hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.1.2.0/24 # control_plane nbg1

hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.2.0.0/24 # agent hel1

hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.2.1.0/24 # agent fsn1

hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.2.2.0/24 # agent nbg1
```
The commands will create the following subnets:
  * 10.0.0.0/24 for the load balancers for the controlplane and agents
  * 10.1.0.0/24 for the controlplane in hel1
  * 10.1.1.0/24 for the controlplane in fsn1
  * 10.1.2.0/24 for the controlplane in nbg1
  * 10.2.0.0/24 for the agents in hel1
  * 10.2.1.0/24 for the agents in fsn1
  * 10.2.2.0/24 for the agents in nbg1

### 2.1.3. create servers
To create the servers for the control plane, run the following commands on your local machine:
```bash
hcloud server create --datacenter hel1-dc2 --image debian-11 --ssh-key k8s_ssh_key --type cx21 --placement-group k8s-control_plane-hel1 --name k8s-controlplane-hel1-1 --label k8s-role=control_plane --label location=hel1

hcloud server create --datacenter fsn1-dc14 --image debian-11 --ssh-key k8s_ssh_key --type cx21 --placement-group k8s-control_plane-fsn1 --name k8s-controlplane-fsn1-1 --label k8s-role=control_plane --label location=fsn1

hcloud server create --datacenter nbg1-dc3 --image debian-11 --ssh-key k8s_ssh_key --type cx21 --placement-group k8s-control_plane-nbg1 --name k8s-controlplane-nbg1-1 --label k8s-role=control_plane --label location=nbg1
```
The commands will create a control plane node in each hetzner location with...
  * the name `k8s-controlplane-[LOCATION]-1`
  * the server type CX21 (2 cores, 4gb ram)
  * the image debian-11
  * the ssh-key added in step [1.1.4](#114-upload-ssh-keys)
  * the placement-groups created in step [2.1.1](#211-create-placement-groups)
  * and the labels `k8s-role=control_plane` and `location=[LOCATION]`.

To add the servers to the private network, run the following commands on your local machine:
```bash
hcloud server attach-to-network k8s-controlplane-hel1-1 --network k8s --ip 10.1.0.1
hcloud server attach-to-network k8s-controlplane-fsn1-1 --network k8s --ip 10.1.1.1
hcloud server attach-to-network k8s-controlplane-nbg1-1 --network k8s --ip 10.1.2.1
```
The commands will add the servers to the private network `k8s` and assign the following ips:
  * 10.1.0.1 to the control plane in hel1
  * 10.1.1.1 to the control plane in fsn1
  * 10.1.2.1 to the control plane in nbg1

See also network creation in step [2.1.2](#212-create-private-network).

### 2.1.4. create load balancers
Kubernetes needs two loadbalancers. One for the control plane and one for the hosted services. In this setup we will use external hardware loadbalancers from the hetzner cloud.  
So in this step we will create the loadbalancers for the control plane and the hosted services with executing the following commands on your local machine:
```bash
hcloud load-balancer create --algorithm-type round_robin --location fsn1 --name k8s-controlplane --type lb11 --label k8s-role=control_plane --label location=fsn1

hcloud load-balancer attach-to-network k8s-controlplane --network k8s --ip 10.0.0.100

hcloud load-balancer create --algorithm-type round_robin --location nbg1 --name k8s-agent --type lb11 --label k8s-role=agent --label location=nbg1

hcloud load-balancer attach-to-network k8s-agent --network k8s --ip 10.0.0.200

hcloud load-balancer add-target k8s-controlplane --label-selector k8s-role=control_plane --use-private-ip

hcloud load-balancer add-service k8s-controlplane --destination-port 6443 --listen-port 6443 --protocol tcp

hcloud load-balancer add-target k8s-agent --label-selector k8s-role=agent --use-private-ip
```
The commands will create the following loadbalancers and configurations:
  * loadbalancer for the controlplane inside the location fsn1 with the private ip 10.0.0.100 using all all k8s-controlplanes on port 6443
  * loadbalancer for the agents inside the location nbg1 with the private ip 10.0.0.200 using all agent-nodes. Services will be added later by the kubernetes cloud controller manager. 

## 2.2. servers
After creating the servers we have to configure the operating system. 

### 2.2.1. install updates
First install all updates on the servers. To do this, run the following commands on all servers (control-plane-fsn1, control-plane-ngb1, control-plane-hel1):
```bash
apt update
apt upgrade -y
```

### 2.2.2. set timezone
Set the correct timezone on all servers. Do this by running the following command on all servers (control-plane-fsn1, control-plane-ngb1, control-plane-hel1):
```bash
timedatectl set-timezone Europe/Berlin
```
I will use the timezone Europe/Berlin in this guide. You can change this to your timezone.

### 2.2.3. install packages
To allow everything on the host we need to install some packages. To do this, run the following commands on all servers (control-plane-fsn1, control-plane-ngb1, control-plane-hel1):
```bash
apt install apparmor apparmor-utils -y
```

## 2.3. k3s
In this step we will install k3s on the servers.

### 2.3.1. control-plane
To install the k3s controlplane software on the controlplane host, we have to separate the installation to the first installed controlplane and the other controlplanes.

#### 2.3.1.1. install first server
To install k3s on the first controlplane node (in this example control-plane-fsn1), run the following command on the server:
```bash
curl -sfL https://get.k3s.io | \
INSTALL_K3S_VERSION="v1.25.0-rc1+k3s1" \
K3S_TOKEN="K3S_TOKEN_HERE" \
INSTALL_K3S_EXEC="server \
--disable-cloud-controller \
--disable servicelb \
--disable traefik \
--disable local-storage \
--disable metrics-server \
--node-name="$(hostname -f)" \
--cluster-cidr=10.100.0.0/16 \
--etcd-expose-metrics=true \
--kube-controller-manager-arg="bind-address=0.0.0.0" \
--kube-proxy-arg="metrics-bind-address=0.0.0.0" \
--kube-scheduler-arg="bind-address=0.0.0.0" \
--node-taint CriticalAddonsOnly=true:NoExecute \
--kubelet-arg="cloud-provider=external" \
--advertise-address=$(hostname -I | awk '{print $2}') \
--node-ip=$(hostname -I | awk '{print $2}') \
--node-external-ip=$(hostname -I | awk '{print $1}') \
--flannel-iface=ens10 \
--tls-san=LOADBALANCER_PUBLIC_IP_HERE \
--tls-san=10.0.0.100 \
--tls-san=10.1.0.1 \
--tls-san=10.1.1.1 \
--tls-san=10.1.2.1 \
--cluster-init" sh -
```
Please replace the `K3S_TOKEN_HERE` with the token you created in step [2.1.1](#211-create-k3s-token) and the `LOADBALANCER_PUBLIC_IP_HERE` with the public ip of the loadbalancer for the controlplane created in step [2.1.4](#214-create-load-balancers).  
This installation disables or customises many parameters to fit the needs of this setup.

#### 2.3.1.2. install other servers
To install k3s on the other controlplane nodes (in this example control-plane-hel1 and control-plane-ngb1), run the following command on the server:
```bash
curl -sfL https://get.k3s.io | \
INSTALL_K3S_VERSION="v1.25.0-rc1+k3s1" \
K3S_TOKEN="K3S_TOKEN_HERE" \
INSTALL_K3S_EXEC="server \
--disable-cloud-controller \
--disable servicelb \
--disable traefik \
--disable local-storage \
--disable metrics-server \
--node-name="$(hostname -f)" \
--cluster-cidr=10.100.0.0/16 \
--etcd-expose-metrics=true \
--kube-controller-manager-arg="bind-address=0.0.0.0" \
--kube-proxy-arg="metrics-bind-address=0.0.0.0" \
--kube-scheduler-arg="bind-address=0.0.0.0" \
--node-taint CriticalAddonsOnly=true:NoExecute \
--kubelet-arg="cloud-provider=external" \
--advertise-address=$(hostname -I | awk '{print $2}') \
--node-ip=$(hostname -I | awk '{print $2}') \
--node-external-ip=$(hostname -I | awk '{print $1}') \
--flannel-iface=ens10 \
--tls-san=LOADBALANCER_PUBLIC_IP_HERE \
--tls-san=10.0.0.100 \
--tls-san=10.1.0.1 \
--tls-san=10.1.1.1 \
--tls-san=10.1.2.1 \
--server https://10.0.0.100:6443" sh -
```
Please replace the `K3S_TOKEN_HERE` with the token you created in step [2.1.1](#211-create-k3s-token) and the `LOADBALANCER_PUBLIC_IP_HERE` with the public ip of the loadbalancer for the controlplane created in step [2.1.4](#214-create-load-balancers).  
This installation also disables and customises many parameters to fit the needs of this setup. The controlplanes will communicate using the private-ip of the controlplane loadbalancer. 

### 2.3.2. setup kubectl
To communicate with the kubernetes cluster we use kubectl on our local machine, which we setup in step [1.4.3](#143-kubectl).  
For the authentication between your local machine and the k3s cluster, kubectl uses tokens. These tokens are stored in the kubeconfig file. 
Run the following command on your local machine to copy the kubeconfig file from one of the controlplane hosts to your local machine:
```bash
scp root@CONTROLPLANE_PUBLIC_IP_HERE:/etc/rancher/k3s/k3s.yaml ~/.kube/config
```
Please replace the `CONTROLPLANE_PUBLIC_IP_HERE` with the public ip of one of the controlplane hosts.

To replace the localhost ip used in the kubectl file with the public ip of the loadbalancer run the following command. Please replace the `CONTROLPLANE_PUBLIC_IP_HERE` with the public ip of the loadbalancer for the controlplane.
```bash
sed -i 's/127.0.0.1/167.235.216.181/' ~/.kube/config
```

As last step change the access rights to the kubeconfig file. Otherwise kubectl will not use the config file because the access rights are too open. 
```bash
chmod 600 ~/.kube/config
```

To check if the communication between the hosts and the local machine works, run the following command on your local machine:
```bash
kubectl get nodes
```
You should see 3 controlplane nodes in the output. 

# 3. Deployment
After the steps above we got a working kubertenes cluster with a loadbalanced, high-available controlplane and communication between our local machine and the cluster.  
In this step we will setup all needed deployments for the cluster to work poperly. This step will not cover the deployment of the applications itself, but only the needed infrastructure.

## 3.1. cloud-controller-manager
The first step is to deploy the cloud-controller-manager. This is needed to manage the cloud resources like loadbalancers, volumes and so on. This is the integration of the hetzner cloud api into the kubernets cluster. 

### 3.1.1. setup secret
The first step is to create a kubernetes secret with our cloud api token that the cloud-controller-manager will use to authenticate against the hetzner cloud api.  
We have created the token in step [1.2.1](#121-create-cloud-api-token).  
In my example configuration I have named the token `cloud-controller-manager` in the hetzner cloud. 

You also need the network-id from your private network. To get the id you can either copy the id from the hetzner cloud webinterface or copy the id from the following command:
```bash
hcloud network list
```

Copy the [secrets file](deployments/ccm/secret.yml) for the cloud-controller-manager to your local machine and replace the `CLOUD_API_TOKEN_HERE` with the token you created in step [1.2.1](#121-create-cloud-api-token) (in this example named as `cloud-controller-manager`) and the `NETWORK_ID_HERE` with the id of your private network as explaned above.  

Apply the secret to the kubernetes cluster by running the following command on your local machine:
```bash
kubectl apply -f deployments/ccm/secret.yml
```

### 3.1.2. deploy ccm
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

## 3.2. cloud-volume driver
To use hetzner cloud volumes as persistent volume claims in kubernetes, we need to deploy the cloud-volume driver. The driver will than handle the volumes claims and create the volumes in hetzner cloud.  
You can find more about the driver on the official [hetzner-csi](https://github.com/hetznercloud/csi-driver) github repository. 

### 3.2.1. setup secret
Similar to the ccm in step [3.1.1](#311-setup-secret), we need to create a secret for the cloud-volume driver. Replace the `CLOUD_API_TOKEN_HERE` in the [secret file](deployments/csi/secret.yml) with the token you created in step [1.2.1](#121-create-cloud-api-token) (in this example named as `container-storage-interface`).

Apply the secret to the kubernetes cluster by running the following command on your local machine:
```bash
kubectl apply -f deployments/csi/secret.yml
```

### 3.2.2. deploy hcloud-csi
Download the latest version of the storage driver deployment into the `deployments/csi` folder on your local machine:
```bash
wget wget https://raw.githubusercontent.com/hetznercloud/csi-driver/v1.6.0/deploy/kubernetes/hcloud-csi.yml -O deployments/csi/deployment.yml
```

Edit the deployment file and replace the secret name. You can use the following command to do this:
```bash
sed -i 's/^.\{18\}name: hcloud-csi$/                  name: hetzner_container_storage_interface/' deployments/csi/deployment.yml
```

You can deploy the cloud controller manager with the following command from your local machine:
```bash
kubectl apply -f deployments/ccm/deployment.yml
```

After this step you should see pods comming up in the cluster. To validate the starting pods, run the following command:
```bash
kubectl get pods -n kube-system
```
You have to use the kube-system namespace here, because the volume-driver is deployed in this namespace.

## 3.3. deploy upgrade-controller
To upgrade the kubernetes cluster, we need to deploy the upgrade-controller. This controller will check for new kubernetes versions and upgrade the cluster if a new version is available. You can deploy different update strategies to the cluster to keep a working cluster during the upgrade.

You can download the latest version of the upgrade-controller deployment into the `deployments/upgrade-controller` folder on your local machine:
```bash
wget https://github.com/rancher/system-upgrade-controller/releases/latest/download/system-upgrade-controller.yaml -O deployments/upgrade-controller/deployment.yml
```

You can deploy the upgrade-controller with the following command from your local machine:
```bash
kubectl apply -f deployments/upgrade-controller/deployment.yml
```

## 3.4. traefik
We will use traefik in this example as "edge router" and ingress controller. You can find more about traefik on the official [traefik](https://traefik.io/) website. 

### 3.4.1. prerequisites
You need the helm repository from traefik added to your local machine. You can add the repository with the following command:
```bash
helm repo add traefik https://helm.traefik.io/traefik
helm repo update
```

To separate the trafik installation from other deployments we create an own namespace for the trafik pods with the following command:
```bash
kubectl create namespace traefik
```

### 3.4.2. configure helm values
Copy the [traefik values file](deployments/traefik/values.yml) to your local machine. The file content fits the needs of this example, if you changed names from hetzner services or ip-ranges please review the file and change the values.

### 3.4.3. deploy workload
Finally install trafik with the following command run from your local machine:
```bash
helm install --namespace=traefik traefik traefik/traefik --values=deployments/traefik/values.yml
```

To validate all running services in the cluster, run the following command:
```bash
kubectl get svc --all-namespaces -o wide
```

### 3.4.4. setup default middleware
Copy the [default middleware](deployments/traefik/default-middleware.yml) file to your local machine. Please review the file and change the values to fit your personal needs. 

To apply the default middleware, run the following kubectl command:
```bash
kubectl apply -f deployments/traefik/default-middleware.yml
```

### 3.4.5. dashboard
To visit all routes traefik provides a dashboard. In the next steps we will create authentication values for the dashboard, a dashboard middleware and the ingressroute to serve traffic to the dashboard.

#### 3.4.5.1. create basic auth
Run the following command on your local machine to install the apache2 utilities. With this package you get access to htpassword which we will use now to generate the basic auth credentials.
```bash
apt install apache2-utils
```

To generate a base64 encoded combination of the username and password, run the following command on your local machine:
```bash
htpasswd -nb USERNAME PASSWORD | openssl base64
```
Replace `USERNAME` with your username and `PASSWORD` with your password.  
Copy the base64 encoded output into the [dashboard-secret]() file where it says `BASE64_ENCODED_USER_AND_PASSWORD_HERE`. 

As final step apply the dashboard-secret to the kubernetes cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-secret.yml
```

#### 3.4.5.2. setup middleware
To connect the traefik dashboard with the basic auth created in the previous step we need to create a middleware. Copy the [dashboard middleware](deployments/traefik/dashboard-middleware.yml) file to your local machine. 

Apply the middleware to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-middleware.yml
```

#### 3.4.5.3. create IngressRoute
To serve traffic to the dashboard we need to create an IngressRoute. Copy the [dashboard ingressroute](deployments/traefik/dashboard-ingressroute.yml) file to your local machine.  

Edit the file and replace the `traefik.example.com` host with your domain name you want to use for traefik.  
The tls setting should be commented out, this will be added when cert-manager is installed and configured. 

Apply the ingress route to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-ingressroute.yml
```

Connect to your traefik domain (in this example `traefik.example.com`) and login with your basic auth credentials you've setup in step [3.4.5.1](#3451-create-basic-auth). You should see the traefik dashboard with the default middlewares and services. 

## 3.5. cert-manager
We will use cert-manager as central certificate manager for all certificates in the cluster. You can find more about cert-manager on the official [cert-manager](https://cert-manager.io/) website.  
Cert-manager will use the [letsencrypt](https://letsencrypt.org/) service to issue certificates for the cluster. The certificates get validated through the dns01 acme challenge, described in the [dns-provider step 1.3](#13-dns-provider). 

### 3.5.1. prerequisites
Similar to traefik we will also use helm to install cert-manager to our cluster. You need the helm repository from cert-manager added to your local machine. You can add the repository with the following command:
```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

And we also create a separate namespace for cert-manager with the following command:
```bash
kubectl create namespace cert-manager
```

Because kubernetes does not know about certificates in the default installation we need to create a custom resource definition for certificates. Run the following command to download and apply the custom resource definitions:
```bash
wget https://github.com/cert-manager/cert-manager/releases/download/v1.9.1/cert-manager.crds.yaml -O deployments/cert-manager/crds.yml
kubectl apply -f deployments/cert-manager/crds.yml
```

You can try to get information about certificates now with the following command:
```bash
kubectl get certificates
```
Before adding the crds kubernetes will return an error that the resource of the type `certificates` is not known. After adding the crds the command should return an empty list.

### 3.5.2. configure helm values
Copy the [cert-manager values file](deployments/cert-manager/values.yml) to your local machine. Edit the file contents if you want to change the dns-servers that are used to validate the dns01 challenge. In this example we will use cloudflare-dns (1.1.1.1) and quad9 (9.9.9.9). 

### 3.5.3. deploy workload
To deploy the workload with helm run the following command on your local machine:
```bash
helm install cert-manager jetstack/cert-manager --namespace cert-manager --values=deployments/cert-manager/values.yml --version v1.9.1
```

To see the pods comming up run the following command:
```bash
kubectl get pods --namespace cert-manager
```

### 3.5.4. certificates
To issue certificates you need different resources. The certificate-issuer (company that issues the certificate), the certificate-request (what certificate you want to issue) and the certificate (the actual certificate). In this example we will first use the letsencrypt staging issuer to issue test certificates for the domains we want to use and switch to the letsencrypt production environment if everything works.

#### 3.5.4.1. create Cloudflare token
As described in the step [1.3.3](#133-create-token) we've created a token for cloudflare to allow cert-manager to update the dns records. This token will be put into a kubernetes secret. 

Copy the [cloudflare secret](deployments/cert-manager/cloudflare-secret.yml) file to your local machine. Edit the file and replace the `CLOUDFLARE_TOKEN_HERE` with the token you've created previously.

Apply the secret to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/cloudflare-secret.yml
```

#### 3.5.4.2. letsencrypt staging
As described previously we first use staging certificates to test our environment because the production api from letsencrypt is rate limited.

##### 3.5.4.2.1. create CerificateIssuer
Copy the file [letsencrypt staging issuer](deployments/cert-manager/letsencrypt-staging-issuer.yml) to your local machine. Edit the file and replace the following values:
  * `certificate@example.com` with your email address you want to use for letsencrypt
  * `cloudflare@example.com` with your email address you use to login to cloudflare
  * `example.com` with your zone name(s) inside cloudflare

Apply the issuer to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/letsencrypt-staging-issuer.yml
```

##### 3.5.4.2.2. create Certificate
The next step is to create a certificate. Copy the [example-staging-certificate](deployments/cert-manager/example-com-staging-tls.yml) to your local machine and replace the domain with your needed domains. You can add multiple domains or use the certificate as wildcard certificate like its shown in the example.  

Attention: The certificate will be created in the namespace trafik to add it to the traefik dashboard as test route. Certificates need to be in the same namespace as the ingressroute.

Apply the certificate to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/example-com-staging-tls.yml
```

You can see the certificates getting requested with the following commands:
```bash
kubectl get challenges --namespace=traefik
kubectl get certificates --namespace=traefik
```

##### 3.5.4.2.3. add certificate to traefik
As final step you can add the certificate to the traefik dashboard. Reopen the [traefik dashboard ingressroute](deployments/traefik/dashboard-ingressroute.yml) and uncomment the tls section. Replace the `example.com` with your domain and apply the ingressroute to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-ingressroute.yml
```

Open the dashboard webpage and open the certificate details and check if the certificate is issued by letsencrypt.  
Remember: We are using a staging (not valid) certificate, so dont worry if you get a warning in your browser. 

#### 3.5.4.3. letsencrypt production
If everything works with the staging certificate we can switch to the production environment. 

You can delete the old staging certificate with the following commands:
```bash
kubectl delete -f example-com-staging-tls.yml --namespace=traefik
```

##### 3.5.4.3.1. create CerificateIssuer
The setup will be similar to the staging environment. Copy the [issuer file](deployments/cert-manager/letsencrypt-production-issuer.yml) to your local machine. Edit the file and replace the following values:
  * `certificate@example.com` with your email address you want to use for letsencrypt
  * `cloudflare@example.com` with your email address you use to login to cloudflare
  * `example.com` with your zone name(s) inside cloudflare

Apply the issuer to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/letsencrypt-production-issuer.yml
```

##### 3.5.4.3.2. create Certificate
Now we will create separate certificates for traefik and all other pods. In this example i will only show the creation of a production certificate for trafik but you can change the deployment file to fit your special needs. 

Copy the [traefik production certificate](deployments/cert-manager/traefik-example-com-tls.yml) to your local machine and replace the domain and the internal certificate name to fit your traefik domain.

Apply the certificate to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/traefik-example-com-tls.yml
```

You can see the certificates getting requested with the following commands:
```bash
kubectl get challenges --namespace=traefik
kubectl get certificates --namespace=traefik
```

##### 3.5.4.3.3. add certificate to traefik
You can add the production certificate to traefik by editing the [traefik dashboard ingressroute](deployments/traefik/dashboard-ingressroute.yml) and change the tls section to the new production certificate name entered in the deployment file above. 

Apply the changed ingressroute to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-ingressroute.yml
```

## 3.6. deploy metrics-server
## 3.7. cluster-autoscaler
### 3.7.1. create cloud-init configuration
### 3.7.2. create secret
### 3.7.3. create autoscaler image
### 3.7.4. create repository secret
### 3.7.5. configure deployment
### 3.7.6. deploy workload
## 3.8. example horizontal pod autoscaler
### 3.8.1. example application
### 3.8.2. scale pods
### 3.8.3. delete deployment

# Credits
Huge thank you to many people and git repos where I got my information and commands from.  
Special thanks to:
* [Techno Tim](https://github.com/techno-tim)
* [The DevOps Guy](https://github.com/marcel-dempers)
* [Hetzner Development Team](https://github.com/hetznercloud/)