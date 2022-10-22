# Servers (VMs)
After creating the servers for the controlplane, we have to configure the operating system.  
The servers get installed with a fresh copy of debian-11 but we need to install some additional software and do updates. 

## Install Updates
First install all updates on the servers. To do this, run the following commands on all servers:

!!! warning
    You have to do this on all servers, created in the previous step.  
    In this guide you will have to do this on 3 servers (`k3s-controlplane-hel1-1`, `k3s-controlplane-fsn1-1` and `k3s-controlplane-nbg1-1`)

```bash
apt update
apt upgrade -y
```

## Set Timezone
Set the correct timezone on all servers. Do this by running the following command on all servers:

!!! warning
    You have to do this on all servers, created in the previous step.  
    In this guide you will have to do this on 3 servers (`k3s-controlplane-hel1-1`, `k3s-controlplane-fsn1-1` and `k3s-controlplane-nbg1-1`)

!!! danger "Replace values"
    You have to replace `YOUR_TIMEZONE` with your timezone.

```bash
timedatectl set-timezone YOUR_TIMEZONE #(1)!
```

1. Replace `YOUR_TIMEZONE` with your timezone.

## Install packages
To configure the hosts, we need to install some packages.  
To do this, run the following commands on all servers:

!!! warning
    You have to do this on all servers, created in the previous step.  
    In this guide you will have to do this on 3 servers (`k3s-controlplane-hel1-1`, `k3s-controlplane-fsn1-1` and `k3s-controlplane-nbg1-1`)

```bash
apt install apparmor apparmor-utils -y #(1)!
```

1. `apparmor` and `apparmor-utils` are needed as kernel security module.