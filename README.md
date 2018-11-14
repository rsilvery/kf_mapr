# Steps to install KubeFlow on MapR
### Config: 
I did this on a single AWS t2.2xlarge instance with the following initial config:
* Kubenetes v1.12.2
* Docker v1.13.1
* SELinux and IPTables disabled
* Swap off


# Install MapR Volume Driver
* Download the most recent version of the following files to your directory on your K8s master node from [here](http://package.mapr.com/tools/KubernetesDataFabric/):
** kdf-namespace.yaml
** kdf-rbac.yaml
** kdf-plugin-centos.yaml
** kdf-provisioner.yaml
* Change host IP (labeled: changeme!) in kdf-plugin-centos.yaml to your Master host IP (can get with “hostname --ip-address”
* Create the following resources as shown:
** kubectl create -f kdf-namespace.yaml
** kubectl create -f kdf-rbac.yaml
** kubectl create -f kdf-plugin-centos.yaml
** kubectl create -f kdf-provisioner.yaml





