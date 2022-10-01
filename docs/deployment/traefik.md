# Ingress Controller (traefik)
We will use traefik in this example as "edge router" and ingress controller. You can find more about traefik on the official [traefik](https://traefik.io/) website. 

## Prerequisites
You need the helm repository from traefik added to your local machine. You can add the repository with the following command:
```bash
helm repo add traefik https://helm.traefik.io/traefik
helm repo update
```

To separate the trafik installation from other deployments we create an own namespace for the trafik pods with the following command:
```bash
kubectl create namespace traefik
```

## Configure Helm Values
Create a new helm values file for traefik with the following command:
```bash
touch deployments/traefik/values.yml
nano deployments/traefik/values.yml
```

Edit the file and add the following content:
```yaml linenums="1"
globalArguments:
  - "--global.sendanonymoususage=false"
  - "--global.checknewversion=false"

additionalArguments:
#  - "--serversTransport.insecureSkipVerify=true"
  - "--log.level=INFO"
  - "--entryPoints.web.proxyProtocol.trustedIPs=10.0.0.200"
  - "--entryPoints.websecure.proxyProtocol.trustedIPs=10.0.0.200"

deployment:
  enabled: true
  replicas: 3
  annotations: {}
  podAnnotations: {}
  additionalContainers: []
  initContainers: []

ports:
  web:
    redirectTo: websecure
  websecure:
    tls:
      enabled: true

ingressRoute:
  dashboard:
    enabled: false

providers:
  kubernetesCRD:
    enabled: true
    ingressClass: traefik-external
  kubernetesIngress:
    enabled: true
    publishedService:
      enabled: false

rbac:
  enabled: true

service:
  enabled: true
  type: LoadBalancer
  annotations: {
    load-balancer.hetzner.cloud/name: "k8s-ingress", #(1)!
    load-balancer.hetzner.cloud/use-private-ip: true
  }
  labels: {}
  loadBalancerSourceRanges: []
  externalIPs: []
```

1. If you changed the name of the ingress loadbalancer you have to change the name here too.

## Deploy Workload
Finally install trafik with the following command run from your local machine:
```bash
helm install --namespace=traefik traefik traefik/traefik --values=deployments/traefik/values.yml
```

To validate all running services in the cluster, run the following command:
```bash
kubectl get svc --all-namespaces -o wide
```

## Setup default Middleware
Create a new middleware file for traefik with the following command:
```bash
touch deployments/traefik/default-middleware.yml
nano deployments/traefik/default-middleware.yml
```

Edit the file and add the following content:
```yaml linenums="1"
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: default-headers
  namespace: default
spec:
  headers:
    browserXssFilter: true
    contentTypeNosniff: true
    forceSTSHeader: true
    stsIncludeSubdomains: true
    stsPreload: true
    stsSeconds: 15552000
    customFrameOptionsValue: SAMEORIGIN
    customRequestHeaders:
      X-Forwarded-Proto: https
```

Change the values that they fot your personal needs. 

To apply the default middleware, run the following kubectl command:
```bash
kubectl apply -f deployments/traefik/default-middleware.yml
```

## Dashboard
To visit all routes traefik provides a dashboard. In the next steps we will create authentication values for the dashboard, a dashboard middleware and the ingressroute to serve traffic to the dashboard.

### Create Basic-Auth
In a previous step we installed apache2-utils to our local machine. With this package you get access to htpassword which we will use now to generate the basic auth credentials.

To generate a base64 encoded combination of the username and password, run the following command on your local machine:
```bash
htpasswd -nb USERNAME PASSWORD | openssl base64 #(1)!
```

1. Replace `USERNAME` with your username and `PASSWORD` with your password.  

Create a new secret file for traefik with the following command:
```bash
touch deployments/traefik/dashboard-secret.yml
nano deployments/traefik/dashboard-secret.yml
```

Edit the file and add the following content:
```yaml linenums="1"
apiVersion: v1
kind: Secret
metadata:
  name: traefik-dashboard-auth
  namespace: traefik
type: Opaque
data:
  users: BASE64_ENCODED_USER_AND_PASSWORD_HERE #(1)!
```

1. Replace `BASE64_ENCODED_USER_AND_PASSWORD_HERE` with the base64 encoded combination of the username and password you generated in the previous step.

As final step apply the dashboard-secret to the kubernetes cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-secret.yml
```

### Setup Middleware
To connect the traefik dashboard with the basic auth created in the previous step we need to create a middleware. 

Create a new middleware file for traefik with the following command:
```bash
touch deployments/traefik/dashboard-middleware.yml
nano deployments/traefik/dashboard-middleware.yml
```

Edit the file and add the following content:
```yaml linenums="1"
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: traefik-dashboard-basicauth
  namespace: traefik
spec:
  basicAuth:
    secret: traefik-dashboard-auth
```

Apply the middleware to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-middleware.yml
```

### Create IngressRoute
To serve traffic to the dashboard we need to create an IngressRoute. 

Create a new ingressroute file for traefik with the following command:
```bash
touch deployments/traefik/dashboard-ingressroute.yml
nano deployments/traefik/dashboard-ingressroute.yml
```

Edit the file and add the following content:
```yaml linenums="1"
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: traefik-dashboard
  namespace: traefik
  annotations:
    kubernetes.io/ingress.class: traefik-external
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`traefik.example.com`) #(1)!
      kind: Rule
      middlewares:
        - name: traefik-dashboard-basicauth
          namespace: traefik
      services:
        - name: api@internal
          kind: TraefikService
#(2)!
#  tls:
#    secretName: example-com-staging-tls
```

1. Replace `traefik.example.com` with your domain name you want to use for traefik.
2. The tls setting should be commented out, this will be added when cert-manager is installed and configured. 

Apply the ingress route to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-ingressroute.yml
```

Connect to your traefik domain (in this example `traefik.example.com`) and login with your basic auth credentials you've setup in [the previous step](#create-basic-auth). You should see the traefik dashboard with the default middlewares and services. 