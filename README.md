# Steps to install KubeFlow on MapR
### Config: 
I did this on a single AWS t2.2xlarge instance with the following initial config:
* Kubenetes v1.12.2
* KubeFlow 0.3.1
* Docker v1.13.1
* KSonnet 0.13.0
* SELinux and IPTables disabled
* Swap off


### Install MapR Volume Driver
Installing the MapR Volume Driver allows you to create persistent volumes that map to volumes in your MapR filespace.
* Download the most recent version of the following files to your directory on your K8s master node from [here](http://package.mapr.com/tools/KubernetesDataFabric/):
  * kdf-namespace.yaml
  * kdf-rbac.yaml
  * kdf-plugin-centos.yaml
  * kdf-provisioner.yaml
* Change host IP (labeled: *changeme!*) in kdf-plugin-centos.yaml to your Master host IP (can get with *hostname --ip-address*)
* Create the following resources as shown:
  * *kubectl create -f kdf-namespace.yaml*
  * *kubectl create -f kdf-rbac.yaml*
  * *kubectl create -f kdf-plugin-centos.yaml*
  * *kubectl create -f kdf-provisioner.yaml*


### Configure namespace, secret, and data access
These are the initial steps needed to configure data cluster access for KubeFlow
* Create a Namespace for Kubeflow: *kubectl create ns kubeflow*
* Create Secret for cluster access (see [kf-secret.yaml](kf-secret.yaml)):
  * Get long lived service ticket from a MapR cluster. Can follow steps [here](https://mapr.com/docs/61/SecurityGuide/GeneratingServiceTicket.html)
  * Base64 encode this ticket. You can use a webtool like [this](https://www.base64encode.org/)
  * Insert encoded ticket string into [kf-secret.yaml](kf-secret.yaml) 
  * Create secret: *kubectl create -f kf-secret.yaml*
* Create Persistent Volume (PV) to provision storage in the cluster
  * Edit [kf-pv.yaml](kf-pv.yaml) and enter your cluster info where indicated under "options"
  * *kubectl create -f kf-pv.yaml*
* Create Persistent Volume Claim (PVC) to bind to this claim (using [kf-pvc.yaml](kf-pvc.yaml))
  * *kubectl create -f kf-pvc.yaml* 

 If you want to test that this worked, you can use the [kf-testpod.yaml](kf-testpod.yaml) to generate a Centos pod with this mount.

### Install KubeFlow dependencies
* KSonnet: has to be built manually with a version of Go newer than 1.9  [JIRA](https://github.com/kubeflow/kubeflow/issues/1929)
  * Install Go (example)
    * *wget https://dl.google.com/go/go1.11.2.linux-amd64.tar.gz*
    * *sudo tar -C /usr/local -xzf go1.11.2.linux-amd64.tar.gz*
    * *export PATH=$PATH:/usr/local/go/bin*
  * Install KSonnet
    * *go get github.com/ksonnet/ksonnet*
    * *cd go/src/github.com/ksonnet/ksonnet/*
    * *make install*
    * Create symbolic link in /usr/local/bin: *sudo ln -s /home/centos/go/bin/ks /usr/local/bin/ks*


### Install KubeFlow 
* Set Environment Variables using whatever method you prefer
  * *export KUBEFLOW_VERSION=0.3.1*
  * *export KUBEFLOW_TAG=v${KUBEFLOW_VERSION}*
  * *export K8S_NAMESPACE=kubeflow*
  * *export KUBEFLOW_REPO=/home/centos/kubeflow/kubeflow-$KUBEFLOW_VERSION* (or whatever you'd like)
  * *export KUBEFLOW_KS_DIR=/home/centos/kubeflow/ks_app*
  * *export DEPLOYMENT_NAME=kubeflowexport DEPLOYMENT_NAME=kubeflow* 
* Create KubeFlow directory and download components to it
  * *mkdir kubeflow*
  * *cd kubeflow*
  * *curl -L -o kubeflow/kubeflow.tar.gz https://github.com/kubeflow/kubeflow/archive/${KUBEFLOW_TAG}.tar.gz*
  * *tar -xzvf kubeflow/kubeflow.tar.gz*
* Initialize KubeFlow apps directory for KSonnet
  * *ks init ks_app*
* Configure KSonnet for KubeFlow
  * *cd $KUBEFLOW_KS_DIR*
  * *ks registry add kubeflow $KUBEFLOW_REPO/kubeflow*
  * *ks env set default --namespace $K8S_NAMESPACE*







