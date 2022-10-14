
# prepare kubernetes
minikube start --kubernetes-version=v1.19.16 --cpus=4 --memory=4000 --disk-size=32g

# deploy vitess
kubectl apply -f operator/operator.yaml
kubectl apply -f operator/101_initial_cluster.yaml
kubectl apply -f operator/201_customer_tablets.yaml

# port forward on host machine
./operator/pf.sh&

# useful aliases
alias vtctlclient="vtctlclient --server=localhost:15999 --logtostderr"
alias mysql="mysql -h 127.0.0.1 -P 15306 -u user"

# create sharding schema for test tables
vtctlclient ApplyVSchema -- --vschema="$(cat operator/vschema.json)" customer

# prepare and run sysbench
sysbench\
  --tables=1\
  --mysql-db=customer\
  --mysql-user=user\
  --mysql-host=127.0.0.1\
  --mysql-port=15306\
  --table_size=100000\
  --auto_inc=off\
  --db-ps-mode=disable\
  --db-driver=mysql\
  oltp_read_write prepare

sysbench\
  --threads=4\
  --tables=1\
  --time=1200\
  --mysql-db=customer\
  --mysql-user=user\
  --mysql-host=127.0.0.1\
  --mysql-port=15306\
  --table_size=100000\
  --auto_inc=off\
  --db-ps-mode=disable\
  --db-driver=mysql\
  oltp_read_write run

