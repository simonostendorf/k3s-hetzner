# High-Available k3s-Cluster using Hetzner Cloud

## Introduction
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

## ToDo
* Deploy kube-prometheus-stack (prometheus, grafana, alertmanager, node-exporter etc.) to collect and visualize metrics from nodes and pods
* Setup vertical pod autoscaler to automaticly update pod resources requests and limits
* Setup goldilocks as dashboard for the vertical pod autoscaler
* Setup argo-cd to automaticly deploy workloads as part of the ci/cd pipeline

## Steps
1. [Prerequisites](#prerequisites)  
1.1 [Hetzner](#prerequisites-hetzner)  
1.1.1 [create cloud account](#prerequisites-hetzner-account)  
1.1.2 [create project](#prerequisites-hetzner-project)  
1.1.3 [create API token(s)](#prerequisites-hetzner-token)  
1.1.4 [upload ssh-key(s)](#prerequisites-hetzner-sshkeys)  
1.2 [container repository](#prerequisites-containerrepo)  
1.2.1 [create account](#prerequisites-containerrepo-account)  
1.2.2 [create token](#prerequisites-containerrepo-token)  
1.3 [Local machine](#prerequisites-local)  
1.3.1 [hcloud](#prerequisites-local-hcloud)  
1.3.1.1 [install hcloud](#prerequisies-local-hcloud-install)  
1.3.1.1 [setup hcloud context](#prerequisies-local-hcloud-context)  
1.3.2 [Helm](#prerequisites-local-helm)  
2. [Installation](#installation)  
2.1 [Hetzner](#installation-hetzner)  
2.1.1 [create placement groups](#installation-hetzner-placementgroups)  
2.1.2 [create private network](#installation-hetzner-privatenetwork)  
2.1.3 [create servers](#installation-hetzner-servers)  
2.1.4 [create load balancers](#installation-hetzner-loadbalancers)  
2.2 [Servers](#installation-servers)  
2.2.1 [install updates](#installation-servers-updates)  
2.2.2 [set timezone](#installation-servers-timezone)  
2.2.3 [install packages](#installation-servers-packages)  
2.3 [k3s](#installation-k3s)  
2.3.1 [control-plane](#installation-k3s-controlplane)  
2.3.1.1 [install first server](#installation-k3s-controlplane-first)  
2.3.1.1 [install other servers](#installation-k3s-controlplane-others)  
2.3.2 [setup kubectl](#installation-k3s-kubectl)  
3. [Deployments](#deployment)  
3.1 [cloud-controller-manager](#deployment-ccm)  
3.1.1 [setup secret](#deployment-ccm-secret)  
3.1.2 [deploy ccm](#deployment-ccm-deployment)  
3.2 [cloud-volume driver](#deployment-hcloudcsi)  
3.2.1 [setup secret](#deployment-hcloudcsi-secret)  
3.2.2 [deploy hcloud-csi](#deployment-hcloudcsi-deployment)  
3.3 [install upgrade-controller](#deployment-upgradecontroller)  
3.4 [traefik](#deployment-traefik)  
3.4.1 [prerequisites](#deployment-traefik-prerequisites)  
3.4.2 [configure helm values](#deployment-traefik-configuration)  
3.4.3 [deploy workload](#deployment-traefik-deployment)  
3.4.4 [setup default middleware](#deployment-traefik-defaultmiddleware)  
3.4.5 [dashboard](#deployment-traefik-dashboard)  
3.4.5.1 [create basic auth](#deployment-traefik-dashboard-basicauth)  
3.4.5.2 [setup middleware](#deployment-traefik-dashboard-middleware)  
3.4.5.3 [create IngressRoute](#deployment-traefik-dashboard-ingressroute)  
3.5 [cert-manager](#deployment-certmanager)  
3.5.1 [prerequisites](#deployment-certmanager-prerequisites)  
3.5.2 [configure helm values](#deployment-certmanager-configuration)  
3.5.3 [deploy workload](#deployment-certmanager-deployment)  
3.5.4 [certificates](#deployment-certmanager-certificates)  
3.5.4.1 [create Cloudflare token](#deployment-certmanager-certificates-cloudflare)  
3.5.4.2 [letsencrypt staging](#deployment-certmanager-certificates-letsencryptstaging)  
3.5.4.2.1 [create CertificateIssuer](#deployment-certmanager-certificates-letsencryptstaging-issuer)  
3.5.4.2.2 [create Certificate](#deployment-certmanager-certificates-letsencryptstaging-cert)  
3.5.4.2.3 [add certificate to traefik](#deployment-certmanager-certificates-letsencryptstaging-traefik)  
3.5.4.3 [letsencrypt production](#deployment-certmanager-certificates-letsencrypt)  
3.5.4.3.1 [create CertificateIssuer](#deployment-certmanager-certificates-letsencrypt-issuer)  
3.5.4.3.2 [create Certificate](#deployment-certmanager-certificates-letsencrypt-cert)  
3.5.4.3.3 [add certificate to traefik](#deployment-certmanager-certificates-letsencrypt-traefik)  
3.6 [deploy metrics-server](#deployment-metricsserver)  
3.7 [cluster-autoscaler](#deployment-clusterautoscaler)  
3.7.1 [create cloud-init configuration](#deployment-clusterautoscaler-cloudinit)  
3.7.2 [create secret](#deployment-clusterautoscaler-secret)  
3.7.3 [create autoscaler image](#deployment-clusterautoscaler-createimage)  
3.7.4 [create repository secret](#deployment-clusterautoscaler-secret)  
3.7.5 [configure deployment](#deployment-clusterautoscaler-configuration)  
3.7.6 [deploy workload](#deployment-clusterautoscaler-deployment)  
3.8 [example horizontal pod autoscaler](#deployment-hpa)  
3.8.1 [example application](#deployment-hpa-app)  
3.8.2 [scale pods](#deployment-hpa-scale)  
3.8.3 [delete deployment](#deployment-hpa-delete)  

## Credits
Huge thank you to many people and git repos where I got my information and commands from.  
Special thanks to:
* [Techno Tim](https://github.com/techno-tim)
* [The DevOps Guy](https://github.com/marcel-dempers)
* [Hetzner Development Team](https://github.com/hetznercloud/)