# Ingress Controller (traefik)
We will use traefik in this example as "edge router" and ingress controller. You can find more about traefik on the official [traefik](https://traefik.io/) website. 

## prerequisites
You need the helm repository from traefik added to your local machine. You can add the repository with the following command:
```bash
helm repo add traefik https://helm.traefik.io/traefik
helm repo update
```

To separate the trafik installation from other deployments we create an own namespace for the trafik pods with the following command:
```bash
kubectl create namespace traefik
```

## configure helm values
Copy the [traefik values file](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/traefik/values.yml) to your local machine. The file content fits the needs of this example, if you changed names from hetzner services or ip-ranges please review the file and change the values.

## deploy workload
Finally install trafik with the following command run from your local machine:
```bash
helm install --namespace=traefik traefik traefik/traefik --values=deployments/traefik/values.yml
```

To validate all running services in the cluster, run the following command:
```bash
kubectl get svc --all-namespaces -o wide
```

## setup default middleware
Copy the [default middleware](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/traefik/default-middleware.yml) file to your local machine. Please review the file and change the values to fit your personal needs. 

To apply the default middleware, run the following kubectl command:
```bash
kubectl apply -f deployments/traefik/default-middleware.yml
```

## dashboard
To visit all routes traefik provides a dashboard. In the next steps we will create authentication values for the dashboard, a dashboard middleware and the ingressroute to serve traffic to the dashboard.

### create basic auth
Run the following command on your local machine to install the apache2 utilities. With this package you get access to htpassword which we will use now to generate the basic auth credentials.
```bash
apt install apache2-utils
```

To generate a base64 encoded combination of the username and password, run the following command on your local machine:
```bash
htpasswd -nb USERNAME PASSWORD | openssl base64
```
Replace `USERNAME` with your username and `PASSWORD` with your password.  
Copy the base64 encoded output into the [dashboard-secret](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/traefik/dashboard-secret.yml) file where it says `BASE64_ENCODED_USER_AND_PASSWORD_HERE`. 

As final step apply the dashboard-secret to the kubernetes cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-secret.yml
```

### setup middleware
To connect the traefik dashboard with the basic auth created in the previous step we need to create a middleware. Copy the [dashboard middleware](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/traefik/dashboard-middleware.yml) file to your local machine. 

Apply the middleware to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-middleware.yml
```

### create IngressRoute
To serve traffic to the dashboard we need to create an IngressRoute. Copy the [dashboard ingressroute](https://github.com/simonostendorf/k3s-hetzner/blob/main/deployments/traefik/dashboard-ingressroute.yml) file to your local machine.  

Edit the file and replace the `traefik.example.com` host with your domain name you want to use for traefik.  
The tls setting should be commented out, this will be added when cert-manager is installed and configured. 

Apply the ingress route to the cluster with the following command:
```bash
kubectl apply -f deployments/traefik/dashboard-ingressroute.yml
```

Connect to your traefik domain (in this example `traefik.example.com`) and login with your basic auth credentials you've setup in [the previous step](#create-basic-auth). You should see the traefik dashboard with the default middlewares and services. 