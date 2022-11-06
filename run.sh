# requirements
# Google Cloud CLI tools, kops

# Configure your credentials
gcloud auth application-default login

# first run only
# Create a bucket on GCP to store state
gsutil mb gs://kubs-clusters/

export KOPS_STATE_STORE=gs://kubs-clusters/
export PROJECT=`gcloud config get-value project`


# Create the cluster
kops create cluster simple.k8s.local --zones us-central1-a --state ${KOPS_STATE_STORE}/ --project=${PROJECT}

# Edit Cluster config
# set kubernetesVersion to 1.22.15
kops edit cluster simple.k8s.local

# Edit the node instance group configuration
# set maxSize and minSize to 8
kops edit ig --name=simple.k8s.local nodes-us-central1-a

# Apply the configuration changes
kops update cluster --name simple.k8s.local --yes --admin

# wait for cluster to be healthy
kops validate cluster --wait 10m

# deploy vitess
# update shard config parts
kubectl apply -f operator/operator.yaml
kubectl apply -f operator/101_initial_cluster.yaml
kubectl apply -f operator/201_customer_tablets.yaml

# port forward on host machine
./operator/pf.sh

# useful aliases
alias vtctlclient="vtctlclient --server=localhost:15999 --logtostderr"
alias mysql="mysql -h 127.0.0.1 -P 15306 -u user"

# create sharding schema for test tables
vtctlclient ApplyVSchema -- --vschema="$(cat operator/vschema.json)" customer

# prepare and run sysbench
time sysbench\
  --tables=1\
  --mysql-db=customer\
  --mysql-user=user\
  --mysql-host=127.0.0.1\
  --mysql-port=15306\
  --table_size=1000000\
  --auto_inc=off\
  --db-ps-mode=disable\
  --db-driver=mysql\
  oltp_read_write prepare

time sysbench\
  --threads=8\
  --tables=1\
  --time=1200\
  --mysql-db=customer\
  --mysql-user=user\
  --mysql-host=127.0.0.1\
  --mysql-port=15306\
  --table_size=1000000\
  --auto_inc=off\
  --db-ps-mode=disable\
  --db-driver=mysql\
  oltp_read_write run

# delete the cluster
kops delete cluster simple.k8s.local --yes
