#!/usr/bin/env python
import sys
import json
import os
import glob
import subprocess


def is_disk(disk_range, path):
    if len(disk_range) == 1:
        return disk_range[0] <= path
    else:
        return disk_range[0] <= path and path >= disk_range[1]

def disks(disk_glob, disk_range):
    for path in glob.glob(disk_glob):
        if is_disk(disk_range, path):
            yield path


def format_arg(flag, items):
    items = filter(None, items)
    if items:
        return [flag, ",".join(items)]
    else:
        return []
                
data = json.load(open(sys.argv[1]))
services = data['services']

cmd = (
    [
        "/opt/mapr/server/configure.sh",
        "-u", "mapr",
        "-g", "mapr",
        "-N", data['clustername']
    ]
    + format_arg(
        "-Z", services.get('mapr-zookeeper', [])
    )
    + format_arg(
        "-C", services.get('mapr-cldb', [])
    )
    + format_arg(
        "-RM", services.get('mapr-resourcemanager', [])
    )
)

subprocess.check_call(cmd)

if not os.path.exists("/opt/mapr/conf/disks.txt"):
    with open("/opt/mapr/conf/disks.txt.tmp", "w") as fh:
        for path in disks(data['disk_glob'], data['disk_range']):
            fh.write("{path}\n".format(path=path))
    os.rename("/opt/mapr/conf/disks.txt.tmp", "/opt/mapr/conf/disks.txt")
    subprocess.check_call(["/opt/mapr/server/disksetup", "-F", "/opt/mapr/conf/disks.txt"])

subprocess.check_call(["service", "mapr-warden", "restart"])
