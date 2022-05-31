#!/bin/bash

function prom_data_loop() {
  counter=$1
  while [[ ${counter} > 0 ]]
  do
    counter=$(( ${counter} - 1 ))
    python3 ./fetch_status_prometheus.py --genesis-url=http://172.17.0.1:9000/genesis --seed=000000000000000000000000Trustee1 -p | tee ../../data/prometheus/node_data.prom
    sleep 60
  done
}

cd ../../..

## building von-network docker container
cd von-network/
./manage build
./manage start
read -p "how many samples: " SAMPLES

wait
sleep 15

## building grafana and prometheus docker container
cd ../amos2022ss06-idunion-blockchain-dashboard
docker-compose up &

## open the node exporter in another terminal for easy exit when necessary
cd indy-node-monitor/node_exp*
gnome-terminal -- node_exporter --collector.disable-defaults --collector.textfile.directory="../../data/prometheus/" --collector.textfile

firefox http://172.17.0.1:3000 http://172.17.0.1:9090/targets http://172.17.0.1:9100/metrics


## fetch the node metrics into the .prom file
cd ../fetch-validator-status/
prom_data_loop ${SAMPLES}
#./fetch_status_prometheus.py --genesis-url=http://172.17.0.1:9000/genesis --seed=000000000000000000000000Trustee1 -p | tee ../../data/prometheus/node_data.prom


