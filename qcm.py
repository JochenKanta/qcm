#!/usr/bin/env python
# coding: utf-8

#import python libraries
import re
import json
import os
import sys
from datetime import date
from qumulo.rest_client import RestClient
import argparse


class QumuloConfigManager():

    def __init__(self, hostname, user, password):
        self.hostname = hostname
        self.user = user
        self.password = password
        self.rc = RestClient(self.hostname, 8000)
        self.rc.login(self.user, self.password)
        self.date = date.today();


    def set_url(self, data_type, area=None, version=1, multiple=True):
        self.data_type = data_type
        self.multiple = multiple
        if area:
            self.data_full_name = "%s-%s" % (area, data_type)
            self.base_url = "/v%s/%s/%s%s" % (version, area, data_type, '/' if multiple else '')
        else:
            self.data_full_name = "%s" % (data_type, )
            self.base_url = "/v%s/%s/" % (version, data_type)
        self.file_name = "qumulo-%s-%s-%s.json" % (self.date, self.hostname, self.data_full_name)

    def export_settings(self):
        print("\n--------------- export %10s settings  ---------------" % self.data_type)
        more_data = True
        url = "%s%s" % (self.base_url, '?limit=1000' if self.multiple else '')
        objects = []
        while url:
            d = self.rc.request("GET", url)
            if self.multiple == False or "roles" in url:
                objects = d
                url = None

            elif self.data_type == "quotas" or self.data_type == "policies":
                if 'entries' in d:
                    for obj in d['entries']:
                        objects.append(obj)
                else:
                    for obj in d[self.data_type]:
                        objects.append(obj)
                # handle pagination
                if 'paging' in d and d['paging']['next']:
                    url = d['paging']['next']
                else:
                    url = None
            elif type(d) is list:
                for obj in d:
                    objects.append(obj)
                url = None
        print("Saving %s %s objects to file %s" % (len(objects) if self.multiple else 1, self.data_full_name, self.file_name))
        fw = open(self.file_name, "w")
        fw.write(json.dumps(objects, indent=2))
        fw.close()

    def load_settings(self):
        print("\n--------------- load %10s settings  ---------------" % self.data_type)
        if not os.path.exists(self.file_name):
            print("Settings file does not exist: %s" % self.file_name)
            return
        objects = json.loads(open(self.file_name, "r").read())
        print("Found %s %s objects to load onto Qumulo cluster %s." % (
                                len(objects), self.data_full_name, self.hostname))
        object_success_count = 0
        for obj in objects:
            try:
                if self.data_type == "policies":
                    del obj['id']
                    for sched in obj['schedules']:
                        del sched['id']
                self.rc.request("POST", self.base_url, obj)
                object_success_count += 1
            except Exception, e:
                print("failed to create %s - %s" % (self.data_type, e))

        print("Created %s %s objects Qumulo cluster %s." % (
                                object_success_count, self.data_full_name, self.hostname))


def main(argv):
    parser = argparse.ArgumentParser(
        description="Sync Shares and Exports "
        )
    base_mode = parser.add_mutually_exclusive_group()

    base_mode.add_argument('--read', action="store_true", help="reads configuration data from Qumulo Cluster")
    base_mode.add_argument('--write', action="store_true", help="writes configuration data to Qumulo Cluster")
    parser.add_argument('--host', dest='host', required=True, type=str, help="Source / Target Hostname or IP")
    parser.add_argument('--password', required=True, type=str, help="Password for login")
    parser.add_argument('--user', dest='user', default="admin", type=str, help="User with aprobiate rights")
    parser.add_argument('--all', dest='all', action="store_true", help="reads / writes all configuration")
    parser.add_argument('--quotas', action="store_true", help="read / writes quotas configuration")
    parser.add_argument('--shares', action="store_true", help="read / writes smb share configuration")
    parser.add_argument('--exports', action="store_true", help="read / writes nfs export configuration")
    parser.add_argument('--policies', action="store_true", help="read / writes policies configuration")
    parser.add_argument('--source-relationships', dest='src_rel', action="store_true", help="read / writes replication configuration")
    parser.add_argument('--users', action="store_true", help="read / writes user configuration")
    parser.add_argument('--roles', action="store_true", help="read / writes RBAC  configuration")
    opts = parser.parse_args()
    qcm = QumuloConfigManager(opts.host, opts.user, opts.password)

    if opts.read:
        if opts.all or opts.quotas:
            qcm.set_url("quotas", area="files")
            qcm.export_settings()
        if opts.all or opts.shares:
            qcm.set_url("shares", area="smb", version=2)
            qcm.export_settings()
        if opts.all or opts.exports:
            qcm.set_url("exports", area="nfs", version=2)
            qcm.export_settings()
        if opts.all or opts.policies:
            qcm.set_url("policies", area="snapshots")
            qcm.export_settings()
        if opts.all or opts.policies:
            qcm.set_url("source-relationships", area="replication")
            qcm.export_settings()
        if opts.all or opts.users:
            qcm.set_url("users")
            qcm.export_settings()
        if opts.all or opts.roles:
            qcm.set_url("roles", area="auth")
            qcm.export_settings()

    if opts.write:
        if opts.all or opts.quotas:
            qcm.set_url("quotas", area="files")
            qcm.load_settings()
        if opts.all or opts.shares:
            qcm.set_url("shares", area="smb", version=2)
            qcm.load_settings()
        if opts.all or opts.exports:
            qcm.set_url("exports", area="nfs", version=2)
            qcm.load_settings()
        if opts.all or opts.policies:
            qcm.set_url("policies", area="snapshots")
            qcm.load_settings()
        if opts.all or opts.src_rel:
            qcm.set_url("source-relationships", area="replication")
            qcm.load_settings()




# Main
version = "1.0.0"
if __name__ == '__main__':
    print(version)
    main(sys.argv[1:])
