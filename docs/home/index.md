# Home

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