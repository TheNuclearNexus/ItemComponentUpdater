import os
from beet import run_beet

import argparse

from mecha import Mecha

from updater.token import TokenReducer
 
 
# Initialize parser
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-o", "--output", help = "Folder to output too", default='.')
parser.add_argument("-i", "--input", help = "Input datapack folder", required=True)

def format_path(input: str, path: str):
    if path == 'None':
        return ""
    
    path = path.replace(os.path.join(os.getcwd(), input), '')

    parts = path.split(os.path.sep)
    parts[-1] = ".".join(parts[-1].split(".")[0:-1])
    return parts[2] + ":" + "/".join(parts[4:])

def main():    
    args = parser.parse_args()
    output: str = args.output
    input: str = args.input

    config = {
        "data_pack": {
            "name": "datapack",
            "load": input,
        },
        "pipeline": [
            "updater.plugin"
        ],
        "output": output
    }
    print("Starting")
    with run_beet(config) as ctx:
        pass
    print("Done")

if __name__ == "__main__":
    main()