# Introduction

This handbook is a central collection point for all bits of knowledge that should be useful for anyone working on the **AMOS IDunion Team**. 

> **Contributions:** This handbook is not immutable - it is a great starting point for discussions and actually should live on its own. Please contribute to the handbook and update it by sending _Pull Requests_. 

# Table of Contents

## General
Here you can find all the general information related to our **AMOS IDunion project**.

  - [Software Architecture](https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/blob/main/Deliverables/sprint-04/software-architecture.pdf)
  - [Team Contract](https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/blob/main/Deliverables/sprint-03/team-contract-signed.pdf)
  - [Code of Conduct Branching](https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/blob/main/Documentation/CoC_Branches.md)
  - [Planning Documents](https://docs.google.com/spreadsheets/d/1Df1QpVa1ACSY_kTNegWYElVrmmdf_bSMS06VU6Qoe90/edit#gid=6)
  - [Product Goal](https://docs.google.com/spreadsheets/d/1Df1QpVa1ACSY_kTNegWYElVrmmdf_bSMS06VU6Qoe90/edit#gid=3)
  - [Product Glossary](https://docs.google.com/spreadsheets/d/1Df1QpVa1ACSY_kTNegWYElVrmmdf_bSMS06VU6Qoe90/edit#gid=12)
  - [Definition of Done](https://docs.google.com/spreadsheets/d/1Df1QpVa1ACSY_kTNegWYElVrmmdf_bSMS06VU6Qoe90/edit#gid=1495433969)
  - [Bill of Materials](https://docs.google.com/spreadsheets/d/1Df1QpVa1ACSY_kTNegWYElVrmmdf_bSMS06VU6Qoe90/edit#gid=927854276)

## Engineering
Here you can find all the technical information and set-up guides related to our **AMOS IDunion project**.
  - [Setup Script]()
    - A bash script for running the docker image of prometheus and grafana, node exporter and fetch_validator_status python script in a loop for the specified duration

  - [Indy Getting Started](https://hyperledger-indy.readthedocs.io/projects/sdk/en/latest/docs/getting-started/run-getting-started.html)
    - This is a simple way to test your set-up by using docker and git. 
  - [Indy Node Monitor](https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/tree/main/indy-node-monitor)
    - Indy Node Monitor is a set of tools for monitoring the status of an Indy Ledger by querying the validator information of the nodes of the ledger.
  - [Fetch Validator Status](https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/tree/main/indy-node-monitor/fetch-validator-status)
    - This is a simple tool that can be used to retrieve "validator-info" — detailed status data about an Indy node (aka "validator) — from all the nodes in a network.
  - [IDunion Node Monitoring](https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/blob/main/indy-node-monitor/setup_IDUnion_node_monitoring.md)
    - Follow these instructions to set up Prometheus and Grafana to monitor the nodes of the IDunion network.
  - [Grafana Dashboards](https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/tree/main/indy-node-monitor/grafana/dashboards)
    - This folder contains Grafana dashboards and a util directory with a python script that will take some of the output from run.sh (../fetch-validator-status/run.sh) and convert it to prometheus style output so that it can be read in and displayed in Grafana. The dashboards display Indy Network administrator type output that is useful for monitoring the status of an Indy Network as a whole and how well the indy-node software is running on each node.
  - [IDunion Blockchain Dashboard](https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/blob/main/Documentation/README.md)
    - Guide to set up Grafana and Prometheus by using de docker files given in the repository.
  - [JSON Tree Visualizer](https://github.com/amosproj/amos2022ss06-idunion-blockchain-dashboard/tree/main/data/vtree-master)
    - This tool converts JSON strings into tree diagrams. For example, it is used to show AST(Abstract Syntax Tree) as tree diagrams for debugging. In that case, of course, you need to translate AST into JSON.
