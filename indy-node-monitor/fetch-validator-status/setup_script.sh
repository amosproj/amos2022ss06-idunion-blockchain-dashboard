#!/bin/bash

source variables


## function to loop the fetch_status_prometheus.py script for give sample size and export the data into a .prom file
function prom_data_loop() {
  counter=$1
  while [[ ${counter} > 0 ]]
  do
    counter=$(( ${counter} - 1 ))
    python3 ./fetch_status_prometheus.py --genesis-url=${genesis_url} --net=${net} --seed=${seed} ${prometheus}  | tee ${AMOS_PROJ_DIR}/data/prometheus/node_data.prom
    sleep 60
  done
}

function usage()
{
   cat << HEREDOC

   Usage: $progname [--net NET] [--genesis-url URL] [--seed SEED] [--samples SAMPLES] [--local JSON-LOCATION] [--prometheus] [--docker-setup] [--verbose]

   optional arguments:
     -h, --help			show this help message and exit
     -n, --net NET		pass in the network, default set to "bct"
     -u, --genesis-url URL	pass in the genesis url
     -s, --seed SEED		pass in the seed if different from 000000000000000000000000Trustee1
     -i, --samples SAMPLES	pass the number of samples, default is set to 120
     -p, --prometheus		output in prometheus format
     -d, --docker-setup		run the docker setup for prometheus and grafana if not already running
     -v, --verbose		increase the verbosity of the script
     -l, --local                convert the local json file to prometheus

HEREDOC
}  

## building von-network docker container
##cd ${VON_NET_DIR}
##./manage build
##./manage start
##wait
##echo "sleeping for 15s to allow the von network to setup"
##sleep 15

progname=$(basename $0)
genesis_url=""
seed="000000000000000000000000Trustee1"
samples=120
net="bct"
json_location=""
docker=false
verbose=0
local=false
#node_exporter="False"

OPTS=$(getopt -o "hn:u:s:i:l:pdv" --long "help,net:,genesis-url:,seed:,samples:,local:,prometheus,docker-setup,verbose" -n "$progname" -- "$@")
if [ $? != 0 ] ; then echo "Error in command line arguments." >&2 ; usage; exit 1 ; fi
eval set -- "$OPTS"

while true; do
  # uncomment the next line to see how shift is working
  # echo "\$1:\"$1\" \$2:\"$2\""
  case "$1" in
    -h | --help ) usage; exit; ;;
    -n | --net ) net="$2"; shift 2 ;;
    -u | --genesis-url ) genesis_url="$2"; shift 2 ;;
    -s | --seed ) seed="$2"; shift 2 ;;
    -i | --samples ) samples="$2"; shift 2 ;;	  
    -l | --local ) local=true ; json_location="$2" ; shift 2;;
    -p | --prometheus ) prometheus="-p"; shift ;;
    -d | --docker-setup ) docker=true ; shift ;;
    -v | --verbose ) verbose=$((verbose + 1)); shift ;;
    -- ) shift; break ;;
    * ) break ;;
  esac
done

if (( $verbose > 0 )); then

   # print out all the parameters we read in
   cat <<EOM
   net=$net
   seed=$seed
   samples=$samples
EOM
fi


if ! [ -z ${genesis_url} ]
then
	net=""
fi

sudo chmod -R 777 ${AMOS_PROJ_DIR}/data/grafana/

## building grafana and prometheus docker container
if $docker
then
	cd ${AMOS_PROJ_DIR}
	docker-compose up &
fi



## open the node exporter in another terminal for easy exit when necessary
#if $node_exporter
#then
	cd ${AMOS_PROJ_DIR}/indy-node-monitor/node_exp*
	gnome-terminal -- ./node_exporter --collector.disable-defaults --collector.textfile.directory=${AMOS_PROJ_DIR}"/data/prometheus/" --collector.textfile
#fi

## open the browser tabs for grafana, prometheus and node exporter 
for link in $(echo http://172.17.0.1:3000 http://172.17.0.1:9090/targets http://172.17.0.1:9100/metrics )
do
    xdg-open $link
done

if $local
then
  cd ${AMOS_PROJ_DIR}/indy-node-monitor/fetch-validator-status/
  python3 convert_json_to_prometheus.py ${json_location} | tee ${AMOS_PROJ_DIR}/data/prometheus/node_data.prom
else
  ## fetch the node metrics into the .prom file by running the above defined prom_data_loop function
  cd ${AMOS_PROJ_DIR}/indy-node-monitor/fetch-validator-status/
  prom_data_loop ${samples}
fi