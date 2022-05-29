#!/usr/bin/env python3
import argparse
import asyncio
import base58
import base64
import json
import re
#import subprocess
import time
import os
import sys
import datetime
import urllib.request
from typing import Tuple

import base58
import nacl.signing

import indy_vdr

from indy_vdr.ledger import (
    build_get_validator_info_request,
    build_get_txn_request,
    Request,
)
from indy_vdr.pool import open_pool


verbose = False
prometheus = False

label = "indy_node"

def log(*args):
    if verbose:
        print(*args, "\n", file=sys.stderr)

class DidKey:
    def __init__(self, seed):
        seed = seed_as_bytes(seed)
        self.sk = nacl.signing.SigningKey(seed)
        self.vk = bytes(self.sk.verify_key)
        self.did = base58.b58encode(self.vk[:16]).decode("ascii")
        self.verkey = base58.b58encode(self.vk).decode("ascii")

    def sign_request(self, req: Request):
        signed = self.sk.sign(req.signature_input)
        req.set_signature(signed.signature)


def seed_as_bytes(seed):
    if not seed or isinstance(seed, bytes):
        return seed
    if len(seed) != 32:
        return base64.b64decode(seed)
    return seed.encode("ascii")


async def fetch_status(genesis_path: str, nodes: str = None, ident: DidKey = None, status_only: bool = False, alerts_only: bool = False):
    pool = await open_pool(transactions_path=genesis_path)
    result = []
    verifiers = {}

    if ident:
        request = build_get_validator_info_request(ident.did)
        ident.sign_request(request)
    else:
        request = build_get_txn_request(None, 1, 1)

    from_nodes = []
    if nodes:
        from_nodes = nodes.split(",")
    response = await pool.submit_action(request, node_aliases = from_nodes)
    try:
        # Introduced in https://github.com/hyperledger/indy-vdr/commit/ce0e7c42491904e0d563f104eddc2386a52282f7
        verifiers = await pool.get_verifiers()
    except AttributeError:
        pass

    primary = ""
    packages = {}
    for node, val in response.items():
        jsval = []
        status = {}
        errors = []
        warnings = []
        info = []
        entry = {"name": node}
        try:
            await get_node_addresses(entry, verifiers)
            jsval = json.loads(val)
            if not primary:
                primary = await get_primary_name(jsval, node)
            errors, warnings = await detect_issues(jsval, node, primary, ident)
            info = await get_info(jsval, ident)
            packages[node] = await get_package_info(jsval)
        except json.JSONDecodeError:
            errors = [val]  # likely "timeout"

        # Status Summary
        entry["status"] = await get_status_summary(jsval, errors)
        # Info
        if len(info) > 0:
            entry["status"]["info"] = len(info)
            entry["info"] = info
        # Errors / Warnings
        if len(errors) > 0:
            entry["status"]["errors"] = len(errors)
            entry["errors"] = errors
        if len(warnings) > 0:
            entry["status"]["warnings"] = len(warnings)
            entry["warnings"] = warnings
        # Full Response
        if not status_only and jsval:
            entry["response"] = jsval

        result.append(entry)

    # Package Mismatches
    if packages:
        await merge_package_mismatch_info(result, packages)

    # Connection Issues
    await detect_connection_issues(result)

    # Filter on alerts
    if alerts_only:
        filtered_result = []
        for item in result:
            if ("info" in item["status"]) or ("warnings" in  item["status"]) or ("errors" in  item["status"]):
                filtered_result.append(item)
        result = filtered_result

    data=json.dumps(result, indent=2)
    if (prometheus==False):
        print(data)
    else:
        output_prometheus(str(data))


