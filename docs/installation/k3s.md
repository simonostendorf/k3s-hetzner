# k3s
In this step we will install k3s on the servers.

## control-plane
To install the k3s controlplane software on the controlplane host, we have to separate the installation to the first installed controlplane and the other controlplanes.

### install first server
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
Please replace the `K3S_TOKEN_HERE` with a secret and long token (save the token securly, you will need it later) and the `LOADBALANCER_PUBLIC_IP_HERE` with the public ip of the loadbalancer for the controlplane created in [the hetzner step](../hetzner/#create-load-balancers).  
This installation disables or customises many parameters to fit the needs of this setup.

### install other servers
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
Please replace the `K3S_TOKEN_HERE` with the token you created in [the previous step](#install-first-server) and the `LOADBALANCER_PUBLIC_IP_HERE` with the public ip of the loadbalancer for the controlplane created in [the hetzner step](../hetzner/#create-load-balancers).  
This installation also disables and customises many parameters to fit the needs of this setup. The controlplanes will communicate using the private-ip of the controlplane loadbalancer. 

## setup kubectl
To communicate with the kubernetes cluster we use kubectl on our local machine, which we setup in the [local machine step](../../prerequisites/local-machine/#kubectl).  
For the authentication between your local machine and the k3s cluster, kubectl uses tokens. These tokens are stored in the kubeconfig file. 
Run the following command on your local machine to copy the kubeconfig file from one of the controlplane hosts to your local machine:
```bash
scp root@CONTROLPLANE_PUBLIC_IP_HERE:/etc/rancher/k3s/k3s.yaml ~/.kube/config
```
Please replace the `CONTROLPLANE_PUBLIC_IP_HERE` with the public ip of one of the controlplane hosts.

To replace the localhost ip used in the kubectl file with the public ip of the loadbalancer run the following command. Please replace the `CONTROLPLANE_PUBLIC_IP_HERE` with the public ip of the loadbalancer for the controlplane.
```bash
sed -i 's/127.0.0.1/CONTROLPLANE_PUBLIC_IP_HERE/' ~/.kube/config
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