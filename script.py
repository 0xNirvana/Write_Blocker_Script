#Python3
from subprocess import *
import os
import sys
import shutil
import re
import concurrent.futures

FORENSIC_READ_ONLY_FILE = "./udev/01-forensic-readonly.rules"
TOOLS_DIRECTORY = "./tools"

RULES_DST_PATH = "/etc/udev/rules.d"
TOOLS_DST_PATH = "/usr/sbin"

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
            print(f"ERROR: Service name {service_name} does not exist!")
        elif (cpe.returncode == 4):
            print(f"ERROR: Execute script with sudo privileges!")
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

def deviceDetection():
    proc = Popen("blkid", stdout=PIPE, shell=True)
    beforeInsertion = proc.communicate()[0].decode('utf-8')
    count = 1
    devices = []
    # devices = {}
    input("Insert your device now.\nPress any key after insertion.")
    proc = Popen("blkid", stdout=PIPE, shell=True)
    afterInsertion = proc.communicate()[0].decode('utf-8')

    beforeInsertion = beforeInsertion.splitlines()
    afterInsertion = afterInsertion.splitlines()
    
    for line in afterInsertion:
        if line not in beforeInsertion:
            if "LABEL" in line:
                path = re.findall('(.*?)\:', line)[0]
                label = re.findall('LABEL=\"(.*?)\"', line)[0]
                devices.append([path, label])
            else:
                path = re.findall('(.*?)\:', line)[0]
                # label = "NO LABEL"
                devices.append([path, "No Label"])

            if path:
                # devices.append(label)
                print("{}: {} -> {}".format(count, path, label))
                count += 1
    
    if len(devices) == 0:
        print ("""
        No new device detected!
        Please follow the steps mentioned below:
        1. Remove the evidence device
        2. Start the script again
        3. Reinsert the evidence device only afteer prompted""")
    else:
        confirmation = input("Enter the index number of your device.")
        confirmation = int(confirmation)
        if confirmation <= count:
            return devices[confirmation-1]
        else:
            return False
    

    # for line in beforeInsertion:
    #     if "LABEL" in line:
    #         label = re.findall('LABEL=\"(.*?)\"', line)
    #     else:
    #         label = re.findall('(.*?)\:', line)
        
    #     if label:
    #         devices.append(label[0])
    #         print("{}: {}".format(count, label[0]))
    #         count += 1
        
    # confirmation = input("Enter the number of your device:\nIf your device is not listed then enter any other key and reinsert your device after starting the script.")
    # confirmation = int(confirmation)
    # if confirmation <= count:
    #     return devices[confirmation-1]
    # else:
    #     return False

def deviceBlock(path):
    print("Enabling read only for block: {} ".format(path), end="")
    try:
        run(["blockdev", "--setro", path])
        print("--> Enabled!")
        return True  
    except Exception as e:
        print ("\n", e)
        sys.exit()

def deviceMount(path):
    print("Mounting the device at {} to /mnt/evidence ".format(path), end="")
    try:
        if not os.path.exists("/mnt/evidence"):
            os.makedirs("/mnt/evidence")

        run(["mount", "-o", "ro", path, "/mnt/evidence"])
        print("--> Mounted!")
        return True
    except Exception as e:
        print ("\n", e)
        sys.exit()

def deviceImageCreation(path, name):
    print("Creating image for {}".format(path))
    print("Image will be stored at: ./{}.dd".format(name))
    try:
        run(["dd", "if={}".format(path), "of=./{}.dd".format(name), "conv=noerror,sync", "status=progress"])
        print("Image created and stored at: ./{}.dd".format(name))
        return True
    except Exception as e:
        print ("\n", e)
        sys.exit()

def hashCalc(path):
    print("Generating Hash for {}".format(path))
    proc = Popen(["md5sum", path], stdout=PIPE, stderr=PIPE)
    serviceStatus = proc.communicate()[0].decode("utf-8")
    serviceStatus = serviceStatus.split()
    return serviceStatus[0]

def hashMatch(path, name):
    paths = [path, "./{}.dd".format(name)]
    hashes = []
    print ("Hashes will be tested for\n1. {}\n2. {}".format(path, name))
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for p in paths:
            futures.append(executor.submit(hashCalc, p))
        
        for future in concurrent.futures.as_completed(futures):
            hashes.append(future.result())

    if hashes[0] == hashes[1]:
        print("Hash is: {}".format(hashes[0]))
        return True
    else:
        print("Hash Mismatch!\n{} -> {}\n{}.dd -> {}".format(path, hashes[0], name, hashes[1]))
        return False

def deviceUnmount(path):
    print("Unmounting device {} from /mnt/evidence.".format(path), end="")
    try:
        run(["umount", "/mnt/evidence"])
        print("--> Unmounted")
        return True
    except Exception as e:
        print("\n", e)
        sys.exit()

def deviceUnplug(path):
    input("Remove the device and press any key to continue.")
    proc = Popen("blkid", stdout=PIPE, shell=True)
    devices = proc.communicate()[0].decode('utf-8')
    if path not in devices:
        return True
    else:
        return False

if __name__ == "__main__":
    if not os.geteuid() == 0:
        print("Run this script with sudo.")
        sys.exit()

    print("### Write Blocker Script ###")
    print("P.S. Run this script only on Linux Machines")
    print("Do not insert the evidence device until instructed to do so!")
    print("If already inserted then remove it!")
    input("Press enter key when you are ready!")
    print("\n", end="")

    service_ops("stop", "udisks2.service")
    print("\n", end="")

    deviceDetected = deviceDetection()
    if deviceDetected:
        print ("You have selected {} as your target device.\n".format(deviceDetected[1]))
    else:
        print("Exiting!\n")
        sys.exit()
    
    blockBlockStatus = deviceBlock(deviceDetected[0])
    if not blockBlockStatus:
        print("Issue with Blocking {}".format(deviceDetected[0]))
        sys.exit()
    print("\n", end="")

    deviceMountStatus = deviceMount(deviceDetected[0])
    if not deviceMountStatus:
        print("Issue with Mounting {}".format(deviceDetected[0]))
        sys.exit()
    print("\n", end="")

    createImage = input("Do you want to create an image? y/n: ")
    if createImage == "y" or createImage == "yes" or createImage == "Y":

        deviceImageCreationStatus = deviceImageCreation(deviceDetected[0], deviceDetected[1])
        if not deviceImageCreationStatus:
            print("Issue with Image Creation for {}".format(deviceDetected[0]))
            sys.exit()
        print("\n", end="")

        hashMatchResult = hashMatch(deviceDetected[0], deviceDetected[1])
        if hashMatchResult:
            print("Hashes matched!")
        else:
            print("Hashes do not match!")
        print("\n", end="")

    else:
        print("Image creation and hash calculation skipped!")
        input("Press any key when you want to unmount the device and enable automounting.")
    print("\n", end="")

    deviceUnmountStatus = deviceUnmount(deviceDetected[0])
    if not deviceUnmountStatus:
        print("Device Unmount Failed!")
        sys.exit()
    print("\n", end="")

    deviceUnplugStatus = deviceUnplug(deviceDetected[0]) 
    if deviceUnplugStatus:
        print("Device Removed Successfully!")
    else:
        print("Issue with device removal!")
        sys.exit()
    print("\n", end="")

    service_ops("start", "udisks2.service")

'''
REFERENCES
1. https://www.reddit.com/r/learnpython/comments/4ijwob/python_code_to_detect_connected_devices/
2. https://github.com/msuhanov/Linux-write-blocker
3. https://linuxhint.com/list-usb-devices-linux/

'''