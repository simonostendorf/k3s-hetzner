# Example Nginx Deployment
To show that the ingress controller, storage interface and cert-manager works, we will deploy an example nginx application. 

## Create DNS record
To make the ingress work, create a dns record at your dns-provider setup in an [earlier step](../../../prerequisites/dns-provider/).  
You can name the subdomain whatever you want, i will keep it test in this scenario. 

!!! warning "Remember"
    Remember to replace `INGRESS_LOADBALANCER_IP` with the public ip of your ingress loadbalancer (see hetzner cloud console)

`test.example.com` -> `A` -> `INGRESS_LOADBALANCER_IP`

## Create deployment
Create a new file on your machine with the following command:
```bash
mkdir -p deployments/nginx
nano deployments/nginx/example-deployment.yml
```

Fill the file with the following content. 

!!! warning "Remember"
    Remember to change the highlighted lines to fit your needs.

```yaml linenums="1" hl_lines="59 61 65 67 79 87"
--8<-- "assets/deployment/other/nginx/example-deployment.yml"
```

The deployment contains the following parts:

  * PersistentVolumeClaim: Volume claim of 5GB with driver hcloud-volumes (hetzner cloud volume) with access-mode ReadWriteOnce. See [access-modes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes)
  * Deployment: Nginx container with 3 replicas and mounted volume
  * Service: New service exposing port 80 from the nginx deployment
  * Certificate: Certificate created for the `test.example.com` domain (or your domain)
  * IngressRoute: Ingress route to tell traefik that the nginx-service (created in this deployment) should be available if the host matches `test.example.com` (or your domain) and should use the certificate created earlier

Apply the deployment to the cluster:
```bash
kubectl apply -f deployments/nginx/example-deployment.yml
```

With the following command you can see the pods comming up:
```bash
kubectl get pods
```

Pick one of the pod-names and connect to this container with a new terminal:

```bash
kubectl exec --stdin --tty CONTAINER_NAME -- /bin/bash
```

Create the index page of the nginx page with the following command:
```bash
echo 'Hello from k3s nginx.' > /usr/share/nginx/html/index.html
exit
```

## Test Ingress and Certificate
After you created the deployment, a certificate should be optained.  
You can follow the process by running:
```bash
kubectl get certificates
kubectl get challenges
```

When the certificate is ready, you can test the ingress by opening the url `https://test.example.com` (or your custom url) in your browser.

You should see the `Hello from k3s nginx.` page created in the step before. 

## Delete Deployment
To delete the deployment and all nested features (ingress-route, certificate, service etc.) run the following command:
```bash
kubectl delete -f deployments/nginx/example-deployment.yml
```