import argparse
from client import run_client


def _argparse():
    parser = argparse.ArgumentParser(description="Get node")
    parser.add_argument('--node', dest='node')
    args = parser.parse_args()
    return args.node


node = _argparse()
run_client(node)
