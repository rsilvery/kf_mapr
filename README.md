# Steps:

### Create namespace and enable volume plugin:
 "kubectl create -f mapr_config.yaml"
### Install KSonnet:
wget https://github.com/ksonnet/ksonnet/releases/download/v0.10.2/ks_0.10.2_linux_amd64.tar.gz

tar -xzvf ks_0.10.2_linux_amd64.tar.gz 

### Run create kubeflow app: 

cd ks_0.10.2_linux_amd64
./ks init kubeflow-demo
cd kubeflow-demo/
../ks env set default --namespace demo-kf
../ks registry add kubeflow github.com/kubeflow/kubeflow/tree/v0.1.3/kubeflow

### Install Kubeflow components
../ks pkg install kubeflow/core@v0.1.3
../ks pkg install kubeflow/tf-serving@v0.1.3
../ks pkg install kubeflow/tf-job@v0.1.3

### Create templates for core components
../ks generate kubeflow-core kubeflow-core

### Deploy Kubeflow
../ks apply default -c kubeflow-core

### Set Jupyter notebook directory for persistent notebooks (assuming "/user/mapr/jupyter" in MapR-FS)
../ks param set kubeflow-core jupyterNotebookPVCMount /mapr/jupyter

### Visit Jupyter hub on port 8000 on your K8s cluster
