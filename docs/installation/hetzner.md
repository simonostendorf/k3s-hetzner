# Hetzner
To provide servers, a network-connection and load-balancers we will use the hetzner cloud. In this step we will create all parts for the hetzner infrastructure. 

## Create Placement-Groups
To separate all servers from each other, we will create placement groups for the servers. One placement group will be for one server-role for one location. This will result in 6 placement groups (3 locations (hel-1, fsn-1, nbg-1) * 2 server-roles (server and agent)) 
To create all placement groups, run the following commands on your local machine:  
```bash
# Create placement group for servers in hel-1
hcloud placement-group create --type spread --name k8s-control_plane-hel1 --label k8s-role=control_plane --label location=hel1

# Create placement group for servers in fsn-1
hcloud placement-group create --type spread --name k8s-control_plane-fsn1 --label k8s-role=control_plane --label location=fsn1

# Create placement group for servers in nbg-1
hcloud placement-group create --type spread --name k8s-control_plane-nbg1 --label k8s-role=control_plane --label location=nbg1

# Create placement group for agents in hel-1
hcloud placement-group create --type spread --name k8s-agent-hel1 --label k8s-role=agent --label location=hel1

# Create placement group for agents in fsn-1
hcloud placement-group create --type spread --name k8s-agent-fsn1 --label k8s-role=agent --label location=fsn1

# Create placement group for agents in nbg-1
hcloud placement-group create --type spread --name k8s-agent-nbg1 --label k8s-role=agent --label location=nbg1
``` 

!!! missing "Attention"
    The placement groups used for the agents are not used yet by the cluster-autoscaler. 

The commands will create the following placement groups:

  * 3 placement groups for the control-plane servers with the name `k8s-control_plane-{location}` and the labels `k8s-role=control_plane` and `location={location}`
  * 3 placement groups for the agents with the name `k8s-agent-{location}` and the labels `k8s-role=agent` and `location={location}`

The `{location}` will be replaced with the location of the placement group. The locations are `hel1`, `fsn1` and `nbg1`.

## Create private Network
We will use a hetzner cloud network to connect all servers to each other ane enable the load-balancers to connect to the private ips of the servers.  
To create the private network for the servers run the following command on your local machine:
```bash
hcloud network create --name k8s --ip-range 10.0.0.0/8 --label k8s-role=control_plane-agent --label location=hel1-fsn1-nbg1
```
The command will create a network with the name `k8s` and the labels `k8s-role=control_plane-agent` and `location=hel1-fsn1-nbg1`.

To create the separate subnets inside this network, run the following commands on your local machine:
```bash
# Create subnet for loadbalancers (for kubernetes-api (controlplane) and ingress (services))
hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.0.0.0/24

# Create subnet for servers (control-plane) in hel-1
hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.1.0.0/24

# Create subnet for servers (control-plane) in fsn-1
hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.1.1.0/24

# Create subnet for servers (control-plane) in nbg-1
hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.1.2.0/24

# Create subnet for agents in hel-1
hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.2.0.0/24

# Create subnet for agents in fsn-1
hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.2.1.0/24

# Create subnet for agent in nbg-1
hcloud network add-subnet k8s --network-zone eu-central --type cloud --ip-range 10.2.2.0/24
```
The commands will create the following subnets:

  * 10.0.0.0/24 for the load balancers for the controlplane and agents
  * 10.1.0.0/24 for the controlplane in hel1
  * 10.1.1.0/24 for the controlplane in fsn1
  * 10.1.2.0/24 for the controlplane in nbg1
  * 10.2.0.0/24 for the agents in hel1
  * 10.2.1.0/24 for the agents in fsn1
  * 10.2.2.0/24 for the agents in nbg1

## Create Servers
To create the servers for the control-plane, run the following commands on your local machine:

!!! danger "Replace values"
    You have to replace the `--ssh-key SSH_KEY_NAME` with your ssh-key name you have uploaded in the prerequisite step.
    If you want to use **more than one ssh-key**, you can specify the ssh-key **parameter multiple times**.

