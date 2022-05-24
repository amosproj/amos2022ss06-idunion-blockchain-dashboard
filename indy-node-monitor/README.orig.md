# Indy Node Monitor

Indy Node Monitor is a set of tools for monitoring the status of an Indy Ledger by querying the validator information of the nodes of the ledger. Based on that, data can be generated data suitable for:

* visualization on a dashboard
* tracking trends about the status of nodes and the overall ledger
* tracking read and write uptimes
* tracking ledger usage such as number of transactions on the ledger
* driving notifications of node outages

The repo has basic tools to collect and format data and tools for using that data in different ways.

Contributions are welcome of tools that consume the collected data to enable easy ways to monitor an Indy network, such as configurations of visualization dashboards that can be deployed by many users. For example, an ELK stack or Splunk configuration that receives validator info and presents it in a ledger dashboard. Or an interface to [Pager Duty](https://www.pagerduty.com/) to enable node outage notifications.

## Fetch Validator Status

This is a simple tool that can be used to retrieve "validator-info"&mdash;detailed status data about an Indy node (aka "validator)&mdash;from all the nodes in a network. The results are returned as: 
- JSON array with a record per validator (default)
- Prometheus format (with option -p)

For more details see the Fetch Validator Status [readme](fetch-validator-status/README.orig.md)

## Authors
- The code of this repository is forked from https://github.com/lynnbendixsen/indy-node-monitor (Lynn Bendixsen and contributors).
The original README.md can be seen in README.orig.md.

## Installation and configuration: 
See [setup](setup_IDUnion_node_monitoring.md) and [install indy vdr](install_indy-vdr.md).

## Code of Conduct

All contributors are required to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) guidelines.

## License

[Apache License Version 2.0](LICENSE)
