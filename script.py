#Python3
from subprocess import *
import os
import sys
import shutil

FORENSIC_READ_ONLY_FILE = "./udev/01-forensic-readonly.rules"
TOOLS_DIRECTORY = "./tools"

RULES_DST_PATH = "/etc/udev/rules.d"
TOOLS_DST_PATH = "/usr/sbin/tools"

"""
Module to perform actions on a given service using systemctl
Usage: service_ops(<Action(Eg: "start", "stop")>, <Service Name>)
"""
def service_ops(action, service_name):
    base = ["systemctl"]
    implementCommand = base + [action, service_name]
    # implementCommand = implementCommand.append(action)
    # implementCommand = implementCommand.append(service_name)
    
    try:
        check_output(implementCommand)
    except CalledProcessError as cpe:
        if (cpe.returncode == 5):
            print(f"ERROR: Service name {service_name} does not exist!\n")
        elif (cpe.returncode == 4):
            print(f"ERROR: Execute script with sudo privileges!\n")
    else:
        statusCheckCommand = base + ["status"]
        statusCheckCommand = statusCheckCommand + [service_name]
        proc = Popen(statusCheckCommand, stdout=PIPE, stderr=PIPE)
        serviceStatus = proc.communicate()[0].decode("utf-8")
        # print(serviceStatus)
        if action == "stop":
            stopCheck(service_name, serviceStatus)
        if action == "start":
            startCheck(service_name, serviceStatus)

def startCheck(service_name, serviceStatus):
    if "Active: active" in serviceStatus:
        print("Service %s started." % (service_name))
    else:
        print("Unable to start %s service." % service_name)     

def stopCheck(service_name, serviceStatus):
    if "Active: inactive" in serviceStatus:
        print("Service %s stopped." % (service_name))
    else:
        print("Unable to stop %s service." % service_name)
        
def implementPatch():
    try:
        shutil.copy(FORENSIC_READ_ONLY_FILE, RULES_DST_PATH)
    except Exception as e:
        print(e)
        sys.exit()

    try:
        files = os.listdir(TOOLS_DIRECTORY)
        if not os.path.exists(TOOLS_DST_PATH):
            os.mkdir(TOOLS_DST_PATH)
        for f in files:
            shutil.copy2(os.path.join(TOOLS_DIRECTORY,f), TOOLS_DST_PATH)
        
    except Exception as e:
        print (e)
        sys.exit()

if __name__ == "__main__":
    print("### Write Blocker Script ###")
    print("P.S. Run this script only on Linux Machines")

    if not os.geteuid() == 0:
        print("Run this script with sudo.")
        sys.exit()

    while True:
        patchCheck = input("Have you implemented the kernel patch? Enter y/n:")
        if patchCheck == "n" or patchCheck == "no" or patchCheck == "N":
            implementPatch()
            break
        elif patchCheck == "y" or patchCheck == "yes" or patchCheck == "Y":
            print("Awesome!")
            break
        else:
            continue
    
    
    service_ops("stop", "udisks2.service")
    # service_ops("stop", "colord")