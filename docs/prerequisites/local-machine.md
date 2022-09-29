# Local Machine
In the last preparation step, we have to setup our local machine. As local machine you need a linux-host. You can install it directy to your host, use a virtual machine or - as i do - use wsl, the windows subsystem for linux.  

## hcloud
To control the hetzner cloud from the command line you need hcloud, a tool by hetzner. You can find more information [here](https://github.com/hetznercloud/cli).

### install hcloud
You can install hcloud with [homebrew](https://brew.sh/).  
Run `brew install hcloud` to install hcloud to your system. 

### setup hcloud context
To communicate with your hetzner cloud project from [the previous step](../hetzner/#create-project) you created an api-token in [a previous step](../hetzner/#create-api-tokens). In my example i named it `command-line-interface`.  
To link the cloud project with the hcloud application by using the api-token, you have to create an hcloud-context. You can manage different cloud-projects with different contexts.  
To create a new context type `hcloud context create [NAME]` and paste your previously saved api-token.  
You can see all contexts with `hcloud context list` and set your used context with `hcloud context use [NAME]`. 

## Helm
To install packages to kubernetes you need helm on your local machine.  
To install helm, visit the [official installation manual](https://helm.sh/docs/intro/install/#from-script). 

## kubectl
To administrate the kubernetes cluster you also need kubectl, a command line interface to control kubernetes clusters.  
You can visit the [kubernets documentation](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-kubectl-binary-with-curl-on-linux) for installation steps.  

## go
In [the autoscaler step](../../deployment/cluster-autoscaler/#create-autoscaler-image) we need to build a custom docker image for the autoscaler. To build the image we need go.

Install go to your local machine with the following commands:
```bash
wget https://go.dev/dl/go1.19.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.19.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
rm go1.19.linux-amd64.tar.gz
```

You can check the installation with `go version`. 

## docker
You need docker on your local machine to build a docker image in the [autoscaler step](../../deployment/cluster-autoscaler/#create-autoscaler-image).  
Because the docker installation can be done via different ways (scripts, package-manager, docker-desktop in wsl) i will skip this step in this tutorial. 
You can find information about getting docker [here](https://docs.docker.com/get-docker/). 

You can check the installation with `docker version`. 

You should login to your container registry created in [a prerequisite step](../container-repository/#create-account) with the following command:
```bash
docker login -u DOCKER-USERNAME -p DOCKER_PASSWORD
```
Replace `DOCKER_USERNAME` with your docker username and `DOCKER_PASSWORD` with your password.