def process_data_prometheus_1_5(data):
    node_info = data['Node_info']
    node_name = node_info['Name']
    metrics = node_info['Metrics']
    pool_metrics = data['Pool_info']
    version_metrics = data['Software']
    #Process Pool related metrics
    for metric in pool_metrics:
        # If it is a "count" metric, assume that the value is a number and good to go
        if 'count' in metric:
            try:
                float(pool_metrics[metric])
                val = pool_metrics[metric]
                print('indy_{metric}{{node_name="{node_name}",source="{label}"}} {value}'.format(
                        metric=metric.replace('-','_').replace(' ','_').lower(),
                        node_name=node_name,
                        label=label,
                        value=val
                    )
                )
            except ValueError:
                sys.stderr.write("Skipping unknown pool metric: '{}'\n".format(metric))
            continue
        # If it is a reachable nodes one, then is probably a list and process these two metrics
        if metric.lower() in [ 'unreachable_nodes','reachable_nodes' ]:
            if metric.lower() == 'reachable_nodes':
                val = 1
            else:
                val = 0
            for node in pool_metrics[metric]:
                if isinstance(node,list):
                    node_real = node[0]
                else:
                    node_real = node
                print('indy_reachable{{node="{node}",node_name="{node_name}",source="{label}"}} {value}'.format(
                        node=node_real,
                        node_name=node_name,
                        label=label,
                        value=val
                    )
                )
                if 0 == node[1]: 
                    print('indy_primary_node{{node="{node}",node_name="{node_name}",source="{label}"}} {value}'.format(
                            node=node_real,
                            node_name=node_name,
                            label=label,
                            value=0
                        )
                    )
            continue
    #Print version metrics directly
    print('indy_sovrin_version{{version="{version}",node_name="{node_name}",source="{label}"}} {value}'.format(
            version=version_metrics['sovrin'],
            node_name=node_name,
            label=label,
            value=0
        )
    )
    print('indy_node_version{{version="{version}",node_name="{node_name}",source="{label}"}} {value}'.format(
            version=version_metrics['indy-node'],
            node_name=node_name,
            label=label,
            value=0
        )
    )

    #Print timestamp metric directly
    print('indy_node_current_timestamp{{node_name="{node_name}",source="{label}"}} {value}'.format(
            node_name=node_name,
            label=label,
            value=data['timestamp']*1000
        )
    )

    #Process general Metrics
    for metric in metrics:
        try:
            metric_obj = metrics[metric]
            # If it is a dictionary, go one level deep and check if it is a value
            if isinstance(metric_obj,dict):
                for name in metric_obj:
                    # See if the value is a number and use it
                    try:
                        val = float(metric_obj[name])
                        print('indy_{metric}{{node_name="{node_name}",source="{label}",ident="{ident}"}} {value}'.format(
                                metric=metric.replace('-','_').replace(' ','_').lower(),
                                node_name=node_name,
                                label=label,
                                ident=name.replace('-','_').replace(' ','_').lower(),
                                value=val
                            )
                        )
                    # Must not be a number, flatten the object (works for a List or a Dict), then make
                    # some guesses about what the metric name should be, and a "name" for future filtering
                    except TypeError:
                        flat_d = flatten_dict(metric_obj,'|')
                        for name_key in flat_d:
                            val = float(flat_d[name_key])
                            name_split = name_key.split('|')
                            name = name_split[-1]
                            key = '_'.join(name_split[:-1])
                            print('indy_{metric}_{key}{{name="{name}",node_name="{node_name}",source="{label}"}} {value}'.format(
                                    metric=metric.replace('-','_').replace(' ','_').lower(),
                                    key=key,
                                    name=name,
                                    node_name=node_name,
                                    label=label,
                                    value=val
                                )
                            )
            # If is a list, flatten it and use the index number as a label for future filtering.
            elif isinstance(metric_obj,list):
                flat_d = flatten_dict(metric_obj)
                for idx in flat_d:
                    val = float(flat_d[idx])
                    print('indy_{metric}{{index="{idx}",node_name="{node_name}",source="{label}"}} {value}'.format(
                            metric=metric.replace('-','_').replace(' ','_').lower(),
                            idx=idx,
                            node_name=node_name,
                            label=label,
                            value=val
                        )
                    )
            else:
                raise TypeError
        # This catches any other accidental misshandling of Types. Triggered by things like, trying to
        # cast a string to a float etc...
        except TypeError:
            # Try one more way of getting usefuly data out of the metric, before giving up on it.
            try:
                val = float(metrics[metric])
                print ('indy_{metric}{{node_name="{node_name}",source="{label}"}} {value}'.format(
                        metric=metric.replace('-','_').replace(' ','_').lower(),
                        node_name=node_name,
                        label=label,
                        value=val
                    )
                )
            except ValueError:
                sys.stderr.write("Skipping unknown node metric (ValueError): '{}'\n".format(metric))
            except TypeError:
                sys.stderr.write("Skipping unknown node metric (TypeError): '{}'\n".format(metric))

    # Process view change information.
    vc_changed = node_info['View_change_status']['Last_view_change_started_at']
    vc_changed = time.mktime(
        time.strptime(
            vc_changed,
            '%Y-%m-%d %H:%M:%S'
        )
    )
    print('indy_last_view_change{{node_name="{node_name}",source="{label}"}} {vc_changed}'.format(
            node_name=node_name,
            label=label,
            vc_changed=vc_changed
        )
    )

    # Process consensus information.
    consensus_metrics = node_info['Freshness_status']
    in_consensus=0
    for metric in consensus_metrics:
        pool_num=consensus_metrics[metric]
        if not pool_num['Has_write_consensus']:
            in_consensus=in_consensus+1
    print('indy_consensus{{node_name="{node_name}",source="{label}"}} {consensus}'.format(
            node_name=node_name,
            label=label,
            consensus=in_consensus
        )
    )