```bash hl_lines="5 16 27"
# Create server for control-plane in hel-1
hcloud server create \
--datacenter hel1-dc2 \
--image debian-11 \
--ssh-key SSH_KEY_NAME \
--type cx21 \
--placement-group k8s-control_plane-hel1 \
--name k8s-controlplane-hel1-1 \
--label k8s-role=control_plane \
--label location=hel1

# Create server for control-plane in fsn-1
hcloud server create \
--datacenter fsn1-dc14 \
--image debian-11 \
--ssh-key SSH_KEY_NAME \
--type cx21 \
--placement-group k8s-control_plane-fsn1 \
--name k8s-controlplane-fsn1-1 \
--label k8s-role=control_plane \
--label location=fsn1

# Create server for control-plane in nbg-1
hcloud server create \
--datacenter nbg1-dc3 \
--image debian-11 \
--ssh-key SSH_KEY_NAME \
--type cx21 \
--placement-group k8s-control_plane-nbg1 \
--name k8s-controlplane-nbg1-1 \
--label k8s-role=control_plane \
--label location=nbg1
```

The commands will create a control plane node in each hetzner location with...

  * the name `k8s-controlplane-{location}-1`
  * the server type CX21 (2 cores, 4gb ram)
  * the image debian-11
  * the ssh-key added in [the prerequisite step](../../prerequisites/hetzner/#upload-ssh-keys)
  * the placement-groups created at the [top of this page](#create-placement-groups)
  * and the labels `k8s-role=control_plane` and `location={location}`.

To add the servers to the private network, run the following commands on your local machine:
```bash
hcloud server attach-to-network k8s-controlplane-hel1-1 --network k8s --ip 10.1.0.1
hcloud server attach-to-network k8s-controlplane-fsn1-1 --network k8s --ip 10.1.1.1
hcloud server attach-to-network k8s-controlplane-nbg1-1 --network k8s --ip 10.1.2.1
```
The commands will add the servers to the private network `k8s` (created in a previous step) and assign the following ips:

  * 10.1.0.1 to the control plane in hel1
  * 10.1.1.1 to the control plane in fsn1
  * 10.1.2.1 to the control plane in nbg1

See also network creation in [a previous step](#create-private-network).

## Create Loadbalancers
Kubernetes needs two loadbalancers. One for the control plane and one for the ingress. In this setup we will use external hardware loadbalancers from the hetzner cloud.

### Loadbalancer for control plane
So in this step we will create the loadbalancer for the control plane with executing the following commands on your local machine:
```bash
# Create loadbalancer for control plane
hcloud load-balancer create --algorithm-type round_robin --location fsn1 --name k8s-controlplane --type lb11 --label k8s-role=control_plane --label location=fsn1

# Attach the loadbalancer to the private network
hcloud load-balancer attach-to-network k8s-controlplane --network k8s --ip 10.0.0.100

# Add target servers to the loadbalancer
hcloud load-balancer add-target k8s-controlplane --label-selector k8s-role=control_plane --use-private-ip

# Create service for the loadbalancer
hcloud load-balancer add-service k8s-controlplane --destination-port 6443 --listen-port 6443 --protocol tcp
```
The commands will create the loadbalancer for the controlplane with the following configuration:

  * Name: `k8s-controlplane`
  * Location: `fsn1`
  * Type: `lb11` (max services: 5, max connections: 10000, max targets: 25)
  * Algorithm: `round_robin`
  * private ip `10.0.0.100` inside the previously created Network
  * labels `k8s-role = control_plane` and `location = fsn1`
  * add all servers with label `k8s-role = control_plane` as target
  * expose port `6443` for the control plane

### Loadbalancer for Ingress
In this step we will create the loadbalancer for the ingress with executing the following commands on your local machine:
```bash	
# Create loadbalancer for ingress
hcloud load-balancer create --algorithm-type round_robin --location nbg1 --name k8s-ingress --type lb11 --label k8s-role=agent --label location=nbg1

# Attach the loadbalancer to the private network
hcloud load-balancer attach-to-network k8s-ingress --network k8s --ip 10.0.0.200

# Add target servers to the loadbalancer
hcloud load-balancer add-target k8s-ingress --label-selector k8s-role=agent --use-private-ip
```

The commands will create the loadbalancer for the ingress with the following configuration:

  * Name: `k8s-ingress`
  * Location: `nbg1`
  * Type: `lb11` (max services: 5, max connections: 10000, max targets: 25)
  * Algorithm: `round_robin`
  * private ip `10.0.0.200` inside the previously created Network
  * labels `k8s-role = agent` and `location = nbg1`
  * add all servers with label `k8s-role = agent` as target
  * Loadbalancer will not expose any ports because the ingress controller will do that later automatically