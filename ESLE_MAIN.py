import os
from itertools import combinations, chain
import logging

import numpy as np
import yaml



from sklearn import linear_model
regr = linear_model.LinearRegression()
X = np.array(
    [
    [-1,-1,1],
    [-1,1,-1],
    [1,-1,-1],
        [1,1,1,],

       [-1,-1,-1] ,
        [-1,1,1],
        [1,-1,1],
        [1,1,-1],
       ]
)
y = np.array(
    [66927,64512,65688,67788,

     65352, 63252, 65058, 62013

     ]
)
regr.fit(X, y)

print("The coefficients are: \n", regr.coef_)














exit()



logging.log(0," ▬▬ι═══════ﺤ  Built by Alexandre and Evandro     -═══════ι▬▬ ")

sysbench_prepare = """/usr/local/bin/sysbench --tables=1 --mysql-db=customer \
--mysql-user=user \
--mysql-host=127.0.0.1 \
--mysql-port=15306 \
--table_size=100000 \
--auto_inc=off \
--db-ps-mode=disable                    --db-driver=mysql \
oltp_read_write prepare
"""
sysbench_run = """sysbench --threads=4 --tables=1 --time=120 --mysql-db=customer --mysql-user=user --mysql-host=127.0.0.1 --mysql-port=15306 --table_size=100000 --auto_inc=off --db-ps-mode=disable --db-driver=mysql oltp_read_write run """

# Actuators
# They take the necessary actions to activate factors
# Reset puts the factor into "-1"/ disabled mode

def shards(reset=False):
    global new_config
    """
    :param reset:
    :return:
    """
    with open("operator/201_customer_tablets.yaml") as config:
        new_config = yaml.safe_load(config)
        new_config["spec"]["keyspaces"][1]["partitionings"][0]['parts'] = 1 if reset else 3
    with open("operator/201_customer_tablets.yaml", "w") as conf:
        yaml.dump(new_config, conf)


def disk(reset=False):
    with open("operator/101_initial_cluster.yaml") as config:
        new_config = list(yaml.load_all(config, yaml.FullLoader))[-1]
        new_config["stringData"]["init_db.sql"] = new_config["stringData"]["init_db.sql"].replace("SET sql_log_bin = 1; #nice", "SET sql_log_bin = 1; #nice" if not reset else "SET sql_log_bin = 0; #nice")
        new_config["stringData"]["init_db.sql"] = new_config["stringData"]["init_db.sql"].replace("SET sql_log_bin = 0; #nice", "SET sql_log_bin = 1; #nice" if not reset else "SET sql_log_bin = 0; #nice")
    with open("operator/101_initial_cluster.yaml", "w") as conf:
        yaml.dump(new_config, conf)

def automicity(reset=False):
    """
    https://vitess.io/docs/14.0/reference/features/two-phase-commit/
    multi is the default
    Clients can set the transaction mode via a session-variable:

    set transaction_mode='twopc';

    :param reset:
    :return:
    """

    """
    global new_config
    "vtttable --enable_semi_sync"
    with open("operator/201_customer_tablets.yaml") as config:
        new_config = yaml.safe_load(config)
        #new_config["spec"]["keyspaces"][1]["partitionings"][0]["shardTemplate"]["tabletPools"]["vttablet"]["extraFlags"]["enforceSemiSync"] = False if reset else True
        new_config["spec"]["keyspaces"][1]["partitionings"][0]["shardTemplate"]["tabletPools"]["vttablet"]["extraFlags"]["enforceSemiSync"] = False if reset else True
        new_config["spec"]["keyspaces"][1]["partitionings"][0]["shardTemplate"]["tabletPools"]["vttablet"]["extraFlags"]["enforceSemiSync"] = False if reset else True
    with open("operator/201_customer_tablets.yaml", "w") as conf:
        yaml.dump(new_config, conf)
    """
    pass

def ram(reset=False):
    """google cloud specific"""
    pass
def cpu(reset=False):
    """google cloud specific"""
    pass

def semi_sync(reset=False):
    global new_config
    "vtttable --enable_semi_sync"
    with open("operator/201_customer_tablets.yaml") as config:
        new_config = yaml.safe_load(config)
        new_config["spec"]["keyspaces"][1]["partitionings"][0]["equal"]["shardTemplate"]["replication"]["enforceSemiSync"] = False if reset else True
    with open("operator/201_customer_tablets.yaml", "w") as conf:
        yaml.dump(new_config, conf)

# Build test configurations
factors = ["shards", "ram", "disk", "semi_sync", "cpu"] #"semi-sync" --> confounded
confounded = {"ram" : ["shards", "semi_sync"]} # "semi-sync" : ["ram", "shards"]}
tests = []
for n in range(1,len(factors)+1):
    print(n)
    test_principal_factors = list(combinations(factors, n))
    for combo in test_principal_factors:
        test_all = combo
        for factor, dependencies in confounded.items():
            if all(d in combo for d in dependencies) or all(d not in combo for d in dependencies):
                test_all = test_all + (factor,)
        tests.append(test_all)

print(list(list(t) for t  in tests))

print(factors + list(confounded.keys()))
all = ""
for t in tests:
    # set up enviroment
    print("Run for ",t, "\n\n")
    excel = ""
    for f in (factors + list(confounded.keys())):
        if f not in t:
            eval("{}(True)".format(f))
            excel += "LOW\t"
        else:
            if f == "ram" or f == "cpu":
                print("Please set up", f)
            eval("{}()".format(f))
            excel += "HIGH\t"
    # run tests
    all += "\n"+excel

    input("WAITING for you to finish configuration, you should call ./run.sh now")


    print("Preparing database...")
    os.system(sysbench_prepare  + " > TEST" + str(t))
    print("Running test now...")
    os.system(sysbench_run  + " > TEST" + str(t))

    print("Just ran " + str(t))
    # delete the cluster
    os.system("kops delete cluster simple.k8s.local --yes")

print(all)