def output_prometheus(data_json):
    all_node_data = json.loads(filter_timestamps(data_json.replace("\r\n","")))

    all_node_data_size=len(data_json)     

  #  all_node_data = json.loads(filter_timestamps(str(data_json).replace("\r\n","")))
    
    for node in all_node_data: 
#        print(node["name"])
        if ('response' not in node):
            # Do some sort of metric stating "node not responding"?
            continue
        if (node['response']['op'] != "REPLY"):  # Skip nodes that dont  respond with REPLY 
            sys.stderr.write("Error: Node \""+node['name']+"\" responded with "+ node['response']['op'])
            continue
        data = node['response']['result']['data']
        if not data:
            sys.stderr.write("Error: No data")
            sys.exit(1)
        try:
            node_ver = data['Software']['indy-node']
        except KeyError:
            try:
                node_ver = data['software']['indy-node']
            except KeyError:
        #        try:
         #           cmd = ['/usr/bin/dpkg-query', '-f', "'${Version}\\n'", '-W', 'indy-node']
                #     dpq = subprocess.Popen(cmd,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                #     dpq_out,dpq_stderr = dpq.communicate()
                #     if dpq.returncode > 0:
                #         sys.stderr.write(dpq_stderr)
                #         sys.stderr.write("\nERROR: indy-node package isn't installed! Can't proceed\n")
                #         sys.exit(2) 
                #     node_ver = dpq_out.decode()
                # except subprocess.SubprocessError:
                #     exc_type, exc_value, exc_traceback = sys.exc_info()
                #     exc_str = "{}: {}".format(exc_type.__name__, exc_value)
                #     sys.stderr.write("Subprocess Error during execution of command: {cmd} Error: '{exc_str}'".format(cmd=cmd, exc_str=exc_str))
                #     sys.exit(2)
                sys.stderr.write("Error: KeyError")
                sys.exit(2) 

        print('indy_node_validator_info_size{source="indy-node"} ',all_node_data_size)

        for v in [ node_ver, '.'.join(node_ver.split('.')[:-1]), 'latest' ]:
            try:
                process_data_prometheus_1_5(data)
                break
            except KeyError:
                pass
 
async def get_node_addresses(entry: any, verifiers: any) -> any:
    if verifiers:
        node_name = entry["name"]
        if "client_addr" in verifiers[node_name]:
            entry["client-address"] = verifiers[node_name]["client_addr"]
        if "node_addr" in verifiers[node_name]:
            entry["node-address"] = verifiers[node_name]["node_addr"]


