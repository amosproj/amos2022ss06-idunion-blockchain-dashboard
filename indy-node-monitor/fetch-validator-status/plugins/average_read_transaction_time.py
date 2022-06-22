import os

import plugin_collection
import json
import argparse

class main(plugin_collection.Plugin):

    prometheus = False

    def __init__(self):
        super().__init__()
        self.index = 4
        self.name = 'Compute average read transaction time of all node'
        self.description = ''
        self.type = ''

    def parse_args(self, parser):
        parser.add_argument("--avgread", action="store_true",
                            help="Average read transaction time of all node")

    def load_parse_args(self, args):
        global verbose
        verbose = args.verbose

        self.enabled = args.avgread

    async def perform_operation(self, result, network_name, response, verifiers):
        sum = 0
        count = 0

        for node in result:
            if "response" in node:
                response = node["response"]
                result_data = response["result"]
                data = result_data["data"]
                node_info = data["Node_info"]
                metrics = node_info["Metrics"]
                average_per_second = metrics["average-per-second"]
                read_transactions = average_per_second["read-transactions"]
                # read_transactions = node["response"]["result"]["data"]["Node_info"]["Metrics"]["average-per-second"]["read-transactions"]
                sum += read_transactions
                count += 1

        average = sum / count

        # for node in result:
        #     if "response" in node:
        #         node["response"]["result"]["data"]["Node_info"]["Metrics"]["average-read-transaction-time"] = average

        # all_node_info = {
        #     "name": "All-node-info",
        #     "response" : {
        #         "average-read-transaction-time" : str(average)
        #     }
        # }

        # all_node_info = {
        #     "name": "All-node-info",
        #     "response": {
        #         "op" : "REPLY",
        #         "result": {
        #             "data": {
        #                 "Node_info": {
        #                     "Name" : "All-node-info",
        #                     "Metrics": {
        #                         "average-read-transaction-time": str(average)
        #                     }
        #                 }
        #             }
        #         }
        #     }
        # }

        # parser2 = argparse.ArgumentParser()
        # options = parser2.parse_args()
        #cur_path = os.path.dirname(__file__)
        #new_path = os.path.relpath('..//plugin//global_var_p.txt', cur_path)
        f = open("global_var_p.txt", "r")
        p = f.read()
        if "True" in p:
            all_node_info = "indy_read_transaction_time_all_node{node_name=\"All_node_info\",source=\"indy_node\"} " + str(average)
            file = open("global_var_p.txt", "w")
            file.write(all_node_info)
        else:
            all_node_info = {
                "name": "All-node-info",
                "response": {
                    "op" : "REPLY",
                    "result": {
                        "data": {
                            "Node_info": {
                                "Name" : "All-node-info",
                                "Metrics": {
                                    "average-read-transaction-time": str(average)
                                }
                            }
                        }
                    }
                }
            }
            result.append(all_node_info)

        return result
