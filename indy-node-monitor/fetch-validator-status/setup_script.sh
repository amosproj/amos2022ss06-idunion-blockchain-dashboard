#!/bin/bash

source variables


## function to loop the fetch_status_prometheus.py script for give sample size and export the data into a .prom file
function prom_data_loop() {
  counter=$1
  while [[ ${counter} > 0 ]]
  do
    counter=$(( ${counter} - 1 ))
    python3 ./fetch_status_prometheus.py --genesis-url=${URL} --seed=${SEED} -p | tee ../../data/prometheus/node_data.prom
    sleep 60
  done
}


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
gnome-terminal -- node_exporter --collector.disable-defaults --collector.textfile.directory="../../data/prometheus/" --collector.textfile


## open the browser tabs for grafana, prometheus and node exporter 
for link in $(echo http://172.17.0.1:3000 http://172.17.0.1:9090/targets http://172.17.0.1:9100/metrics )
do
    xdg-open $link
done


## fetch the node metrics into the .prom file by running the above defined prom_data_loop function
cd ../fetch-validator-status/
prom_data_loop ${SAMPLES}
