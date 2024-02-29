from beet import Context, LootTable, PackConfig, PackLoadOptions, ProjectConfig, run_beet
from beet.toolchain.cli import error_handler




def main():    
    config = {
        "data_pack": {
            "name": "datapack",
            "load": "tcc/datapack",
        },
        "pipeline": [
            "plugin"
        ],
        "output": "tcc_out"
    }
    print("Ran")
    with run_beet(config) as ctx:
        pass

if __name__ == "__main__":
    main()