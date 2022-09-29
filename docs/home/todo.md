# ToDo

* Deploy kube-prometheus-stack (prometheus, grafana, alertmanager, node-exporter etc.) to collect and visualize metrics from nodes and pods
* Setup vertical pod autoscaler to automaticly update pod resources requests and limits
* Setup goldilocks as dashboard for the vertical pod autoscaler
* Setup argo-cd to automaticly deploy workloads as part of the ci/cd pipeline
* Setup automatic deployment of github workers done by argo-cd
* Use placement groups for agents for better availability (currently not possible because of the cluster autoscaler hetzner support)
* Allow connection to the kubernetes api and some services only with high-available vpn
* Setup more loadbalancers for separation of dev and production deployments and different access rights
