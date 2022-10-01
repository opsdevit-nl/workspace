#!/bin/bash

shopt -s expand_aliases
alias ws-container='podman run --rm -v ~/Projects/Ansible:/ansible:Z -v ~/.kube/config:/ansible/.kube/config:Z -e ANSIBLE_VAULT_PASSWORD=${ANSIBLE_VAULT_PASSWORD} --entrypoint='\'''\'' workspace-container'

rm versions_run.ini
for i in `grep -v "^\[" versions.ini | grep -v "^$" | awk '{print $1}' | sort -u`; do ws-container python3 check_versions.py versions.ini $i; done
diff <(grep -v "^\[" versions.ini | grep -v "^$"  | sort) <(cat versions_run.ini | sort) 2>&1 > /dev/null
if [ "$?" -ne 0 ] ; then echo "new versions available"; fi
