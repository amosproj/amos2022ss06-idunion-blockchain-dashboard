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
prometheus = False
label = "indy_node"

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
    file = open("global_var_p.txt", "r")
    print(file.read())
    file = open("global_var_p.txt", "w")
    file.write("")

def process_data_prometheus_1_5(data):
    node_info = data['Node_info']
    node_name = node_info['Name']
    metrics = node_info['Metrics']
    pool_metrics = data['Pool_info']
    version_metrics = data['Software']
    hardware_metrics = data['Hardware']

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
    print('indy_os_version{{version="{version}",node_name="{node_name}",source="{label}"}} {value}'.format(
        version=version_metrics['OS_version'],
        node_name=node_name,
        label=label,
        value=0
    )
    )

    #Print node hardware metric
    print('indy_node_hdd_used{{node_name="{node_name}",source="{label}"}} {value}'.format(
        node_name=node_name,
        label=label,
        value=hardware_metrics['HDD_used_by_node'].split()[0]
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
    file_name = sys.argv[1]
    f = open(file_name)
    data = f.read()
    output_prometheus(data)
