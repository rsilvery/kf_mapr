# Steps to install KubeFlow on MapR
### Config: 
I did this on a single AWS t2.2xlarge instance with the following initial config:
* Kubenetes v1.12.2
* KubeFlow 0.3.3
* Docker v1.13.1
* KSonnet 0.13.0
* SELinux and IPTables disabled
* Swap disabled


### Install MapR Volume Driver
Installing the MapR Volume Driver allows you to create persistent volumes that map to volumes in your MapR filespace.
* Download the most recent version of the following files to your directory on your K8s master node from [here](http://package.mapr.com/tools/KubernetesDataFabric/):
  * kdf-namespace.yaml
  * kdf-rbac.yaml
  * kdf-plugin-centos.yaml
  * kdf-provisioner.yaml
* Change host IP (labeled: *changeme!*) in kdf-plugin-centos.yaml to your Master host IP (can get with *hostname --ip-address*)
* Create the following resources as shown:
  ```
  kubectl create -f kdf-namespace.yaml
  kubectl create -f kdf-rbac.yaml
  kubectl create -f kdf-plugin-centos.yaml
  kubectl create -f kdf-provisioner.yaml
  ```

### Configure namespace, secret, and data access
These are the initial steps needed to configure data cluster access for KubeFlow
* Create a Namespace for Kubeflow: 
  ```
  kubectl create ns kubeflow
  ```
* Create Secret for cluster access (see [kf-secret.yaml](kf-secret.yaml)):
  * Get long lived service ticket from a MapR cluster. Can follow steps [here](https://mapr.com/docs/61/SecurityGuide/GeneratingServiceTicket.html)
  * Base64 encode this ticket. You can use a webtool like [this](https://www.base64encode.org/)
  * Insert encoded ticket string into [kf-secret.yaml](kf-secret.yaml) 
  * Create secret: 
  ```
  kubectl create -f kf-secret.yaml
  ```
* Create Persistent Volume (PV) to provision storage in the cluster for personal applications
  * Edit [kf-pv.yaml](kf-pv.yaml) and enter your cluster info where indicated under "options"
  ```
  kubectl create -f kf-pv.yaml
  ```
* Create Persistent Volume Claim (PVC) to bind to this claim (using [kf-pvc.yaml](kf-pvc.yaml))
  ```
  kubectl create -f kf-pvc.yaml
  ``` 
* Edit [claim-admin-pv.yaml](claim-admin-pv.yaml) and enter your cluster info where indicated under "options" to create a Persistent Volume claim for JupyterHub. 
  ```
  kubectl create -f claim-admin-pv.yaml
  ```
* Create Persistent Volume Claim (PVC) for JupyterHub (using [claim-admin-pvc.yaml](claim-admin-pvc.yaml))
  ```
  kubectl create -f claim-admin-pvc.yaml
  ```

 If you want to test that this worked, you can use the [kf-testpod.yaml](kf-testpod.yaml) to generate a Centos pod with this mount.

### Install KubeFlow dependencies
* KSonnet: has to be built manually with a version of Go newer than 1.9  ([JIRA])(https://github.com/kubeflow/kubeflow/issues/1929)
  * Install Go (example)
  ```
     wget https://dl.google.com/go/go1.11.2.linux-amd64.tar.gz
     sudo tar -C /usr/local -xzf go1.11.2.linux-amd64.tar.gz
     export PATH=$PATH:/usr/local/go/bin
     export GOPATH=/home/centos/go(whereever you want to pull the KSonnet source)
  ```
  * Install KSonnet
  ```
     sudo yum -y install git
     go get github.com/ksonnet/ksonnet
     cd /home/centos/go/src/github.com/ksonnet/ksonnet (or your dir)
     make install
     sudo ln -s /home/centos/go/bin/ks /usr/local/bin/ks
     cd ~
  ```
  * Install Seldon monitoring dashboard (Prometheus+Grafana)
    * Install Helm
    ```
    curl https://raw.githubusercontent.com/helm/helm/master/scripts/get > get_helm.sh
    chmod a+x get_helm.sh 
    ./get_helm.sh
    helm init

    ```
    * Install Seldon Core Anayltics using Helm
    ```
    helm install seldon-core-analytics --name seldon-core-analytics --set grafana_prom_admin_password=password --set persistence.enabled=false --repo https://storage.googleapis.com/seldon-charts --namespace kubeflow
    ```


### Install KubeFlow 
* Set Environment Variables using whatever method you prefer
  ```
   export K8S_NAMESPACE=kubeflow
   export DEPLOYMENT_NAME=kubeflow
   export KUBEFLOW_VERSION=0.3.3
   export KUBEFLOW_TAG=v${KUBEFLOW_VERSION}
   export KUBEFLOW_DEPLOY=true
   export KUBEFLOW_REPO=`pwd`/kubeflow/
   export KUBEFLOW_KS_DIR=`pwd`/${DEPLOYMENT_NAME}_ks_app
   ```
* Create KubeFlow directory and clone repo from GitHub
  ```
  curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash
  ```
* Initialize KSonnet app 
  ```
  cd $(dirname "${KUBEFLOW_KS_DIR}")
  ks init $(basename "${KUBEFLOW_KS_DIR}")
  ```
* Add local KubeFlow registry
  ```
   cd $KUBEFLOW_KS_DIR
   ks registry add kubeflow "${KUBEFLOW_REPO}"
  ```
* Set default namespace for KSonnet
  ```
  ks env set default --namespace $K8S_NAMESPACE
  ```
* Install KubeFlow packages. Please see master list in KubeFlow [repo](https://github.com/kubeflow) for what's available or run this command: "*ks pkg list*"
   ```
   ks pkg install kubeflow/core
   ks pkg install kubeflow/argo
   ks pkg install kubeflow/tf-serving
   ks pkg install kubeflow/seldon
   ks pkg install kubeflow/examples
   ```
* Generate Kube manifests for kubeflow components:
  ```
   ks generate ambassador ambassador
   ks generate jupyterhub jupyterhub --namespace ${K8S_NAMESPACE}
   ks generate centraldashboard centraldashboard
   ks generate tf-job-operator tf-job-operator --namespace ${K8S_NAMESPACE}
   ks generate argo argo --namespace ${K8S_NAMESPACE}
   ks generate seldon seldon --namespace ${K8S_NAMESPACE}
   ```
* Configure KS environment for deployment
   ```
   ks env add cloud
   ks env set cloud --namespace ${K8S_NAMESPACE}
   kubectl config set-context $(kubectl config current-context) --namespace=$K8S_NAMESPACE
   ```
* Deploy Ksonnet app
  ```
  ks apply cloud
  ```

### Provide Ingress to UIs
If you're on AWS, then you need to do some port mapping in order to have the external IP route to the internal node IP. 
* JupyterHub
  * Download and edit [jupyter-svc.yaml](jupyter-svc.yaml) by changing the external IP to match your configuration and deploy service.
    ```
    kubectl create -f jupyter-svc.yaml
    ```
* Argo
  * Download and edit [argo-svc.yaml](argo-svc.yaml) by changing the external IP to match your configuration and deploy service.
    ```
    kubectl create -f argo-svc.yaml
    ```
* Grafana (for Seldon Core Analytics)
  * Download and edit [seldon-svc.yaml](seldon-svc.yaml) by changing the external IP to match your configuration and deploy service.
    ```
    kubectl create -f seldon-svc.yaml
    ```


## Demo of KubeFlow
This demo is to train and serve a TensorFlow MNIST model. Training is done in the notebook container on data in the MapR volume and model is output back to MapR storage.

### Train Model
* Launch Jupyter instance with TensorFlow from JupyterHub (located on port 8000)
* Open [mnist.ipynb](mnist.ipynb) notebook 
* Set your training_data and model_output directories to the correct location in the MapR filesystem.
  * Note that the mount point is under */home/jovyan* so if your directory was mounted as *training_data* it will be */home/jovyan/training_data*
* Run training job 

...to be continued.



