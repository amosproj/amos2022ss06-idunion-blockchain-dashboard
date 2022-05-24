# VON Network

- The code of this repository is forked from https://github.com/IDunion/indy-node-monitor. The original README.md can be seen in README.orig.md.
- The adaptation and bug fixes were done by Carlos Morra, Siemens AG.

### Start VON Network 

To start a local Indy network to test with, clone a VON Network, build it and start it using the following commands run in a bash terminal:

``` bash
git clone https://github.com/bcgov/von-network
cd von-network
./manage build
./manage start
cd ..

```

The build step will take a while as 1/3 of the Internet is downloaded. Eventually, the `start` step will execute and a four-node Indy ledger will start.  Wait about 30 seconds and then go to the web interface to view the network.

- If you are running locally, go to [http://localhost:9000](http://localhost:9000).
- If you are on Play with Docker, click the `9000` link above the terminal session window.

Note the last command above puts you back up to the folder in which you started. If you want to explore `von-network` you'll have to change back into the `von-network` folder.

When you are finished your running the validator tool (covered in the steps below) and want to stop your local indy-network, change to the von-network folder and run:

```bash
./manage down
```

### Clone the indy-node-monitor repo

Run these commands to clone this repo so that you can run the fetch validator info command.

```bash
git clone https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/indy-node-monitor
cd indy-node-monitor/fetch-validator-status

```

### Run the Validator Info Script

To get the details for the known networks available for use with the `--net` option, run:
``` bash
./run.sh --list-nets
```

To run the validator script, run the following command in your bash terminal from the `fetch-validator-status` folder in the `indy-node-monitor` clone:

``` bash
./run.sh --net=<netId> --seed=<SEED>
```
or
``` bash
./run.sh --genesis-url=<URL> --seed=<SEED>
```

To fetch data for a single node, or a particular set of nodes use the `--nodes` argument and provide a comma delimited list of node names (aliases);
``` bash
./run.sh --net=<netId> --seed=<SEED> --status --nodes node1,node2
```

For the first test run using von-network:

- the `<SEED>` is the Indy test network Trustee seed: `000000000000000000000000Trustee1`.
- the URL is retrieved by clicking on the `Genesis Transaction` link in the VON-Network web interface and copying the URL from the browser address bar.

If you are running locally, the full command is:

``` bash
./run.sh --net=vn --seed=000000000000000000000000Trustee1
```
or
``` bash
./run.sh --genesis-url=http://localhost:9000/genesis --seed=000000000000000000000000Trustee1
```

# Metrics Engine
### Extracting Useful Information

Once you have the script running, you can write a plug-in that takes the JSON input and produces a more useful monitoring output file&mdash;probably still in JSON. Here is some information that would be useful to extract from the JSON output:

- Detect when a node is inaccessible (as with Node 1 above) and produce standard output for that situation.
- Detect any nodes that are accessible (populated JSON data) but that are "unreachable" to some or all of the other Indy nodes.
  - That indicates that the internal port to the node is not accessible, even though the public port is accessible.
- The number of transaction per Indy ledger, especially the domain ledger.
- The average read and write times for the node.
- The average throughput time for the node.
- The uptime of the node (time is last restart).
- The time since last freshness check (should be less than 5 minutes).

The suggestions above are only ideas. Precise meanings of the values should be investigated, particularly for "ledger" type data (e.g. number of transactions) but that are generated on a per node basis.

Note that there are three different formats for the timestamps in the data structure, and all appear to be UTC. Make sure to convert times into a single format during collection.

# Prometheus & Grafana

- The code of this repository is forked from https://github.com/lynnbendixsen/indy-node-monitor (Lynn Bendixsen and contributors). The original README.md can be seen in README.orig.md.


1. Clone and configure (change) run.sh script (from indy-node-monitor)
    1. mkdir ~/github
    2. cd ~/github
    3. git clone [https://github.com/hyperledger/indy-node-monitor](https://github.com/hyperledger/indy-node-monitor)
    4. vi indy-node-monitor/fetch-validator-status/run.sh
    5. Edit the file as follows
        1. Remove the -i for running docker (NO LONGER REQUIRED - after a recent PR)
        2. Add the full path to each “docker” command (for cron)
            1. /usr/bin/docker
2. Configure indy_metrics.py
    1. vi ~/github/indy-node-monitor/dashboards/util/indy_metrics.py
        1. Change the location of run.sh in this file to match where it really is (fully qualified path is all I could get to work):
        2. /home/ubuntu/github/indy-node-monitor/fetch-validator-status/run.sh
3. Setup crontab to run indy_metrics.py for each network once every minute
    1. Create the output directories for node_exporter instances:
        1. sudo mkdir -p /var/log/node_exporter/9100
        2. sudo mkdir /var/log/node_exporter/9101
        3. sudo mkdir /var/log/node_exporter/9102
        4. sudo mkdir /var/log/node_exporter/9103
    2. sudo crontab -e 
```
    */1 * * * * python3 /home/ubuntu/github/indy-node-monitor/dashboards/util/indy_metrics.py https://raw.githubusercontent.com/Indicio-tech/indicio-network/master/genesis_files/pool_transactions_testnet_genesis (your ITN network monitor seed) >/var/log/node_exporter/9100/IndicioTestNet.prom
    */1 * * * * python3 /home/ubuntu/github/indy-node-monitor/dashboards/util/indy_metrics.py https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_builder_genesis (your BuilderNet network monitor seed) >/var/log/node_exporter/9101/SovrinBuilderNet.prom
    */1 * * * * python3 /home/ubuntu/github/indy-node-monitor/dashboards/util/indy_metrics.py https://raw.githubusercontent.com/sovrin-foundation/sovrin/stable/sovrin/pool_transactions_sandbox_genesis (your StagingNet network monitor seed) >/var/log/node_exporter/9102/SovrinStagingNet.prom
    */1 * * * * python3 /home/ubuntu/github/indy-node-monitor/dashboards/util/indy_metrics.py https://raw.githubusercontent.com/sovrin-foundation/sovrin/stable/sovrin/pool_transactions_live_genesis (your SovrinMainNet  network monitor seed) >/var/log/node_exporter/9103/SovrinMainNet.prom
```
4. Download, install, and enable Prometheus 
    1. sudo groupadd --system prometheus  
    3. sudo useradd -s /sbin/nologin --system -g prometheus prometheus
    4. sudo mkdir /var/lib/prometheus 
    5. for i in rules rules.d files_sd; do sudo mkdir -p /etc/prometheus/${i}; done
    6. mkdir -p /tmp/prometheus && cd /tmp/prometheus
    7. curl -s https://api.github.com/repos/prometheus/prometheus/releases/latest | grep browser_download_url | grep linux-amd64 | cut -d '"' -f 4 | wget -qi -
    8. tar xvf prometheus*.tar.gz
    9. cd prometheus*/
    10. sudo mv prometheus promtool /usr/local/bin/
    11. prometheus --version
    12. sudo mv consoles/ console_libraries/ /etc/prometheus/
    13. sudo tee /etc/systemd/system/prometheus.service&lt;<EOF

            [Unit]
            Description=Prometheus
            Documentation=https://prometheus.io/docs/introduction/overview/
            Wants=network-online.target
            After=network-online.target

            [Service]
            Type=simple
            User=prometheus
            Group=prometheus
            ExecReload=/bin/kill -HUP \$MAINPID
            ExecStart=/usr/local/bin/prometheus   --config.file=/etc/prometheus/prometheus.yml   --storage.tsdb.path=/var/lib/prometheus   --web.console.templates=/etc/prometheus/consoles   --web.console.libraries=/etc/prometheus/console_libraries   --web.listen-address=0.0.0.0:9090   --web.external-url=
            SyslogIdentifier=prometheus
            Restart=always

            [Install]
            WantedBy=multi-user.target
            EOF

    13. cat /etc/systemd/system/prometheus.service
        1. To double check the file just created
    14. vi /etc/prometheus/prometheus.yml  

                global:
                  scrape_interval: 15s
                  evaluation_interval: 15s # Evaluate rules every 15 seconds.

                scrape_configs:
                  - job_name: 'node-external'
                    static_configs:
                      - targets: ['localhost:9100', 'localhost:9101','localhost:9102', 'localhost:9103']
                        labels:
                          group: 'prod-ext'

    15. for i in rules rules.d files_sd; do sudo chown -R prometheus:prometheus /etc/prometheus/${i}; done
    16. for i in rules rules.d files_sd; do sudo chmod -R 775 /etc/prometheus/${i}; done
    17. sudo chown -R prometheus:prometheus /var/lib/prometheus/
    18. sudo systemctl daemon-reload
    19. sudo systemctl start prometheus
    20. sudo systemctl enable prometheus
    21. systemctl status prometheus
5. Configure and enable Node_Exporter (multiple running instances)
    1. sudo useradd -rs /bin/false node_exporter
    2. mkdir -p /tmp/node_exporter && cd /tmp/node_exporter
    3. wget [https://github.com/prometheus/node_exporter/releases/download/v1.0.1/node_exporter-1.0.1.linux-amd64.tar.gz](https://github.com/prometheus/node_exporter/releases/download/v1.0.1/node_exporter-1.0.1.linux-amd64.tar.gz)
    4. tar xvzf node_exporter*.tar.gz
    5. cd node_exporter*/
    6. sudo mv node_exporter /usr/local/bin
    7. sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
    8. cd /etc/systemd/system
    9. Now create 2 system files that will start the multiple node_exporters needed to scrape the files from multiple Indy Networks. I used info from this site as a guide: [https://www.stevenrombauts.be/2019/01/run-multiple-instances-of-the-same-systemd-unit/](https://www.stevenrombauts.be/2019/01/run-multiple-instances-of-the-same-systemd-unit/)
    10. sudo vi node_exporters.target

            [Unit]
            Description=Node Exporters
            Requires=node_exporter@9100.service node_exporter@9101.service node_exporter@9102.service node_exporter@9103.service 

            [Install]
            WantedBy=multi-user.target

    11. sudo vi node_exporter@.service

            [Unit]
            Description=”Node Exporter on port %i”
            After=network-online.target
            PartOf=node_exporters.target

            [Service]
            User=node_exporter
            Group=node_exporter
            Type=simple
            ExecStart=/usr/local/bin/node_exporter --collector.textfile.directory /var/log/node_exporter/%i --web.listen-address=":%i"

            [Install]
            WantedBy=multi-user.target

    12. sudo systemctl daemon-reload
    13. sudo systemctl start node_exporters.target
6. Install, configure, enable, secure, Grafana as a web server (nginx)
    1. I relied heavily on the instructions found at [How To Install and Secure Grafana on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-grafana-on-ubuntu-18-04)
    2. Setup domain names
        1. indymonitor.indiciotech.io
        2. [www.indymonitor.indiciotech.io](www.indymonitor.indiciotech.io) (I am not sure this one is required…)
    3. Install nginx by following the instructions at the 2 major links following:
        1. [How To Install Nginx on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04)
            1. Add these commands to what the guide has (near the beginning)
            2. sudo ufw allow 'OpenSSH'
            3. sudo ufw enable
            4. (also open ports 80 and 443 in your AWS or other firewalls)
            5. I also followed step 5 to set up a server block.
        2. [How To Secure Nginx with Lets Encrypt on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04)
            1. If everything runs correctly and you followed the steps in 9.2.1 then the following few commands should be all you need (this will save lots of reading and double-checking what you already did):
            2. sudo add-apt-repository ppa:certbot/certbot
            3. sudo apt install python-certbot-nginx
            4. sudo certbot --nginx -d indymonitor.indiciotech.io -d www.indymonitor.indiciotech.io
            5. To check if renewals will work:
                1. sudo certbot renew --dry-run
    4. Install grafana: (I used the following resource as an excellent guide, [How To Install and Secure Grafana on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-grafana-on-ubuntu-18-04), but abbreviated many of the actions from step 1 and 2 here.)
        1. wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
        2. sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
        3. sudo apt update
        4. Verify that grafana is coming from the right place
            1. apt-cache policy grafana
            2. The following should be where it is getting grafana: [https://packages.grafana.com/oss/deb](https://packages.grafana.com/oss/deb)
        5. sudo apt install grafana
        6. sudo systemctl start grafana-server
        7. sudo systemctl status grafana-server
        8. sudo systemctl enable grafana-server
    5. Install a reverse proxy
        1. Follow step 2 (only) at [How To Install and Secure Grafana on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-grafana-on-ubuntu-18-04) or the following abbreviated steps:
        2. sudo vi /etc/nginx/sites-available/indymonitor.indiciotech.io
            1. Delete the “try_files” line and replace it with 
            2. <code>proxy_pass [http://localhost:3000](http://localhost:3000);</code>
        3. sudo systemctl reload nginx
    6. Setup Grafana to allow for Anonymous(public) Access
        1. This is generally frowned upon, if I am not mistaken, because the data source will also be made public.  In this case, I believe the data is already public, so access to it is not bad.
        2. sudo vi /etc/grafana/grafana.ini
            1. Uncomment and change the following line in the [users] section
                1. allow_sign_up = false 
            2. Uncomment and change the following lines in the [auth.anonymous] section
                1. enabled = true
                2. org_name = Indy
                3. org_role = Viewer
        3. sudo systemctl restart grafana-server
    7. Login to your grafana server to complete the initial setup
        1. [https://indymonitor.indiciotech.io/login](https://indymonitor.indiciotech.io/login)
        2. admin admin (default login)
        3. Change the password as per the prompt to do so (this is required as your dashboards will be publicly available, but only alterable by the admin)
    8. Create an organization (matching what was added to the grafana.ini file)
        1. Click the shield on the bottom of the left menu bar and select ‘Orgs’
        2. Click “+ New org” then type in “Indy” and click ‘Create’
    9. Configure a data source
        1. Click the gear icon on the left menu and select ‘Data Sources’
        2. Click ‘Add data source’ and select ‘Prometheus’
    10. Create/Copy a dashboard
        1. Click the big + sign in the left menu, and select ‘Import’
        2. Upload the JSON file(s) matching the dashboard that you want to use as template (or initial) dashboards from the github repo ‘hyperledger/indy-node-monitor’.
        3. Repeat for as many dashboards as you would like to upload.
    11. Select a default Dashboard for your organization
        1. Select the dashboard that you want visitors to see when they come to the site.
        2. Next to the name of the dashboard in the upper left corner, click on the empty star to mark this dashboard as a favorite. (this can be done for multiple dashboards, but you will only end up selecting one as the final default dashboard)
        3. Click on the Gear icon in the left menu bar and select ‘Preferences’
        4. In ‘Home Dashboard’ select the dashboard that you want the public anonymous visitors to see when they first get to the site.