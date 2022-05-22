# Idunion-blockchain-dashboard Setup
Clone repository with: git clone https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard.git

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
- Paste the copied URL
- Click save and test
