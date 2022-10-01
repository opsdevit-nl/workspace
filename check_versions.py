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


  subprocess.run("apk update", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  for package in packages[kind]:
    package_name = package.split()[1]

    package_current = package.split()[2]
    if kind == "apk":
      package_latest = subprocess.run("apk -q info " + package_name + " | head -n1 | awk '{print $1}' | sed -r 's/^" + package_name + "-(.*)/\\1/g'", shell=True, capture_output=True, text=True).stdout.strip()
    
    print(package_current)
    print(package_latest)
    if package_current == package_latest:
      print("matched\n")
    
    ### TODO
    ### als geen match dan latest pushen naar nieuwe version file, container builden en tests draaien