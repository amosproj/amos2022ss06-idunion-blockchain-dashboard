#!/bin/bash

source variables


## function to loop the fetch_status_prometheus.py script for give sample size and export the data into a .prom file
function act() {
  python3 ./fetch_status_prometheus.py --genesis-url=${URL} --seed=${SEED} -p | tee ../../src/test/node_data.prom
}

function assert() {
  python3 ./prometheus_format_test.py
}

function clean_data() {
  rm *.json
  rm *.prom
}

## Arrange

## building von-network docker container
cd ${VON_NET_DIR}
./manage build
./manage start

wait
echo "sleeping for 15s to allow the von network to setup"
sleep 15


## building grafana and prometheus docker container
cd ${AMOS_PROJ_DIR}
docker-compose up &


## open the node exporter in another terminal for easy exit when necessary
cd indy-node-monitor/node_exp*
gnome-terminal -x -- node_exporter --collector.disable-defaults --collector.textfile.directory="../../data/prometheus/" --collector.textfile
# ./node_exporter --collector.disable-defaults --collector.textfile.directory="../amos2022ss06-idunion-blockchain-dashboard/data/prometheus" --collector.textfile

## fetch the node metrics into the .prom file by running the above defined prom_data_loop function
cd ../fetch-validator-status/

# Act Assert and Delete unneeded data
act
# Change directory to test directory
cd ../../src/test
assert
clean_data