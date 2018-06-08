import getpass
import subprocess
import base64
import time
import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# assumes namespace demo-kf has already been created
# ex run: ../miniconda3/bin/python make_cluster.py

# Cluster Config
MAPR_CLUSTER = "<>" 
MAPR_CLDB_HOSTS = "<>"
HOST_IP = "<>"

# Get login info for creating secret
print("\n Please enter the login information for your cluster user (ex. 'mapr')")
user=input("\nUsername: ")
passwd = getpass.getpass()


# Generate ticket and export to Base64
cmd = "echo '" + passwd + "' | /opt/mapr/bin/maprlogin password"
ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
output = ps.communicate()[0]
#print (output)
file = open("/tmp/maprticket_5000","r")
ticket = file.read()
ticket64 = str(base64.b64encode(bytes(ticket.strip(),'utf-8')), 'utf-8')
file.close()


MAPR_CONTAINER_USER = user
MAPR_CONTAINER_PASSWORD = passwd

# Kubernetes config
namespace = 'demo-kf'
config.load_kube_config()
v1 = client.CoreV1Api()
v1apps = client.AppsV1Api()
api_version = 'v1'

# Create secret in Kubernetes
kind = 'Secret'
metadata = {'name': 'kfsecret', 'namespace': namespace}
data = {'CONTAINER_TICKET': ticket64}
body = kubernetes.client.V1Secret(api_version, data, kind, metadata, type='Opaque' )
api_response = v1.create_namespaced_secret(namespace, body)

# create persistent volume claim 
kind = 'PersistentVolume'
metadata = {'name': 'kfpv', 'namespace': namespace}
spec = {"capacity": {"storage": "5Gi"},"accessModes": ["ReadWriteOnce"],"claimRef": {"namespace": namespace,"name": "kfpvc"},"flexVolume": {"driver": "mapr.com/maprfs","options": {"platinum": "false","cluster": MAPR_CLUSTER,"cldbHosts": MAPR_CLDB_HOSTS,"volumePath": "/user/mapr","securityType": "secure","ticketSecretName": "kfsecret","ticketSecretNamespace": namespace}}} 
body = kubernetes.client.V1PersistentVolume(api_version, kind, metadata, spec)
api_response = v1.create_persistent_volume(body)

# create persistent volume claim 
kind = 'PersistentVolumeClaim'
metadata = {'name': 'kfpvc', 'namespace': namespace}
spec = {"accessModes":["ReadWriteOnce"],"resources":{"requests":{"storage":"5G"}}}
body = kubernetes.client.V1PersistentVolumeClaim(api_version, kind, metadata, spec)
api_response = v1.create_namespaced_persistent_volume_claim(namespace, body)