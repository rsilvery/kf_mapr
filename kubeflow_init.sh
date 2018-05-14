
# Initialize a ksonnet app. Set the namespace for it's default environment.
APP_NAME=my-kubeflow
ks_0.10.2_linux_amd64/ks init ${APP_NAME}
cd ${APP_NAME}
ks_0.10.2_linux_amd64/ks env set default --namespace demo-kf

# Install Kubeflow components
ks_0.10.2_linux_amd64/ks registry add kubeflow github.com/kubeflow/kubeflow/tree/v0.1.3/kubeflow
ks_0.10.2_linux_amd64/ks pkg install kubeflow/core@v0.1.3
ks_0.10.2_linux_amd64/ks pkg install kubeflow/tf-serving@v0.1.3
ks_0.10.2_linux_amd64/ks pkg install kubeflow/tf-job@v0.1.3

# Create templates for core components
ks_0.10.2_linux_amd64/ks generate kubeflow-core kubeflow-core

# Deploy Kubeflow
ks_0.10.2_linux_amd64/ks apply default -c kubeflow-core