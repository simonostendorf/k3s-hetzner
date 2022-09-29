# cert-manager
We will use cert-manager as central certificate manager for all certificates in the cluster. You can find more about cert-manager on the official [cert-manager](https://cert-manager.io/) website.  
Cert-manager will use the [letsencrypt](https://letsencrypt.org/) service to issue certificates for the cluster. The certificates get validated through the dns01 acme challenge, described in the [dns-provider step](../../prerequisites/dns-provider/). 

## prerequisites
Similar to traefik we will also use helm to install cert-manager to our cluster. You need the helm repository from cert-manager added to your local machine. You can add the repository with the following command:
```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

And we also create a separate namespace for cert-manager with the following command:
```bash
kubectl create namespace cert-manager
```

Because kubernetes does not know about certificates in the default installation we need to create a custom resource definition for certificates. Run the following command to download and apply the custom resource definitions:
```bash
wget https://github.com/cert-manager/cert-manager/releases/download/v1.9.1/cert-manager.crds.yaml -O deployments/cert-manager/crds.yml
kubectl apply -f deployments/cert-manager/crds.yml
```

You can try to get information about certificates now with the following command:
```bash
kubectl get certificates
```
Before adding the crds kubernetes will return an error that the resource of the type `certificates` is not known. After adding the crds the command should return an empty list.

## configure helm values
Copy the [cert-manager values file](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/cert-manager/values.yml) to your local machine. Edit the file contents if you want to change the dns-servers that are used to validate the dns01 challenge. In this example we will use cloudflare-dns (1.1.1.1) and quad9 (9.9.9.9). 

## deploy workload
To deploy the workload with helm run the following command on your local machine:
```bash
helm install cert-manager jetstack/cert-manager --namespace cert-manager --values=deployments/cert-manager/values.yml --version v1.9.1
```

To see the pods comming up run the following command:
```bash
kubectl get pods --namespace cert-manager
```

## certificates
To issue certificates you need different resources. The certificate-issuer (company that issues the certificate), the certificate-request (what certificate you want to issue) and the certificate (the actual certificate). In this example we will first use the letsencrypt staging issuer to issue test certificates for the domains we want to use and switch to the letsencrypt production environment if everything works.

### create Cloudflare token
As described in the [cloudflare step](../../prerequisites/dns-provider/#create-token) we've created a token for cloudflare to allow cert-manager to update the dns records. This token will be put into a kubernetes secret. 

Copy the [cloudflare secret](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/cert-manager/cloudflare-secret.yml) file to your local machine. Edit the file and replace the `CLOUDFLARE_TOKEN_HERE` with the token you've created previously.

Apply the secret to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/cloudflare-secret.yml
```

### letsencrypt staging
As described previously we first use staging certificates to test our environment because the production api from letsencrypt is rate limited.

#### create CerificateIssuer
Copy the file [letsencrypt staging issuer](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/cert-manager/letsencrypt-staging-issuer.yml) to your local machine. Edit the file and replace the following values:
  * `certificate@example.com` with your email address you want to use for letsencrypt
  * `cloudflare@example.com` with your email address you use to login to cloudflare
  * `example.com` with your zone name(s) inside cloudflare

Apply the issuer to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/letsencrypt-staging-issuer.yml
```

#### create Certificate
The next step is to create a certificate. Copy the [example-staging-certificate](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/cert-manager/example-com-staging-tls.yml) to your local machine and replace the domain with your needed domains. You can add multiple domains or use the certificate as wildcard certificate like its shown in the example.  

Attention: The certificate will be created in the namespace trafik to add it to the traefik dashboard as test route. Certificates need to be in the same namespace as the ingressroute.

Apply the certificate to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/example-com-staging-tls.yml
```

You can see the certificates getting requested with the following commands:
```bash
kubectl get challenges --namespace=traefik
kubectl get certificates --namespace=traefik
```

#### add certificate to traefik
As final step you can add the certificate to the traefik dashboard. Reopen the [traefik dashboard ingressroute](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/traefik/dashboard-ingressroute.yml) and uncomment the tls section. Replace the `example.com` with your domain and apply the ingressroute to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-ingressroute.yml
```

Open the dashboard webpage and open the certificate details and check if the certificate is issued by letsencrypt.  
Remember: We are using a staging (not valid) certificate, so dont worry if you get a warning in your browser. 

### letsencrypt production
If everything works with the staging certificate we can switch to the production environment. 

You can delete the old staging certificate with the following commands:
```bash
kubectl delete -f example-com-staging-tls.yml --namespace=traefik
```

#### create CerificateIssuer
The setup will be similar to the staging environment. Copy the [issuer file](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/cert-manager/letsencrypt-production-issuer.yml) to your local machine. Edit the file and replace the following values:

  * `certificate@example.com` with your email address you want to use for letsencrypt
  * `cloudflare@example.com` with your email address you use to login to cloudflare
  * `example.com` with your zone name(s) inside cloudflare

Apply the issuer to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/letsencrypt-production-issuer.yml
```

#### create Certificate
Now we will create separate certificates for traefik and all other pods. In this example i will only show the creation of a production certificate for trafik but you can change the deployment file to fit your special needs. 

Copy the [traefik production certificate](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/cert-manager/traefik-example-com-tls.yml) to your local machine and replace the domain and the internal certificate name to fit your traefik domain.

Apply the certificate to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/traefik-example-com-tls.yml
```

You can see the certificates getting requested with the following commands:
```bash
kubectl get challenges --namespace=traefik
kubectl get certificates --namespace=traefik
```

#### add certificate to traefik
You can add the production certificate to traefik by editing the [traefik dashboard ingressroute](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/traefik/dashboard-ingressroute.yml) and change the tls section to the new production certificate name entered in the deployment file above. 

Apply the changed ingressroute to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-ingressroute.yml
```