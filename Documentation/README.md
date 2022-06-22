# Idunion-blockchain-dashboard Setup
Clone repository with: git clone https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard.git

## Utils


## Node exporter setup
Run command: wget https://github.com/prometheus/node_exporter/releases/download/v1.3.1/node_exporter-1.3.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.3.1.linux-amd64.tar.gz
cd indy-node-monitor/node_exp*
gnome-terminal -- ./node_exporter --collector.disable-defaults --collector.textfile.directory="../amos2022ss06-idunion-blockchain-dashboard/data/prometheus/" --collector.textfile
firefox http://172.17.0.1:3000 http://172.17.0.1:9090/targets http://172.17.0.1:9100/metrics 

## Grafana and Prometheus setup
- Run docker-compose.yml file with: sudo docker-compose up

### Get Prometheus URL inside docker

- Get Container ID of Prometheus: sudo docker ps
- Get Prometheus docker URL: docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_name_or_id
- Copy the result URL

### Connect Grafana with Prometheus

- Open Grafana via ui: http://localhost:3000
- Login with default account username: admin and default password: admin
- Click configuration -> data source -> add data source
- Choose Prometheus database
- Paste the copied URL in format http://URL:9090
- Click save and test
