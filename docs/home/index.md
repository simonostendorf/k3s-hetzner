# Home

<img src="https://cncf-branding.netlify.app/img/projects/k3s/horizontal/color/k3s-horizontal-color.svg" alt="k3s-logo" width="150"/>
<img src="../../assets/home/meets.png" alt="meets" width="130"/>
<img src="https://www.hetzner.com/assets/Uploads/hetzner-logo3.svg" alt="Hetzner-logo" width="370"/>

## Introduction
In this documentation you will find a step by step solution to deploy a high-available, auto scalable and loadbalanced [k3s](https://k3s.io/) cluster to servers inside the Hetzner-Cloud.  

This guide covers:

  * Prerequisites
    * Setting up [Hetzner](https://hetzner.com) account (including cloud project, api-tokens and ssh-keys)
    * Setting up [Docker-Hub](https://hub.docker.com) as private container repository for custom images (e.g. cluster-autoscaler)
    * Setting up [CloudFlare](https://www.cloudflare.com) as dns provider for dns01 acme challenge 
    * Installing all requirements on your local development machine ([hcloud command line](https://github.com/hetznercloud/cli), [helm](https://helm.sh/), [kubectl](https://kubernetes.io/docs/reference/kubectl/kubectl/), [go](https://go.dev/) and [docker](https://www.docker.com/))
  * Installation
    * Setting up [placement groups](https://docs.hetzner.com/cloud/placement-groups/) to separate hetzner cloud servers
    * Setting up [private networks](https://docs.hetzner.com/cloud/networks/) for communication between servers 
    * Setting up three k3s-servers (controlplane) in high-available mode
    * Create a hetzner [loadbalancer](https://docs.hetzner.com/cloud/load-balancers/) to loadbalance the kubernetes-api
    * Create a hetzner [loadbalancer](https://docs.hetzner.com/cloud/load-balancers/) to loadbalance the services exposed to the ingress
    * Install all required packages to the hosts and configure them properly
    * Automatic install and configuration of k3s with one single command
  * Deployment
    * Deploy the hetzner [cloud-controller-manager](https://github.com/hetznercloud/hcloud-cloud-controller-manager/) to the cluster to integrate the hetzner api into the k8s cluster
    * Deploy the hetzner [container-storage-interface](https://github.com/hetznercloud/csi-driver) to the cluster to use hetzner cloud volumes as persistent volume claim inside k8s
    * Deploy the [cluster-autoscaler](https://github.com/kubernetes/autoscaler/) to the cluster and configure it to use hetzner cloud servers for automatic scaleup and scaledown of nodes
    * Deploy the [metrics-server](https://github.com/kubernetes-sigs/metrics-server) to get metrics from pods and nodes and enable autoscaling of nodes and pods
    * Deploy the [system-upgrade-controller](https://github.com/rancher/system-upgrade-controller) to use automated upgrade plans
    * Deploy and configure [traefik](https://traefik.io/traefik/) as ingress controller
    * Deploy and configure [cert-manager](https://cert-manager.io/) to use [letsencrypt](https://letsencrypt.org/) certificates for all services exposed to the internet
    * Setting up the traefik dashboard with basic auth and certificates
    * Give an example of [horizontal pod autoscaling](https://kubernetes.io/de/docs/tasks/run-application/horizontal-pod-autoscale/) to scale pods based on cpu usage

## Files
By following this guide you will need deployment files to change them to fit your needs and to deploy them to your cluster.  
You will find the the original files references in the download command. 

## Disclaimer
This guide is not an official guide from Hetzner or k3s.  
If you want help, do not contant the official support of Hetzner or k3s. Instead you can open an issue in the [github repository](https://github.com/simonostendorf/k3s-hetzner/issues).