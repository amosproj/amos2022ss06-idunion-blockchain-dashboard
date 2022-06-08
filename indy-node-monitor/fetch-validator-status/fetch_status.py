#!/usr/bin/env python3
import argparse
import asyncio
# import base58
# import base64
import json
import os
import sys
import datetime
import urllib.request
from typing import Tuple
import re
import nacl.signing
import time
import indy_vdr
from indy_vdr.ledger import (
    build_get_validator_info_request,
    build_get_txn_request,
    # Request,
)
from indy_vdr.pool import open_pool
from plugin_collection import PluginCollection
# import time
from DidKey import DidKey
from plugins import analysis
verbose = False
prometheus = True
label = "indy_node"

def log(*args):
    if verbose:
        print(*args, "\n", file=sys.stderr)


async def fetch_status(genesis_path: str, nodes: str = None, ident: DidKey = None, network_name: str = None):
    # Start Of Engine
    attempt = 3
    while attempt:
        try:
            pool = await open_pool(transactions_path=genesis_path)
        except:
            log("Pool Timed Out! Trying again...")
            if not attempt:
                print("Unable to get pool Response! 3 attempts where made. Exiting...")
                exit()
            attempt -= 1
            continue
        break

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
    # End Of Engine

    result = await monitor_plugins.apply_all_plugins_on_value(result, network_name, response, verifiers)
    data = json.dumps(result, indent=2)
    if (prometheus == False):
        print(data)
    else:
        output_prometheus(str(data))

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


def output_prometheus(data_json):
    all_node_data = json.loads(filter_timestamps(data_json.replace("\r\n", "")))

    all_node_data_size = len(data_json)

    #  all_node_data = json.loads(filter_timestamps(str(data_json).replace("\r\n","")))

    for node in all_node_data:
        #        print(node["name"])
        if ('response' not in node):
            # Do some sort of metric stating "node not responding"?
            continue
        if (node['response']['op'] != "REPLY"):  # Skip nodes that dont  respond with REPLY
            sys.stderr.write("Error: Node \"" + node['name'] + "\" responded with " + node['response']['op'])
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

        print('indy_node_validator_info_size{source="indy-node"} ', all_node_data_size)

        for v in [node_ver, '.'.join(node_ver.split('.')[:-1]), 'latest']:
            try:
                process_data_prometheus_1_5(data)
                break
            except KeyError:
                pass

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
    monitor_plugins = PluginCollection('plugins')

    parser = argparse.ArgumentParser(description="Fetch the status of all the indy-nodes within a given pool.")
    parser.add_argument("--net", choices=list_networks(), help="Connect to a known network using an ID.")
    parser.add_argument("--list-nets", action="store_true", help="List known networks.")
    parser.add_argument("--genesis-url", default=os.environ.get('GENESIS_URL') , help="The url to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_URL' environment variable.")
    parser.add_argument("--genesis-path", default=os.getenv("GENESIS_PATH") or f"{get_script_dir()}/genesis.txn" , help="The path to the genesis file describing the ledger pool.  Can be specified using the 'GENESIS_PATH' environment variable.")
    parser.add_argument("-s", "--seed", default=os.environ.get('SEED') , help="The privileged DID seed to use for the ledger requests.  Can be specified using the 'SEED' environment variable. If DID seed is not given the request will run anonymously.")
    parser.add_argument("--nodes", help="The comma delimited list of the nodes from which to collect the status.  The default is all of the nodes in the pool.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("-p", "--prometheus", action="store_true", help="Enable output in Prometheus format")

    monitor_plugins.get_parse_args(parser)
    args, unknown = parser.parse_known_args()

    verbose = args.verbose

    monitor_plugins.load_all_parse_args(args)

    if args.list_nets:
        print(json.dumps(load_network_list(), indent=2))
        exit()

    network_name = None 
    if args.net:
        log("Loading known network list ...")
        networks = load_network_list()
        if args.net in networks:
            log("Connecting to '{0}' ...".format(networks[args.net]["name"]))
            args.genesis_url = networks[args.net]["genesisUrl"]
            network_name = networks[args.net]["name"]

    if args.genesis_url:
        download_genesis_file(args.genesis_url, args.genesis_path)
        if not network_name: 
            network_name = args.genesis_url
    if not os.path.exists(args.genesis_path):
        print("Set the GENESIS_URL or GENESIS_PATH environment variable or argument.\n", file=sys.stderr)
        parser.print_help()
        exit()

    did_seed = None if not args.seed else args.seed

    log("indy-vdr version:", indy_vdr.version())
    if did_seed:
        ident = DidKey(did_seed)
        log("DID:", ident.did, " Verkey:", ident.verkey)
    else:
        ident = None

    asyncio.get_event_loop().run_until_complete(fetch_status(args.genesis_path, args.nodes, ident, network_name))

