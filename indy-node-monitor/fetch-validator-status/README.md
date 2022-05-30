# Fetch Validator Status

This folder contains a simple Python script that uses [indy-vdr](https://github.com/hyperledger/indy-vdr) to execute a "validator-info" call to an Indy network. The validator info transaction script returns a great deal of information about the accessed ledger. An example of the JSON data returned by the call for an individual node is provided [below](#example-validator-info).

The call can only be made by an entity with a suitably authorized DID on the ledger. For example, on the Sovrin MainNet, only Stewards and some within the Sovrin Foundation has that access.

The easiest way to use this now is to use the `./fetch_status_prometheus.py` script.

## How To Run

Here is guidance of how you can run the script to get validator info about any accessible Indy network. We'll start with a test on local network (using [von-network](https://github.com/bcgov/von-network)) and provide how this can be run on any Indy network, including Sovrin networks.

### Prerequisites

If you are running locally, you must have `git`, `docker` and a bash terminal.

The rest of the steps assume you are in your bash terminal in a folder where GitHub repos can be cloned.

### Start VON Network

To start a local Indy network to test with, we'll clone a VON Network, build it and start it using the following commands run in a bash terminal:

``` bash
git clone https://github.com/bcgov/von-network
cd von-network
./manage build
./manage start
cd ..

```

The build step will take a while as 1/3 of the Internet is downloaded. Eventually, the `start` step will execute and a four-node Indy ledger will start.  Wait about 30 seconds and then go to the web interface to view the network.

- If you are running locally, go to [http://localhost:9000](http://localhost:9000).
- If you are on Play with Docker, click the `9000` link above the terminal session window.

Note the last command above puts you back up to the folder in which you started. If you want to explore `von-network` you'll have to change back into the `von-network` folder.

When you are finished your running the validator tool (covered in the steps below) and want to stop your local indy-network, change to the von-network folder and run:

```bash
./manage down

```

We'll remind you of that later in these instructions.

### Install Indy-vdr
Following the instructions from [install_indy-vdr.md](install_indy-vdr.md) to setup Indy-vdr.


### Clone the indy-node-monitor repo

Run these commands to clone this repo so that you can run the fetch validator info command.

```bash
git clone https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard.git
cd amos2022ss06-idunion-blockchain-dashboard/indy-node-monitor/fetch-validator-status

```

### Run the Validator Info Script

For a full list of script options run:
``` bash
./fetch_status_prometheus.py -h
```

To get the details for the known networks available for use with the `--net` option, run:
``` bash
./fetch_status_prometheus.py --list-nets
```

To run the validator script, run the following command in your bash terminal from the `fetch-validator-status` folder in the `indy-node-monitor` clone:

``` bash
./fetch_status_prometheus.py --net=<netId> --seed=<SEED>
```
or
``` bash
./fetch_status_prometheus.py --genesis-url=<URL> --seed=<SEED>
```

To get the details in Prometheus format run:
``` bash
./fetch_status_prometheus.py --genesis-url=<URL> --seed=<SEED> -p

```

To just get a status summary for the nodes, run:
``` bash
./fetch_status_prometheus.py --net=<netId> --seed=<SEED> --status
```
or
``` bash
./fetch_status_prometheus.py --genesis-url=<URL> --seed=<SEED> --status
```

To fetch data for a single node, or a particular set of nodes use the `--nodes` argument and provide a comma delimited list of node names (aliases);
``` bash
./fetch_status_prometheus.py --net=<netId> --seed=<SEED> --status --nodes node1,node2
```

For the first test run using von-network:

- the `<SEED>` is the Indy test network Trustee seed: `000000000000000000000000Trustee1`.
- the URL is retrieved by clicking on the `Genesis Transaction` link in the VON-Network web interface and copying the URL from the browser address bar.

If you are running locally, the full command is:

``` bash
./fetch_status_prometheus.py --net=vn --seed=000000000000000000000000Trustee1
```
or
``` bash
./fetch_status_prometheus.py --genesis-url=http://localhost:9000/genesis --seed=000000000000000000000000Trustee1
```

To perform an anonymous connection test when a privileged DID seed is not available, omit the `SEED` (`-a` is no longer needed to perform an anonymous connection):

``` bash
./fetch_status_prometheus.py --net=<netId>
```
or
``` bash
./fetch_status_prometheus.py --genesis-url=<URL>
```

If running in the browser, you will have to get the URL for the Genesis file (as described above) and replace the `localhost` URL above.

You should see a very long JSON structure printed to the terminal. You can redirect the output to a file by adding something like `> good.json` at the end of the command.

If you use the Seed of a DID that does not have permission to see validator info, you will get a much shorter JSON structure containing access denied messages.



### Extracting Useful Information

Once you have the script running, you can write a plug-in that takes the JSON input and produces a more useful monitoring output file&mdash;probably still in JSON. Here is some information that would be useful to extract from the JSON output:

- Detect when a node is inaccessible (as with Node 1 above) and produce standard output for that situation.
- Detect any nodes that are accessible (populated JSON data) but that are "unreachable" to some or all of the other Indy nodes.
  - That indicates that the internal port to the node is not accessible, even though the public port is accessible.
- The number of transaction per Indy ledger, especially the domain ledger.
- The average read and write times for the node.
- The average throughput time for the node.
- The uptime of the node (time is last restart).
- The time since last freshness check (should be less than 5 minutes).

The suggestions above are only ideas. Precise meanings of the values should be investigated, particularly for "ledger" type data (e.g. number of transactions) but that are generated on a per node basis.

Note that there are three different formats for the timestamps in the data structure, and all appear to be UTC. Make sure to convert times into a single format during collection.


## Plug-ins

For info on plug-ins see the plug-ins [readme](plugins/README.md)

### Running against other Indy Networks

To see the validator info against any other Indy network, you need a URL for the Genesis file for the network, and the seed for a suitably authorized DID. The pool Genesis file URLs are easy, since that is published data needed by agents connecting to Indy networks. Sovrin genesis URLs can be found [here](https://github.com/sovrin-foundation/sovrin/tree/master/sovrin). You need the URL for the raw version of the pool transaction files. For example, the URL you need for the Sovrin MainNet is:

- [`https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_live_genesis`](`https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_live_genesis`)

For the other Sovrin networks, replace `live` with `sandbox` (Sovrin Staging Net) and `builder` (Sovrin Builder Net).

Getting a Seed for a DID with sufficient authorization on specific ledger is an exercise for the user. **DO NOT SHARE DID SEEDS**. Those are to be kept secret.

Do not write the Seeds in a public form. The use of environment variables for these parameters is very deliberate so that no one accidentally leaks an authorized DID.

Did I mention: **DO NOT SHARE DID SEEDS**?

## Example Validator info

The following is an example of the data for a single node from a VON-Network instance in Prometheus compatible format:

```bash
indy_node_validator_info_size{source="indy-node"}  11204
indy_total_nodes_count{node_name="Node1",source="indy_node"} 4
indy_reachable{node="Node1",node_name="Node1",source="indy_node"} 1
indy_primary_node{node="Node1",node_name="Node1",source="indy_node"} 0
indy_reachable{node="Node2",node_name="Node1",source="indy_node"} 1
indy_reachable{node="Node3",node_name="Node1",source="indy_node"} 1
indy_reachable{node="Node4",node_name="Node1",source="indy_node"} 1
indy_reachable_nodes_count{node_name="Node1",source="indy_node"} 4
indy_unreachable_nodes_count{node_name="Node1",source="indy_node"} 0
indy_sovrin_version{version="unknown",node_name="Node1",source="indy_node"} 0
indy_node_version{version="1.12.4",node_name="Node1",source="indy_node"} 0
indy_node_current_timestamp{node_name="Node1",source="indy_node"} 1653413471000
indy_delta{node_name="Node1",source="indy_node"} 0.1
indy_lambda{node_name="Node1",source="indy_node"} 240.0
indy_omega{node_name="Node1",source="indy_node"} 20.0
indy_instances_started{node_name="Node1",source="indy_node",ident="0"} 15423.601956658
indy_instances_started{node_name="Node1",source="indy_node",ident="1"} 15423.605604258
indy_ordered_request_counts{node_name="Node1",source="indy_node",ident="0"} 0.0
indy_ordered_request_counts{node_name="Node1",source="indy_node",ident="1"} 0.0
indy_ordered_request_durations{node_name="Node1",source="indy_node",ident="0"} 0.0
indy_ordered_request_durations{node_name="Node1",source="indy_node",ident="1"} 0.0
indy_max_master_request_latencies{node_name="Node1",source="indy_node"} 0.0
Skipping unknown node metric (TypeError): 'client avg request latencies'
indy_throughput{node_name="Node1",source="indy_node",ident="0"} 0.0
indy_throughput{node_name="Node1",source="indy_node",ident="1"} 0.0
Skipping unknown node metric (TypeError): 'master throughput'
indy_total_requests{node_name="Node1",source="indy_node"} 0.0
indy_avg_backup_throughput{node_name="Node1",source="indy_node"} 0.0
Skipping unknown node metric (TypeError): 'master throughput ratio'
indy_average_per_second{node_name="Node1",source="indy_node",ident="read_transactions"} 0.0184271315
indy_average_per_second{node_name="Node1",source="indy_node",ident="write_transactions"} 0.0
indy_transaction_count{node_name="Node1",source="indy_node",ident="ledger"} 5.0
indy_transaction_count{node_name="Node1",source="indy_node",ident="pool"} 4.0
indy_transaction_count{node_name="Node1",source="indy_node",ident="config"} 0.0
indy_transaction_count{node_name="Node1",source="indy_node",ident="audit"} 414.0
indy_uptime{node_name="Node1",source="indy_node"} 75920.0
indy_last_view_change{node_name="Node1",source="indy_node"} -3600.0
indy_consensus{node_name="Node1",source="indy_node"} 0

```
