# qcm
Qumulo Configuration Manager

Simple Script to read Qumulo Configuration Data for documentation or to import this to another Cluster

joka@jkantaMBP Desktop % python qcm.py --help
1.0.0
usage: qcm.py [-h] [--read | --write] --host HOST --password PASSWORD
              [--user USER] [--all] [--quotas] [--shares] [--exports]
              [--policies] [--source-relationships] [--users] [--roles]

Sync Shares and Exports

optional arguments:
  -h, --help            show this help message and exit
  --read                reads configuration data from Qumulo Cluster
  --write               writes configuration data to Qumulo Cluster
  --host HOST           Source / Target Hostname or IP
  --password PASSWORD   Password for login
  --user USER           User with aprobiate rights
  --all                 reads / writes all configuration
  --quotas              read / writes quotas configuration
  --shares              read / writes smb share configuration
  --exports             read / writes nfs export configuration
  --policies            read / writes policies configuration
  --source-relationships
                        read / writes replication configuration
  --users               read / writes user configuration
  --roles               read / writes RBAC configuration
joka@jkantaMBP Desktop %
