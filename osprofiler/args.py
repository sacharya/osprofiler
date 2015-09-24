import argparse

prog = "profile.py"
description = "Openstack Profiling tool. BYOP (Bring your own probes)"
parser = argparse.ArgumentParser(description=description, prog=prog)

# Configuration file argument. Defaults to /etc/osprofiler/osprofiler.conf"
parser.add_argument(
    '-c', '--config', help="Configuration File",
    type=str, default="/etc/osprofiler/osprofiler.conf"
)


def get_args():
    """
    Returns args object.

    """
    return parser.parse_args()
