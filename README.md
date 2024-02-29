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

## Planned features
- Updating `give`, `item`, and `clear` commands
- Detecting `data` commands referencing the old `item.tag`
## Shameless self-promotion
Check out my main project over at https://smithed.net