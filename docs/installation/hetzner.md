# Hetzner
To provide servers, a network-connection and load-balancers we will use the hetzner cloud. In this step we will create all parts for the hetzner infrastructure. 

## create placement groups
To separate all servers from each other, we will create placement groups for the servers. One placement group will be for one server-role for one location.  
To create all placement groups, run the following commands on your local machine:  
```bash
hcloud placement-group create --type spread --name k8s-control_plane-hel1 --label k8s-role=control_plane --label location=hel1
hcloud placement-group create --type spread --name k8s-control_plane-fsn1 --label k8s-role=control_plane --label location=fsn1
hcloud placement-group create --type spread --name k8s-control_plane-nbg1 --label k8s-role=control_plane --label location=nbg1
```
The commands will create a placement group for each hetzner location with the name `k8s-control_plane-[LOCATION]` and the labels `k8s-role=control_plane` and `location=[LOCATION]`.  

**IMPORTANT:** agent placement groups are not used in the current configuration because of configuration problems with the cluster-autoscaler.
To create the placement groups for all agents, run these commands on your local machine:
```bash
hcloud placement-group create --type spread --name k8s-agent-hel1 --label k8s-role=agent --label location=hel1
hcloud placement-group create --type spread --name k8s-agent-fsn1 --label k8s-role=agent --label location=fsn1
hcloud placement-group create --type spread --name k8s-agent-nbg1 --label k8s-role=agent --label location=nbg1
```
The commands will create a placement group for each hetzner location with the name `k8s-agent-[LOCATION]` and the labels `k8s-role=agent` and `location=[LOCATION]` similar to the commands for the controlplane.

## create private network
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
hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.2.0.0/16 # agents (all locations)
```
The commands will create the following subnets:

  * 10.0.0.0/24 for the load balancers for the controlplane and agents
  * 10.1.0.0/24 for the controlplane in hel1
  * 10.1.1.0/24 for the controlplane in fsn1
  * 10.1.2.0/24 for the controlplane in nbg1
  * 10.2.0.0/16 for the agents in all locations

## create servers
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
  * the ssh-key added in [the prerequisite step](../../prerequisites/hetzner/#upload-ssh-keys)
  * the placement-groups created at the [top of this page](#create-placement-groups)
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

See also network creation in [a previous step](#create-private-network).

## create load balancers
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