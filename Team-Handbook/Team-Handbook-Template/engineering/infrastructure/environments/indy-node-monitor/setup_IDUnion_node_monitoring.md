# Local prometheus and node exporter installation.
Instructions adapted from  https://github.com/lynnbendixsen/indy-node-monitor/tree/master/dashboards
 
## Node Exporter configuration
- Create directory for the node exporter data
```
$ CURRENT_DIR=$PWD
$ sudo mkdir -p /var/log/node_exporter/9100
```
- Add the crontab line to execute "fetch_status_prometheus.py" every minute
```
$ sudo crontab -e 
```
Example:  
```
*/1 * * * * python3 PATH_TO_INDY_MONITORING/fetch_status_prometheus.py --net iut --seed MONITORING_SEED -p >  /var/log/node_exporter/9100/IDUnion.prom
```
- Alternatively fetch_status_prometheus.py can be run as part of the docker image with run.sh;  or directly in python3 after installing indy-vdr (see steps in install_indy-vdr.md)

## Download, install, and enable Prometheus
- Add user and group for prometheus 
```
$ sudo groupadd --system prometheus
$ sudo useradd -s /sbin/nologin --system -g prometheus prometheus
```
- Create directories and copy rules to /etc/prometheus
```
$ sudo mkdir /var/lib/prometheus
$ for i in rules rules.d files_sd; do sudo mkdir -p /etc/prometheus/${i}; done
```
- Download and install latest release 
```
$ mkdir -p /tmp/prometheus && cd /tmp/prometheus
$ curl -s https://api.github.com/repos/prometheus/prometheus/releases/latest | grep browser_download_url | grep linux-amd64 | cut -d '"' -f 4 | wget -qi -
$ tar xvf prometheus*.tar.gz
$ cd prometheus*/
$ sudo mv prometheus promtool /usr/local/bin/
```
- Check if prometheus was installed correctly
```
$ prometheus --version
```
- Copy files to /etc
```
$ sudo mv consoles/ console_libraries/ /etc/prometheus/
```
- Copy systemd services and yml file to etc
```
$ sudo cp $CURRENT_DIR/etc/systemd/system/prometheus.service /etc/systemd/system/prometheus.service 
$ sudo cp $CURRENT_DIR/etc/prometheus/prometheus.yml /etc/prometheus/prometheus.yml
```
- Set owner, group and file permissions
```
$ for i in rules rules.d files_sd; do sudo chown -R prometheus:prometheus /etc/prometheus/${i}; done
$ for i in rules rules.d files_sd; do sudo chmod -R 775 /etc/prometheus/${i}; done
$ sudo chown -R prometheus:prometheus /var/lib/prometheus/
```
- Enable prometheus systemd service
```
$ sudo systemctl daemon-reload
$ sudo systemctl start prometheus
$ sudo systemctl enable prometheus
$ systemctl status prometheus
```
## Configure and enable Node_Exporter (multiple running instances)
- Add user for node_exporter
```
$ sudo useradd -rs /bin/false node_exporter
```
- Download and install node_exporter
```
$ mkdir -p /tmp/node_exporter && cd /tmp/node_exporter
$ wget https://github.com/prometheus/node_exporter/releases/download/v1.0.1/node_exporter-1.0.1.linux-amd64.tar.gz
$ tar xvzf node_exporter*.tar.gz
$ cd node_exporter*/
$ sudo mv node_exporter /usr/local/bin
$ sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
```
- Copy systemd services for node_exporter
```
$ sudo cp  $CURRENT_DIR/etc/systemd/system/node_exporters.target /etc/systemd/system/node_exporters.target 
$ sudo cp  $CURRENT_DIR/etc/systemd/system/node_exporter@.service /etc/systemd/system/node_exporter@.service
```
- Enable node_exporter systemd service
```
$ sudo systemctl daemon-reload
$ sudo systemctl start node_exporters.target
$ sudo systemctl enable node_exporters.target
```

## Install, configure, enable, Grafana as a web server
- Run grafana in a docker container or use docker-compose.yml in the grafana directory
```
$ docker run -d -p 3000:3000 grafana/grafana
```
- Log into grafana at http://SERVER_IP_ADDRESS:3000 for further configuration
- Add prometheus source to grafana
- Add dashboards to grafana and/or import dashboards from the grafana directory
- Configure alert_channels and alerts in grafana
