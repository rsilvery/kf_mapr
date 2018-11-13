# Steps to install KubeFlow on MapR
### Config: 
I did this on a single AWS t2.2xlarge instance with the following initial config:
* Kubenetes v1.12.2
* Docker v1.13.1
* SELinux and IPTables disabled
* Swap off




### Create namespace and enable volume plugin:
 "kubectl create -f mapr_config.yaml"


