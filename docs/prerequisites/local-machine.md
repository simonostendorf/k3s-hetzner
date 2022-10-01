# Local Machine
In the last preparation step, we have to setup our local machine. 

As local machine you need a linux-host. You can install it directy to your host, use a virtual machine or *- as i do -* use [wsl](https://learn.microsoft.com/de-de/windows/wsl/), the windows subsystem for linux.  

## Packages
To install the required packages, you can use the following commands:
```bash
apt install apache2-utils -y #(1)!
```

1. We need the apache2-utils package to generate the basic auth credentials for the traefik dashboard in a later step.

## hcloud
To control the hetzner cloud from the command line you need hcloud, a command-line tool by hetzner. You can find more information [here](https://github.com/hetznercloud/cli).

### Install hcloud
You can install hcloud with [homebrew](https://brew.sh/).  
To install homebrew visit their website or run the following command:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

As next step install hcloud to your system using homebrew: 
```bash
brew install hcloud
``` 

### Setup hcloud context
To communicate with your hetzner account you created a cloud project in the [hetzner prerequisite step](../hetzner/#create-project). You have also added an api-token in [a previous step](../hetzner/#create-api-tokens). 

In my example the token named `command-line-interface` is relevant for the hcloud-cli.

To link the cloud project with the hcloud application by using the api-token, you have to create a hcloud-context. You can manage different cloud-projects with different contexts.  
To create a new context type the following command and paste your api-token if it is asked:
```bash
hcloud context create [NAME] # (1)!
```

1. The name of the context. 
   You can choose any name you want.
   It is recommended to use the **name of the cloud project**.

You can see all contexts with `hcloud context list` and set your used context with `hcloud context use [NAME]`. 

Check that the hcloud-cli can connect to your cloud project by typing:
```bash
hcloud server list
```
You should get an empty list of servers, because we have not created any yet.

## Helm
To install packages to kubernetes you need helm on your local machine.  
To install helm run the following commands. You can also visit the [official installation manual](https://helm.sh/docs/intro/install/).
```bash
# Download latest helm install script
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3

# Change access rights to execute the script
chmod 700 get_helm.sh

# run the script to install helm
./get_helm.sh
``` 

Check if helm is installed correctly by running:
```bash
helm version
```

## kubectl
To administrate the kubernetes cluster from your local machine you also need kubectl, a command line interface to control kubernetes clusters.  
To install kubectl to your system, run the following commands or visit the [kubernets documentation](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) for installation steps:
```bash
# Download latest kubectl release
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Download kubectl checksum file
curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"

# Verify checksum file (output should be "kubectl: OK")
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check

# Finally install kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

Check if kubectl is installed correctly by running:
```bash
kubectl version --client
```

## go
In [the autoscaler step](../../deployment/cluster-autoscaler/#create-autoscaler-image) we need to build a custom docker image for the kubernetes cluster autoscaler. To build the image we need go.

Install go to your local machine with the following commands. You can also view the [official installation manual](https://go.dev/doc/install).
```bash
# Remove old go installations
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.19.1.linux-amd64.tar.gz

# Download latest go release
wget https://go.dev/dl/go1.19.1.linux-amd64.tar.gz

# Extract the archive
sudo tar -C /usr/local -xzf go1.19.1.linux-amd64.tar.gz

# Add go to the path
export PATH=$PATH:/usr/local/go/bin

# Remove downloaded archive
rm go1.19.1.linux-amd64.tar.gz
```

You can check the installation with:
```bash
go version
``` 

## Docker
You need docker on your local machine to build a docker image in the [autoscaler step](../../deployment/cluster-autoscaler/#create-autoscaler-image).  

### Install Docker
The installation of docker can be done in many different ways, i will show you the easiest way to install docker on your local machine using the following script:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```
You can also install docker using the package-manager or docker-desktop in wsl. You can find more installation steps in the [docker documentation](https://docs.docker.com/engine/install/). 

You can check the installation with `docker version`. 

### Login to Docker Hub
You should login to your container registry created in [a prerequisite step](../container-repository/#create-account) with the following command.  

!!! danger "Replace variables"
    Replace `DOCKER_USERNAME` with your docker username and `DOCKER_PASSWORD` with your writeable token (In this guide i named the token `local-machine`).

```bash
docker login -u DOCKER-USERNAME -p DOCKER_PASSWORD #(1)!
```

1. Your docker username and writeable token created in the container-registry step