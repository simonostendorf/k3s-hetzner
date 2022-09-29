# Hetzner
## create cloud account
Create an account at the Hetzner Cloud Hosting portal.  
You can use [my ref-link](https://hetzner.cloud/?ref=QVP9EsLHwtNY) to get 20€ for free if you want. 

## create project
The autoscale cluster should sit in a **plain cloud project**.  
Login at [console.hetzner.cloud/projects](https://console.hetzner.cloud/projects) and create new project.  
The name of the project doesn't matter.  

<img src="../../assets/prerequisites/hetzner/create-project.png" width=50%>

## create API token(s)
Open the project and go to security and the api-tokens tab.  
Here you have to create **at least one api-token**.  
I created several ones to keep the different services seperated and logged what which service does. 
I created the following tokens:

  * `command-line-interface` (used for hcloud cli application on local machine)
  * `container-storage-interface` (used for persistent volume driver)
  * `cloud-controller-manager` (used for cloud-controller-manager)
  * `cluster-autoscaler` (used for cluster autoscaler)  

All tokens need read and write access.  
Save them in a **secure place** you will need them later and cant view them another time inside the webpanel.

<img src="../../assets/prerequisites/hetzner/create-api-tokens.png" width=50%>

## upload ssh-key(s)
Stay inside the security part of the hetzner webinterface and open the tab for the ssh-keys.  
Click add to upload your ssh-key(s). Paste your public key to the window.  
They will be later added to the servers when we create them. 
If you want to create a new ssh-key you can use `ssh-keygen`. 