from beet import Context, LootTable, PackConfig, PackLoadOptions, ProjectConfig, run_beet
from beet.toolchain.cli import error_handler
import argparse
 
 
# Initialize parser
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-o", "--output", help = "Folder to output too", default='.')
parser.add_argument("-i", "--input", help = "Input datapack folder", required=True)

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