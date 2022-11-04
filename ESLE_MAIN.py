import os
from itertools import combinations, chain
import logging
import yaml

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

    pass

def disk(reset=False):
    pass

def automicity(reset=False):
    """
    https://vitess.io/docs/14.0/reference/features/two-phase-commit/
    multi is the default
    Clients can set the transaction mode via a session-variable:

    set transaction_mode='twopc';

    :param reset:
    :return:
    """
    global new_config
    "vtttable --enable_semi_sync"
    with open("operator/201_customer_tablets.yaml") as config:
        new_config = yaml.safe_load(config)
        new_config["spec"]["keyspaces"][1]["partitionings"][0]["shardTemplate"]["extraFlags"]["enforceSemiSync"] = False if reset else True
    with open("operator/201_customer_tablets.yaml", "w") as conf:
        yaml.dump(new_config, conf)
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
        new_config["spec"]["keyspaces"][1]["partitionings"][0]["shardTemplate"]["replication"]["enforceSemiSync"] = False if reset else True
    with open("operator/201_customer_tablets.yaml", "w") as conf:
        yaml.dump(new_config, conf)

# Build test configurations
factors = ["shards", "disk", "automicity", "ram", "cpu"] #"semi-sync" --> confounded
confounded = { "semi-sync" : ["ram", "shards"]}
tests = []
for f in factors:
    tests.append((f,))
for n in range(2,len(factors)+1):
    test_principal_factors = list(combinations(factors, n))
    for combo in test_principal_factors:
        test_all = combo
        for factor, dependencies in confounded.items():
            if all(d in combo for d in dependencies):
                test_all = test_all + (factor,)
        tests.append(test_all)

print(list(list(t) for t  in tests))

for t in tests:
    # set up enviroment
    for f in factors:
        if f not in t:
            eval("{}(True)".format(f))
        else:
            eval("{}()".format(f))
    # run tests
    healthy = os.system("kops validate cluster --wait 10m")
    print("WARNING Could not make sure system was healthy before starting benchmark! \nIteration:{}".format(t))
    print("Preparing database...")
    os.system(sysbench_prepare  + " > TEST" + str(t))
    print("Running test now...")
    os.system(sysbench_run  + " > TEST" + str(t))
    print("Just ran " + str(t))

exit()




