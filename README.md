# Steps to install KubeFlow on MapR
### Config: 
I did this on a single AWS t2.2xlarge instance with the following initial config:
* Kubenetes v1.12.2
* Docker v1.13.1
* SELinux and IPTables disabled
* Swap off


### Install MapR Volume Driver
Installing the MapR Volume Driver allows you to create persistent volumes that map to volumes in your MapR filespace.
* Download the most recent version of the following files to your directory on your K8s master node from [here](http://package.mapr.com/tools/KubernetesDataFabric/):
  * kdf-namespace.yaml
  * kdf-rbac.yaml
  * kdf-plugin-centos.yaml
  * kdf-provisioner.yaml
* Change host IP (labeled: *changeme!*) in kdf-plugin-centos.yaml to your Master host IP (can get with *hostname --ip-address*
* Create the following resources as shown:
  * *kubectl create -f kdf-namespace.yaml*
  * *kubectl create -f kdf-rbac.yaml*
  * *kubectl create -f kdf-plugin-centos.yaml*
  * *kubectl create -f kdf-provisioner.yaml*


### Create namespace, secret, and volume claims
These are the initial steps needed to configure data cluster access for KubeFlow
* Create a Namespace for Kubeflow: *kubectl create ns kubeflow*
* Create Secret for cluster access (see /kf-secret.yaml):
  * Get long lived service ticket from a MapR cluster. Can follow steps [here](https://mapr.com/docs/61/SecurityGuide/GeneratingServiceTicket.html)
  * Base64 encode this ticket. You can use a webtool like [this](https://www.base64encode.org/)
  * Insert encoded ticket string into /kf-secret.yaml 
  * Create secret: *kubectl create -f kf-secret.yaml*
* Create Persistent Volume (PV) to provision storage in the cluster
  * Edit /kf-pv.yaml and enter your cluster info where indicated under "options"
  * *kubectl create -f kf-pv.yaml*
* Create Persistent Volume Claim (PVC) to bind to this claim (using /kf-pvc.yaml)
  * *kubectl create -f kf-pvc.yaml* 

  




