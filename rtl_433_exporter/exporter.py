import argparse
import json
import http.server
import logging
import sys
import threading
import datetime
import time

import prometheus_client

import rtl_433_exporter


def log():
    return logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser("rtl_433 prometheus exporter")

    parser.add_argument("--port", type=int, default=9433)
    parser.add_argument("--bind_address", default="0.0.0.0")
    parser.add_argument("--label", action="append")
    parser.add_argument("--persist", type=int, default=60)
    parser.add_argument("--verbose", "-v", action="count", default=0)

    args = parser.parse_args()

    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(stream=sys.stdout, level=level)

    collector = rtl_433_exporter.RTL433Collector(
        persist=args.persist, labels=args.label)

    prometheus_client.REGISTRY.register(collector)

    handler = prometheus_client.MetricsHandler.factory(
            prometheus_client.REGISTRY)
    server = http.server.HTTPServer(
            (args.bind_address, args.port), handler)
    threading.Thread(name="http-server", target=server.serve_forever).start()

    try:
        for line in sys.stdin:
            sys.stdout.write(line)
            event = json.loads(line)
            event["time"] = time.time()
            collector.add_event(event)
    finally:
        server.shutdown()
