# Deployment

After the prevoius steps in this guide we got a working kubertenes cluster with a loadbalanced, high-available controlplane and communication between our local machine and the cluster.

But we still miss some important features like agent-nodes, storage-drivers, ingress-controller and autoscalers.

In this step we will setup all needed deployments for the cluster to work poperly. This step will **not** cover the deployment of the applications itself, but **only the needed infrastructure**.