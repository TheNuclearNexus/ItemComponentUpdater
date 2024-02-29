# Item Component Updater

This script automatically updates most json files to be compatible with 24w09a's item component system.

## Known Issues:
- `MINECRAFT:ENTITY_DATA` and `MINECRAFT:BEES` use `UNKNOWN_ENTITY` when `id` wasn't present in the original `EntityTag`. 
- `MINECRAFT:ENTITY_DATA` is always used instead of `MINECRAFT:BUCKET_ENTITY_DATA`
- `MINECRAFT:BANNER_PATTERNS` still use the old 3 character pattern id

## Setup
1. Clone the repo
```
git clone https://github.com/TheNuclearNexus/ItemComponentUpdater
cd ItemComponentUpdater/
```
2. Install requirements
```
pip install -r requirements.txt
```
or
```
pip3 install -r requirements.txt
```

3. Run the script
```
python main.py -h
```
or 
```
python3 main.py -h
```

The script will also output a `functions.yaml` file within the datapack. 
This file shows all occurences of `item` nbt it could find as well as potential fixes for the path.
It can be wrong so copying and pasting directly is not recommended.
This doesn't account for all cases such as item nbt hiding within storage.

## Planned features
- Updating `give`, `item`, and `clear` commands
- Detecting `data` commands referencing the old `item.tag`
## Shameless self-promotion
Check out my main project over at https://smithed.net