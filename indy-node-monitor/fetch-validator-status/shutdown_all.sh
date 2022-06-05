#!/bin/bash
source variables

## close von-network docker container
cd ${VON_NET_DIR}
./manage down

## close grafana and prometheus docker container
cd ${AMOS_PROJ_DIR}
docker-compose down &

## close node exporter
pkill node_expo
