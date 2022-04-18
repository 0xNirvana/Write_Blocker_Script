#Python3
import subprocess

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

if __name__ == "__main__":
    service_ops("stop", "colord")