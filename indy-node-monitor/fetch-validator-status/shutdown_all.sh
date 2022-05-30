#!/bin/bash

cd ../../..

## close von-network docker container
cd von-network/
#./manage down

## close grafana and prometheus docker container
cd ../amos2022ss06*/
docker-compose down &

## close node exporter
pkill node_expo