async def detect_connection_issues(result: any) -> any:
    for node in result:
        connection_errors = []
        node_name = node["name"]
        if "warnings" in node:
            for warning in node["warnings"]:
                if "unreachable_nodes" in warning :
                    for item in warning["unreachable_nodes"]["nodes"].split(', '):
                        # This is the name of the unreachable node.  Now we need to determine whether that node can't see the current one.
                        # If the nodes can't see each other, upgrade to an error condition.
                        unreachable_node_name = item
                        unreachable_node_query_result = [t for t in result if t["name"] == unreachable_node_name]
                        if unreachable_node_query_result:
                            unreachable_node = unreachable_node_query_result[0]
                            if "warnings" in unreachable_node:
                                for unreachable_node_warning in unreachable_node["warnings"]:
                                    if "unreachable_nodes" in unreachable_node_warning :
                                        for unreachable_node_item in unreachable_node_warning["unreachable_nodes"]["nodes"].split(', '):
                                            if unreachable_node_item == node_name:
                                                connection_errors.append(node_name + " and " + unreachable_node_name + " can't reach each other.")

        # Merge errors and update status
        if connection_errors:
            if "errors" in node:
                for item in connection_errors:
                    node["errors"].append(item)
            else:
                node["errors"] = connection_errors
            node["status"]["errors"] = len(node["errors"])
            node["status"]["ok"] = (len(node["errors"]) <= 0)


async def get_primary_name(jsval: any, node: str) -> str:
    primary = ""
    if "REPLY" in jsval["op"]:
        if "Node_info" in jsval["result"]["data"]:
            primary = jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"]
    return primary


async def get_status_summary(jsval: any, errors: list) -> any:
    status = {}
    status["ok"] = (len(errors) <= 0)
    if jsval and ("REPLY" in jsval["op"]):
        if "Node_info" in jsval["result"]["data"]:
            status["uptime"] = str(datetime.timedelta(seconds = jsval["result"]["data"]["Node_info"]["Metrics"]["uptime"]))
        if "timestamp" in jsval["result"]["data"]:
            status["timestamp"] = jsval["result"]["data"]["timestamp"]
        if "Software" in jsval["result"]["data"]:
            status["software"] = {}
            status["software"]["indy-node"] = jsval["result"]["data"]["Software"]["indy-node"]
            status["software"]["sovrin"] = jsval["result"]["data"]["Software"]["sovrin"]

    return status

async def get_package_info(jsval: any) -> any:
    packages = {}
    if jsval and ("REPLY" in jsval["op"]):
        if "Software" in jsval["result"]["data"]:
            for installed_package in jsval["result"]["data"]["Software"]["Installed_packages"]:
                package, version = installed_package.split()
                packages[package] = version

    return packages

async def check_package_versions(packages: any) -> any:
    warnings = {}
    for node, package_list in packages.items():
        mismatches = []
        for package, version in package_list.items():
            total = 0
            same = 0
            other_version = ""
            for comp_node, comp_package_list in packages.items():
                if package in comp_package_list:
                    total +=1
                    comp_version = comp_package_list[package]
                    if comp_version == version:
                        same +=1
                    else:
                        other_version = comp_version
            if (same/total) < .5:
                mismatches.append("Package mismatch: '{0}' has '{1}' {2}, while most other nodes have '{1}' {3}".format(node, package, version, other_version))
        if mismatches:
            warnings[node] = mismatches
    return warnings

async def merge_package_mismatch_info(result: any, packages: any):
    package_warnings = await check_package_versions(packages)
    if package_warnings:
        for node_name in package_warnings:
            entry_to_update = [t for t in result if t["name"] == node_name][0]
            if "warnings" in entry_to_update:
                for item in package_warnings[node_name]:
                    entry_to_update["warnings"].append(item)
            else:
                entry_to_update["warnings"] = package_warnings[node_name]
            entry_to_update["status"]["warnings"] = len(entry_to_update["warnings"])


