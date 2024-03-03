
"""
Converts item nbt to components and custom_data
"""
from beet import Predicate
from updater.components import find_components
from updater.components import handle_item_data




def handle_entity_properties_predicate(predicate: dict):
    if equipment := predicate.get("equipment"):
        for slot in equipment:
            handle_item_data(equipment[slot])

    if pred := predicate.get("vehicle"):
        handle_entity_properties_predicate(pred)
    if pred := predicate.get("passenger"):
        handle_entity_properties_predicate(pred)
    if pred := predicate.get("targetted_entity"):
        handle_entity_properties_predicate(pred)


def handle_location_predicate(predicate: dict):
    if structure := predicate.get('structure'):
        del predicate['structure']
        predicate['structures'] = structure

    if biome := predicate.get('biome'):
        del predicate['biome']
        predicate['biomes'] = biome

    if block := predicate.get('block'):
        if 'tag' in block:
            block['blocks'] = '#' + block['tag']
            del block['tag']    

    if fluid := predicate.get('fluid'):
        if 'tag' in fluid:
            fluid['fluids'] = '#' + fluid['tag']
            del fluid['tag']            

def handle_condition_predicate(c):
    match c["condition"].split(":")[-1]:
        case "entity_properties":
            handle_entity_properties_predicate(c["predicate"])
        case "match_tool":
            handle_item_data(c["predicate"])
        case "any_of" | "all_of":
            for c in c["terms"]:
                handle_condition_predicate(c)
        case "inverted":
            handle_condition_predicate(c["term"])
        case "location" | "location_check":
            handle_location_predicate(c["predicate"])


def handle_predicate(path: str, predicate: Predicate):
    print(f"Predicate: {path}")
    data = predicate.data

    if isinstance(data, list):
        for c in data:
            handle_condition_predicate(c)
    else:
        handle_condition_predicate(data)

    return Predicate(data)
