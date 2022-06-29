# Setup script
This is a bash script that takes flag inputs and can be used for:
- running the docker image of prometheus and grafana 
- running the node exporter
- running the fetch validator status python script in  a loop for the specified duration

## How to run
### Clone the Idunion-blockchain-dashboard repo
Run these commands to clone this repo so that you can run the setup script.

```bash
git clone https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard.git
cd amos2022ss06-idunion-blockchain-dashboard/indy-node-monitor/fetch-validator-status

```
### Python environment
Make sure to be in the python environment that has the requirements of [Indy-vdr](https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/blob/main/indy-node-monitor/fetch-validator-status/install_indy-vdr.md) fulfilled.

### Run the setup script
For full list of script options run:
```bash
bash setup_script.sh -h 
```

For running docker image of prometheus and grafana and output in prometheus format, 
with the default network of "British Colombia testnet" and sample size of 
120 (1 sample every minute). The node exporter is running by default but will
display the node metrics in the port 9100 only when the prometheus flag (-p) is passed 
```bash
bash setup_script.sh -d -p
```

For running with the same with a different [network](https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/blob/main/indy-node-monitor/fetch-validator-status/networks.json)
and sample size
```bash
bash setup_script.sh -d -n NET -i SAMPLES -p
```

### Ports of Grafana, Prometheus and node_exporter
Grafana: 3000 \
Prometheus: 9090 \
node_exporter: 9100