async def get_info(jsval: any, ident: DidKey = None) -> any:
    info = []
    if "REPLY" in jsval["op"]:
        if ident:
            # Pending Upgrade
            if jsval["result"]["data"]["Extractions"]["upgrade_log"]:
                current_upgrade_status = jsval["result"]["data"]["Extractions"]["upgrade_log"][-1]
                if "succeeded" not in current_upgrade_status:
                    info.append("Pending Upgrade: {0}".format(current_upgrade_status.replace('\t', '  ').replace('\n', '')))

    return info

async def detect_issues(jsval: any, node: str, primary: str, ident: DidKey = None) -> Tuple[any, any]:
    errors = []
    warnings = []
    ledger_sync_status={}
    if "REPLY" in jsval["op"]:
        if ident:
            # Ledger Write Consensus Issues
            if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["0"]["Has_write_consensus"]:
                errors.append("Config Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["0"]["Has_write_consensus"]))
            if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["1"]["Has_write_consensus"]:
                errors.append("Main Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["1"]["Has_write_consensus"]))
            if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["2"]["Has_write_consensus"]:
                errors.append("Pool Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["2"]["Has_write_consensus"]))
            if "1001" in  jsval["result"]["data"]["Node_info"]["Freshness_status"]:
                if not jsval["result"]["data"]["Node_info"]["Freshness_status"]["1001"]["Has_write_consensus"]:
                    errors.append("Token Ledger Has_write_consensus: {0}".format(jsval["result"]["data"]["Node_info"]["Freshness_status"]["1001"]["Has_write_consensus"]))

            # Ledger Status
            for ledger, status in jsval["result"]["data"]["Node_info"]["Catchup_status"]["Ledger_statuses"].items():
                if status != "synced":
                    ledger_sync_status[ledger] = status
            if ledger_sync_status:
                ledger_status = {}
                ledger_status["ledger_status"] = ledger_sync_status
                ledger_status["ledger_status"]["transaction-count"] = jsval["result"]["data"]["Node_info"]["Metrics"]["transaction-count"]
                warnings.append(ledger_status)

            # Mode
            if jsval["result"]["data"]["Node_info"]["Mode"] != "participating":
                warnings.append("Mode: {0}".format(jsval["result"]["data"]["Node_info"]["Mode"]))

            # Primary Node Mismatch
            if jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"] != primary:
                warnings.append("Primary Mismatch! This Nodes Primary: {0} (Expected: {1})".format(jsval["result"]["data"]["Node_info"]["Replicas_status"][node+":0"]["Primary"], primary))

            # Unreachable Nodes
            if jsval["result"]["data"]["Pool_info"]["Unreachable_nodes_count"] > 0:
                unreachable_node_list = []
                unreachable_nodes = {"unreachable_nodes":{}}
                unreachable_nodes["unreachable_nodes"]["count"] = jsval["result"]["data"]["Pool_info"]["Unreachable_nodes_count"]
                for unreachable_node in jsval["result"]["data"]["Pool_info"]["Unreachable_nodes"]:
                    unreachable_node_list.append(unreachable_node[0])
                unreachable_nodes["unreachable_nodes"]["nodes"] = ', '.join(unreachable_node_list)
                warnings.append(unreachable_nodes)

            # Denylisted Nodes
            if len(jsval["result"]["data"]["Pool_info"]["Blacklisted_nodes"]) > 0:
                warnings.append("Denylisted Nodes: {1}".format(jsval["result"]["data"]["Pool_info"]["Blacklisted_nodes"]))
    else:
        if "reason" in jsval:
            errors.append(jsval["reason"])
        else:
            errors.append("unknown error")

    return errors, warnings


def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))


def download_genesis_file(url: str, target_local_path: str):
    log("Fetching genesis file ...")
    target_local_path = f"{get_script_dir()}/genesis.txn"
    urllib.request.urlretrieve(url, target_local_path)

def load_network_list():
    with open(f"{get_script_dir()}/networks.json") as json_file:
        networks = json.load(json_file)
    return networks

def list_networks():
    networks = load_network_list()
    return networks.keys()

def filter_timestamps(data):
    filtered=[]
    for l in data.splitlines():
        if re.match(r'^[0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-6][0-9]:[0-6][0-9],[0-9]+ .*',l):
            continue              
        filtered.append(l)
    return ''.join(filtered)

def flatten_dict(d,separator='.',parent_key=''):
    items=[]
    try:
        d_items = d.items()
    except AttributeError:
        i=0
        for e in d:
            new_key = '{}'.format(i)
            if isinstance(e,str):
                items.append((new_key,e))
            elif isinstance(e,float):
                items.append((new_key,e))
            elif isinstance(e,int):
                items.append((new_key,e))
            else:
                items.extend(
                    flatten_dict(e,separator=separator,parent_key=new_key).items()
                )
            i+=1
        return dict(items)
    for k, v in d_items:
        if parent_key:
            new_key = '{}{}{}'.format(parent_key,separator,k)
        else:
            new_key = k
        if isinstance(v,dict):
            items.extend(
                flatten_dict(v,separator=separator,parent_key=new_key).items()
            )
        elif isinstance(v,list):
            org_key=new_key
            i=0
            for e in v:
                new_key = '{}{}{}'.format(org_key,separator,i)
                if isinstance(e,str):
                    items.append((new_key,e))
                elif isinstance(e,float):#.split('{',1)[1]))
                    items.append((new_key,e))
                elif isinstance(e,int):
                    items.append((new_key,e))
                else:
                    items.extend(
                        flatten_dict(e,separator=separator,parent_key=new_key).items()
                    )
                i+=1
        else:
            items.append((new_key,v))
    return dict(items)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch the status of all the indy-nodes within a given pool.")
    parser.add_argument("--net", choices=list_networks(), help="Connect to a known network using an ID.")
    parser.add_argument("--list-nets", action="store_true", help="List known networks.")
    parser.add_argument("--genesis-url", default=os.environ.get('GENESIS_URL') , help="The url to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_URL' environment variable.")
    parser.add_argument("--genesis-path", default=os.getenv("GENESIS_PATH") or f"{get_script_dir()}/genesis.txn" , help="The path to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_PATH' environment variable.")
    parser.add_argument("-s", "--seed", default=os.environ.get('SEED') , help="The privileged DID seed to use for the ledger requests.  Can be specified using the 'SEED' environment variable.")
    parser.add_argument("-a", "--anonymous", action="store_true", help="Perform requests anonymously, without requiring privileged DID seed.")
    parser.add_argument("--status", action="store_true", help="Get status only.  Suppresses detailed results.")
    parser.add_argument("--alerts", action="store_true", help="Filter results based on alerts.  Only return data for nodes containing detected 'info', 'warnings', or 'errors'.")
    parser.add_argument("--nodes", help="The comma delimited list of the nodes from which to collect the status.  The default is all of the nodes in the pool.")
    parser.add_argument("-p", "--prometheus",action="store_true", help="Enable output in Prometheus format")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    verbose = args.verbose

    if args.prometheus:
        prometheus = True
#        print("Enabled Output in Prometheus format: "+ str(prometheus))

    if args.list_nets:
        print(json.dumps(load_network_list(), indent=2))
        exit()

    if args.net:
        log("Loading known network list ...")
        networks = load_network_list()
        if args.net in networks:
            log("Connecting to '{0}' ...".format(networks[args.net]["name"]))
            args.genesis_url = networks[args.net]["genesisUrl"]

    if args.genesis_url:
        download_genesis_file(args.genesis_url, args.genesis_path)
    if not os.path.exists(args.genesis_path):
        print("Set the GENESIS_URL or GENESIS_PATH environment variable or argument.\n", file=sys.stderr)
        parser.print_help()
        exit()

    did_seed = None if args.anonymous else args.seed
    if not did_seed and not args.anonymous:
        print("Set the SEED environment variable or argument, or specify the anonymous flag.\n", file=sys.stderr)
        parser.print_help()
        exit()

    log("indy-vdr version:", indy_vdr.version())
    if did_seed:
        ident = DidKey(did_seed)
        log("DID:", ident.did, " Verkey:", ident.verkey)
    else:
        ident = None

    asyncio.get_event_loop().run_until_complete(fetch_status(args.genesis_path, args.nodes, ident, args.status, args.alerts))
