# Vitess scalability

The goal of this project is to study the scalability and performance of the Vitess database system.
This README file describes the steps followed so far.

## Getting started

In order to run our tests, Vitess was run with the Vitess Operator for Kubernetes, at version 15.0 (RC).
The dependencies are Minikube, kubectl, the MySQL client and the vtctlclient application.

### Kubernetes setup

    minikube start --kubernetes-version=v1.19.16 --cpus=4 --memory=4000 --disk-size=32g

### Deploying Vitess

The required YAML files to deploy Vitess via Kubernetes are in the operator directory.

    kubectl apply -f operator/operator.yaml
    kubectl apply -f operator/101_initial_cluster.yaml
    kubectl apply -f operator/201_customer_tablets.yaml

To customize the number of shards, change partitionings/equal/parts parameter in the two later yaml files to the number of shards (1 for a single/unsharded, etc).

### Port Forward on Host Machine

To access our Vitess setup from the host machine, use the following script along setting the aliases in the shell environment.

    ./operator/pf.sh

    alias vtctlclient="vtctlclient --server=localhost:15999 --logtostderr"
    alias mysql="mysql -h 127.0.0.1 -P 15306 -u user"

### Create Sharding Schema for Test table

In order to set up sharding in the MySQL table used to benchmark, a VSchema file is required. Use the following command to apply it:

    vtctlclient ApplyVSchema -- --vschema="$(cat operator/vschema.json)" customer

### Prepare and run sysbench

Finally, the benchmark used to test the system was a modified version of sysbench to better support Vitess in the MySQL driver. It can be found at https://github.com/planetscale/sysbench

The following two commands prepare and then run the benchmark.

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
    --threads=1\
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

### Updating graphs

The two graphs can be generated with gnuplot. To update the Universal Scalability Model graph, first update the universalscalabilitymodel.csv file with your data and run a program to find the values of Delta, Lambda and Kappa. Then update those values and range in the universalcalabilitymodel.gp file.
