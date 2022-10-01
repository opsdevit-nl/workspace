#!/usr/bin/python3

import sys
import subprocess

with open(sys.argv[1]) as versionfile:
  lines = [line.rstrip() for line in versionfile]

# print(lines)

kind = sys.argv[2]

def get_packages(kind):
  versions = []

  for line in lines:
    if line.startswith(kind):
      versions.append(line)

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
        package_latest = subprocess.run("curl -s https://api.github.com/repos/" + package_name + " | jq -r .[].tag_name | grep kustomize | sort -Vr | sed -r 's/^kustomize\\/(.*)/\\1/g' | head -n 1", shell=True, capture_output=True, text=True).stdout.strip()
      if "sealed-secrets" in package_name:
        package_latest = subprocess.run("curl -s https://api.github.com/repos/" + package_name + " | jq -r .[].tag_name | grep ^v | sort -rV | head -n 1", shell=True, capture_output=True, text=True).stdout.strip()
      else:
        print("add config for new package")

    print(package_current)
    print(package_latest)
    if package_current == package_latest:
      print("matched\n")
    else:
      print("upgrade me\n")
    
    ### TODO
    ### als geen match dan latest pushen naar nieuwe version file, container builden en tests draaien