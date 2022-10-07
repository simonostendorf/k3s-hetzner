# Cert-Manager
We will use cert-manager as central certificate manager for all certificates in the cluster. You can find more about cert-manager on the official [cert-manager](https://cert-manager.io/) website.  
Cert-Manager will use the [letsencrypt](https://letsencrypt.org/) service to issue certificates for the cluster. The certificates get validated through the dns01 acme challenge, described in the [dns-provider step](../../../prerequisites/dns-provider/). 

## Prerequisites
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
curl https://github.com/cert-manager/cert-manager/releases/download/v1.9.1/cert-manager.crds.yaml --create-dirs -L -o deployments/cert-manager/crds.yml
kubectl apply -f deployments/cert-manager/crds.yml
```

You can try to get information about certificates now with the following command:
```bash
kubectl get certificates
```
*Before adding the crds kubernetes will return an error that the resource of the type `certificates` is not known. After adding the crds the command should return an empty list.*

## Configure Helm Values
Create a new helm values file for cert-manager with the following command:
```bash
nano deployments/cert-manager/values.yml
```

Edit the file and add the following content:
```yaml linenums="1"
installCRDs: false
replicaCount: 3
extraArgs:
  - --dns01-recursive-nameservers=1.1.1.1:53,9.9.9.9:53
  - --dns01-recursive-nameservers-only
podDnsPolicy: None
podDnsConfig:
  nameservers:
    - "1.1.1.1"
    - "9.9.9.9"
```

Edit the file contents if you want to change the dns-servers that are used to validate the dns01 challenge. In this example we will use cloudflare-dns (1.1.1.1) and quad9 (9.9.9.9). 

## Deploy Workload
To deploy the workload with helm run the following command on your local machine:
```bash
helm install cert-manager jetstack/cert-manager --namespace cert-manager --values=deployments/cert-manager/values.yml --version v1.9.1
```

To see the pods comming up run the following command:
```bash
kubectl get pods --namespace cert-manager
```

## Certificates
To issue certificates you need different resources. The certificate-issuer (company that issues the certificate), the certificate-request (what certificate you want to issue) and the certificate (the actual certificate). In this example we will first use the letsencrypt staging issuer to issue test certificates for the domains we want to use and switch to the letsencrypt production environment if everything works.

### Create Cloudflare Token
As described in the [cloudflare step](../../../prerequisites/dns-provider/#create-token) we've created a token for cloudflare to allow cert-manager to update the dns records. This token will be put into a kubernetes secret. 

Create a new kubernetes secret with the following command:
```bash
nano deployments/cert-manager/cloudflare-secret.yml
```

Edit the file and add the following content:
```yaml linenums="1"
apiVersion: v1
kind: Secret
metadata:
  name: cloudflare-token-secret
  namespace: cert-manager
type: Opaque
stringData:
  cloudflare-token: CLOUDFLARE_TOKEN_HERE #(1)!
```

1. Replace the `CLOUDFLARE_TOKEN_HERE` with the token you've created previously.

Apply the secret to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/cloudflare-secret.yml
```

### LetsEncrypt Staging
As described previously we first use staging certificates to test our environment because the production api from letsencrypt is rate limited.

#### Create CerificateIssuer
Create a new certificate issuer with the following command:
```bash
nano deployments/cert-manager/letsencrypt-staging-issuer.yml
```

Edit the file and add the following content:
```yaml linenums="1"
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: certificate@example.com #(1)!
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
      - dns01:
          cloudflare:
            email: cloudflare@example.com #(2)!
            apiTokenSecretRef:
              name: cloudflare-token-secret
              key: cloudflare-token
        selector:
          dnsZones:
            - "example.com" #(3)!
```

1. `certificate@example.com` with your email address you want to use for letsencrypt
2. `cloudflare@example.com` with your email address you use to login to cloudflare
3. `example.com` with your zone name(s) inside cloudflare

Apply the issuer to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/letsencrypt-staging-issuer.yml
```

#### Create Certificate
The next step is to create a certificate. 

Create a new certificate with the following command:
```bash
nano deployments/cert-manager/example-com-staging-tls.yml #(1)!
```

1. Replace `example-com-staging-tls.yml` with the name of your certificate.

Edit the file and add the following content:
```yaml linenums="1"
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-com #(1)!
  namespace: traefik
spec:
  secretName: example-com-staging-tls #(2)!
  issuerRef:
    name: letsencrypt-staging
    kind: ClusterIssuer
  commonName: "*.example.com" #(3)!
  dnsNames:
  - "example.com" #(4)!
  - "*.example.com" #(5)!
```

1. Replace `example-com` with the name of your certificate.
2. Replace `example-com-staging-tls` with the name of your certificate.
3. Replace `*.example.com` with the common name of your certificate.
4. Replace `example.com` with the dns names you want the certificate for.
5. Replace `*.example.com` with the dns names you want the certificate for.

You can add multiple domains or use the certificate as wildcard certificate like its shown in the example.  

!!! error "Attention"
    The certificate will be created in the namespace trafik to add it to the traefik dashboard as test route. Certificates need to be in the same namespace as the IngressRoute.

Apply the certificate to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/example-com-staging-tls.yml
```

You can see the certificates getting requested with the following commands:
```bash
kubectl get challenges --namespace=traefik
kubectl get certificates --namespace=traefik
```

#### Add Certificate to traefik
As final step you can add the certificate to the traefik dashboard. Reopen the traefik dashboard ingressroute and uncomment the tls section. 

```bash
nano deployments/traefik/dashboard-ingressroute.yml
```

Edit the file and uncomment the tls section:
```yaml linenums="1"
  tls:
    secretName: example-com-staging-tls #(1)!
```

1. Replace the `example-com-staging-tls` with your certificate name

Apply the ingressroute to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-ingressroute.yml
```

Open the dashboard webpage and open the certificate details and check if the certificate is issued by letsencrypt.  

!!! info "Remember"
    We are using a staging (not valid) certificate, so dont worry if you get a warning in your browser. 

### LetsEncrypt Production
If everything works with the staging certificate we can switch to the production environment. 

You can delete the old staging certificate with the following commands:
```bash
kubectl delete -f deployments/cert-manager/example-com-staging-tls.yml --namespace=traefik #(1)!
```

1. Replace `example-com-staging-tls.yml` with the name of your certificate.

#### Create CerificateIssuer
The setup will be similar to the staging environment. Copy the staging issuer file:
```bash
cp deployments/cert-manager/letsencrypt-staging-issuer.yml deployments/cert-manager/letsencrypt-production-issuer.yml
sed -i 's/letsencrypt-staging/letsencrypt-production/g' deployments/cert-manager/letsencrypt-production-issuer.yml
sed -i 's/-staging-/-/g' deployments/cert-manager/letsencrypt-production-issuer.yml
```

Apply the issuer to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/letsencrypt-production-issuer.yml
```

#### Create Certificate
Now we will create separate certificates for traefik and all other pods. In this example i will only show the creation of a production certificate for trafik but you can change the deployment file to fit your special needs. 

Create a new certificate with the following command:
```bash
nano deployments/cert-manager/traefik-example-com-tls.yml #(1)!
```

1. Replace `traefik-example-com-tls.yml` with the name of your certificate.

Edit the file and add the following content:
```yaml linenums="1"
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: traefik-example-com #(1)!
  namespace: traefik
spec:
  secretName: traefik-example-com-tls #(2)!
  issuerRef:
    name: letsencrypt-production
    kind: ClusterIssuer
  commonName: "traefik.example.com" #(3)!
  dnsNames:
  - "traefik.example.com" #(4)!
```

1. Replace `traefik-example-com` with the name of your certificate.
2. Replace `traefik-example-com-tls` with the name of your certificate.
3. Replace `traefik.example.com` with the common name of your certificate.
4. Replace `traefik.example.com` with the dns names you want the certificate for.

Apply the certificate to the cluster with the following command:
```bash
kubectl apply -f deployments/cert-manager/traefik-example-com-tls.yml #(1)!
```

1. Replace `traefik-example-com-tls.yml` with the name of your certificate.

You can see the certificates getting requested with the following commands:
```bash
kubectl get challenges --namespace=traefik
kubectl get certificates --namespace=traefik
```

#### Add Certificate to traefik
As final step you can add the certificate to the traefik dashboard. Reopen the traefik dashboard ingressroute and change the tls section. 

```bash
nano deployments/traefik/dashboard-ingressroute.yml
```

Edit the file and change the tls section:
```yaml linenums="1"
  tls:
    secretName: traefik-example-com-tls #(1)!
```

1. Replace the `traefik-example-com-tls` with your certificate name

Apply the ingressroute to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-ingressroute.yml
```

Open the dashboard webpage and open the certificate details and check if the certificate is issued by letsencrypt and is a valid secure connection.  