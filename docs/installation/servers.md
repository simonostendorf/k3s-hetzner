# Servers (VMs)
After creating the servers we have to configure the operating system. 

## install updates
First install all updates on the servers. To do this, run the following commands on all servers (control-plane-fsn1, control-plane-ngb1, control-plane-hel1):
```bash
apt update
apt upgrade -y
```

## set timezone
Set the correct timezone on all servers. Do this by running the following command on all servers (control-plane-fsn1, control-plane-ngb1, control-plane-hel1):
```bash
timedatectl set-timezone Europe/Berlin
```
I will use the timezone Europe/Berlin in this guide. You can change this to your timezone.

## install packages
To allow everything on the host we need to install some packages. To do this, run the following commands on all servers (control-plane-fsn1, control-plane-ngb1, control-plane-hel1):
```bash
apt install apparmor apparmor-utils -y
```