"""
Simple python script to confirm if a given path is read-only
"""

from sys import argv

def open_file(path):
    if not path.strip().endswith('/'):
        path = path.strip() + '/'
    try:
        o = open(path + 'ro_test.txt', 'w')
    except Exception as e:
        print(e)
        if (e.errno == 30):
            print(f"\"{path}\" is Read-Only.\n")
    else:
        print(f"\"{path}\" is not Read-Only.\n")

if __name__ == "__main__":
    if (len(argv) < 2):
        print("Usage: python3 test_readonly.py <path>\n")
        exit()

    open_file(argv[1])