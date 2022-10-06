#!/usr/bin/python3

import sys
import subprocess
import os

with open(sys.argv[1]) as versionfile:
  lines = [line.rstrip() for line in versionfile]

# print(lines)

kind = sys.argv[2]

def get_packages(kind):
  versions = []

  for line in lines:
    if line.startswith(kind):
      versions.append(line)
  # print("versions", versions)
  return versions

if __name__ == "__main__":
  packages = {}
  packages[kind] = (get_packages(kind))

  if kind == "apk":
    subprocess.run("apk update", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  
  for package in packages[kind]:
    package_name = package.split()[1]
    # print(package_name)

    package_current = package.split()[2]
    
    if kind == "apk":
      package_latest = subprocess.run("apk -q info " + package_name + " | head -n1 | awk '{print $1}' | sed -r 's/^" + package_name + "-(.*)/\\1/g'", shell=True, capture_output=True, text=True).stdout.strip()

    if kind == "container":
      if "alpine" in package_name:
        package_latest = subprocess.run("skopeo list-tags docker://" + package_name + " | jq -r \".Tags[]\" | sort -Vr | grep -v '^[a-z]' | grep \"\\.\" | head -n 1", shell=True, capture_output=True, text=True).stdout.strip()
      else:
        print("add config for new package")

    if kind == "pip":
      package_latest = subprocess.run("yolk -M" + package_name + " -f version", shell=True, capture_output=True, text=True).stdout.strip()

    if kind == "github":
      if "kustomize" in package_name:
        # print("echoo")
        package_latest = subprocess.run("curl -s \"https://api.github.com/repos/" + package_name + "\"" + " | jq -r .[].tag_name | grep kustomize | sort -Vr | sed -r 's/^kustomize\\/(.*)/\\1/g' | head -n 1", shell=True, capture_output=True, text=True).stdout.strip()
      elif "sealed-secrets" in package_name:
        package_latest = subprocess.run("curl -s \"https://api.github.com/repos/" + package_name + "\"" + " | jq -r .[].tag_name | grep ^v | sort -rV | head -n 1", shell=True, capture_output=True, text=True).stdout.strip()
      else:
        print("add config for new package")
    
    if kind == "oc":
      package_latest = subprocess.run("curl -s  \"https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/\" | grep openshift-client.*linux.*tar.gz | head -n 1 | sed -r 's/^.*openshift-client-linux-(.*)\\.tar\\.gz.*/\\1/g'", shell=True, capture_output=True, text=True).stdout.strip()

    if kind == "ansible-role":
      package_latest = subprocess.run("curl -s \"https://api.github.com/repos/" + package_name + "\"" + " | jq -r .[].name | sort -Vr | head -n 1", shell=True, capture_output=True, text=True).stdout.strip()

    if kind == "ansible-collection":
      package_latest = subprocess.run("ansible-galaxy collection list" + package_name + "--format json | jq -r \".[] | .[].version\" | head -n 1", shell=True, capture_output=True, text=True).stdout.strip()

    print("package name   : ", package_name)
    print("current version: ", package_current)
    print("latest version : ", package_latest)

    if package_current == package_latest:
      print("matched\n")
      with open('versions_run.ini', 'a') as versionfile:
        versionfile.write(kind + " " + package_name + " " + package_current + "\n")  
    elif package_latest == "":
      print("error occurred\n")
      with open('versions_run.ini', 'a') as versionfile:
        versionfile.write(kind + " " + package_name + " " + package_current + "\n")  
    else:
      print("upgrade me\n")
      with open('versions_run.ini', 'a') as versionfile:
        versionfile.write(kind + " " + package_name + " " + package_latest + "\n")  
    
    ### TODO
    ### pipeline werk:
    ### versies in files/Containerfile aanpassen op basis van gegenereerde versions_run.ini, nieuwe container builden en tests draaien