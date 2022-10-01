# k3s
In this step we will finally install k3s on the servers.

## Token
First we need to generate a token for the server to join the cluster. This token is used to authenticate the server to the cluster. We can generate a token with the following command:
```bash
openssl rand -hex 64
```

Be shure to save the token in a **save place**, you will need it later to join the servers and agents to the cluster. 

## control-plane
To install the k3s control-plane software on the control-plane host, we have to separate the installation to the first installed control-plane and the other control-planes.

### Install first Server
To install k3s on the first control-plane node (in this example control-plane-fsn1-1), run the following command on the server:

!!! warning "Replace values"
    Please replace the `K3S_TOKEN_HERE` with your [previously created k3s-token](#token) and the `LOADBALANCER_PUBLIC_IP_HERE` with the public ip of the loadbalancer for the controlplane created in [the hetzner step](../hetzner/#create-load-balancers).  

```bash hl_lines="3 22"
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

This installation disables or customises many parameters to fit the needs of this setup.

### Install other Servers
To install k3s on the other controlplane nodes (in this example control-plane-hel1-1 and control-plane-ngb1-1), run the following command on the server:

!!! warning "Replace values"
    Please replace the `K3S_TOKEN_HERE` with your [previously created k3s-token](#token) and the `LOADBALANCER_PUBLIC_IP_HERE` with the public ip of the loadbalancer for the controlplane created in [the hetzner step](../hetzner/#create-load-balancers).  

```bash hl_lines="3 22"
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

This installation also disables and customises many parameters to fit the needs of this setup. The controlplanes will communicate using the private-ip of the controlplane loadbalancer. 

## Setup kubectl
To communicate with the kubernetes cluster we use kubectl on our local machine, which we setup in the [local machine step](../../prerequisites/local-machine/#kubectl).  
For the authentication between your local machine and the k3s cluster, kubectl uses tokens. These tokens are stored in the kubeconfig file. 
Run the following command on your local machine to copy the kubeconfig file from one of the controlplane hosts to your local machine:

!!! warning "Replace values"
    Please replace the `CONTROLPLANE_PUBLIC_IP_HERE` with the public ip of one of the controlplane hosts (for example k8s-controlplane-hel1-1).

```bash
scp root@CONTROLPLANE_PUBLIC_IP_HERE:/etc/rancher/k3s/k3s.yaml ~/.kube/config
```

To replace the localhost ip used in the kubectl file with the public ip of the loadbalancer run the following command. 

!!! warning "Replace values"
    Please replace the `LOADBALANCER_PUBLIC_IP_HERE` with the public ip of the loadbalancer for the controlplane.

```bash
sed -i 's/127.0.0.1/LOADBALANCER_PUBLIC_IP_HERE/' ~/.kube/config
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