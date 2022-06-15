import plugin_collection
import json


class main(plugin_collection.Plugin):

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

        for node in result:
            if "response" in node:
                node["response"]["result"]["data"]["Node_info"]["Metrics"]["average-read-transaction-time"] = average

        return result
