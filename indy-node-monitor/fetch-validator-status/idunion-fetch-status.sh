#!/bin/bash

display_usage() {
        echo "This script executes fetch_status_prometheus.py with the IDunion configuration"
        echo -e "\nUsage: idunion-fetch-status.sh {SEED} [-p]\n"
        echo "Default output is in JSON format."
        echo "Use -p to get the output in prometheus format."
        }

# if less than one arguments supplied, display usage
        if [  $# -le 0 ]
        then
                display_usage
                exit 1
        fi

# if more than two arguments supplied, display usage
        if [  $# -ge 3 ]
        then
                display_usage
                exit 1
        fi

# check whether user had supplied -h or --help . If yes display usage
        if [[ ( $# == "--help") ||  $# == "-h" ]]
        then
                display_usage
                exit 0
        fi

# Execute fetch_status_prometheus.py with IDunion configuration
python3 ./fetch_status_prometheus.py --net iut --seed  $1 $2
