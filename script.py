#Python3
import subprocess
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
    command = ["systemctl"]
    command.append(action)
    command.append(service_name)

    try:
        subprocess.check_output(command)
    except subprocess.CalledProcessError as cpe:
        if (cpe.returncode == 5):
            print(f"ERROR: Service name {service_name} does not exist!\n")
        elif (cpe.returncode == 4):
            print(f"ERROR: Execute script with sudo privileges!\n")
    else:
        print(f"{action} command on {service_name} completed!\n")

def implementPatch():
    try:
        shutil.copy(FORENSIC_READ_ONLY_FILE, RULES_DST_PATH)
    except Exception as e:
        print(e)
        sys.exit()

    try:
        files = os.listdir(TOOLS_DIRECTORY)
        if os.path.exists(TOOLS_DST_PATH):
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

    patchCheck = input("Have you implemented the kernel patch? Enter y/n:")
    if patchCheck == "y" or patchCheck == "yes" or patchCheck == "Y":
        patchResult = implementPatch()
        
    service_ops("stop", "colord")