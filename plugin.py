from itertools import zip_longest
from typing import Union
from beet import Advancement, Context, ItemModifier, LootTable, Predicate, Recipe
from nbtlib import parse_nbt, Compound, Int, serialize_tag, Byte, List, Short, IntArray, Float, Double

DECORATION_IDS: list[str] = [
    "player",
    "frame",
    "red_marker",
    "blue_marker",
    "target_x",
    "target_point",
    "player_off_map",
    "player_off_limits",
    "mansion",
    "monument",
    "banner_white",
    "banner_orange",
    "banner_magenta",
    "banner_light_blue",
    "banner_yellow",
    "banner_lime",
    "banner_pink",
    "banner_gray",
    "banner_light_gray",
    "banner_cyan",
    "banner_purple",
    "banner_blue",
    "banner_brown",
    "banner_green",
    "banner_red",
    "banner_black",
    "red_x",
    "village_desert",
    "village_plains",
    "village_savanna",
    "village_snowy",
    "village_taiga",
    "jungle_temple",
    "swamp_hut"
]

FIREWORK_EXPLOSION_SHAPES = [
    "small_ball",
    "large_ball",
    "star",
    "creeper",
    "burst"
]

BASE_COLORS = [
    "white",
    "orange",
    "magenta",
    "light_blue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "light_gray",
    "cyan",
    "purple",
    "blue",
    "brown",
    "green",
    "red",
    "black"
]

def find_components(nbt: Union[Compound, str]) -> tuple[str, dict]:
    components: dict = {}
    nbt: Compound = parse_nbt(nbt) if isinstance(nbt, str) else nbt

    if cmd := nbt.get("CustomModelData"):
        cmd: Int = cmd
        components["minecraft:custom_model_data"] = cmd.as_unsigned
        del nbt["CustomModelData"]

    if damage := nbt.get("Damage"):
        damage: Int = damage
        components["minecraft:damage"] = damage.as_unsigned
        del nbt["Damage"]

    if repair_cost := nbt.get("RepairCost"):
        repair_cost: Int = repair_cost
        components["minecraft:repair_cost"] = repair_cost.as_unsigned
        del nbt["RepairCost"]

    if attribute_modifiers := nbt.get("AttributeModifiers"):
        attribute_modifiers: List = attribute_modifiers

        attr_components = {
            "modifiers": [],
        }

        for a in attribute_modifiers:
            attr = {}
            for k in a:
                attr[k.lower()] = a[k]
            handle_attribute_modifier(attr)

            uuid: IntArray = attr["uuid"]
            attr["uuid"] = uuid.tolist()
            attr_components["modifiers"].append(attr)

        components["minecraft:attribute_modifiers"] = attr_components
        del nbt["AttributeModifiers"]

    if enchantments := nbt.get("Enchantments"):
        enchantments: List = enchantments

        ench_component = handle_enchantments(nbt, components, enchantments)

        if len(ench_component["levels"].keys()) > 0:
            components["minecraft:enchantments"] = ench_component
        del nbt["Enchantments"]

    if stored_enchantments := nbt.get("StoredEnchantments"):
        stored_enchantments: List = stored_enchantments

        ench_component = handle_enchantments(nbt, components, stored_enchantments)

        if len(ench_component["levels"].keys()) > 0:
            components["minecraft:stored_enchantments"] = ench_component
        del nbt["StoredEnchantments"]

    if unbreakable := nbt.get("Unbreakable"):
        if unbreakable.as_unsigned == 1:
            components["!minecraft:damage"] = {}
            if "minecraft:damage" in components:
                del components["minecraft:damage"]
            del nbt["Unbreakable"]

    if display := nbt.get("display"):
        display: Compound = display

        if "Name" in display:
            name: str = display["Name"]
            components["minecraft:custom_name"] = name

        if "Lore" in display:
            lore: list[str] = display["Lore"]
            components["minecraft:lore"] = lore

        if "color" in display:
            color: Int = display["color"]
            components["minecraft:dyed_color"] = {"rgb": color}

        if "MapColor" in display:
            color: Int = display["MapColor"]
            components["minecraft:map_color"] = color

        del nbt["display"]

    if charged_projectiles := nbt.get("ChargedProjectiles"):
        components["minecraft:charged_projectiles"] = charged_projectiles
        del nbt["ChargedProjectiles"]

    if bundle_contents := nbt.get("Items"):
        components["minecraft:bundle_contents"] = [handle_item_data(i) for i in bundle_contents]
        del nbt["Items"]
    
    if decorations := nbt.get("Decorations"):
        for decoration in decorations:
            decoration['type'] = DECORATION_IDS[decoration['type'].as_unsigned]

            rot: Double = decoration['rot']
            decoration['rotation'] = rot.real
            del decoration['rot']

        components["minecraft:map_decorations"] = decorations
        del nbt["Decorations"]

    if map_id := nbt.get("map"):
        components["minecraft:map_id"] = map_id
        del nbt["map"]
        

    if "Potion" in nbt or "CustomPotionColor" in nbt or "custom_potion_effects" in nbt:
        potion = nbt.get("Potion")
        color = nbt.get("CustomPotionColor")
        effects = nbt.get("custom_potion_effects", [])

        contents = {
            "custom_effects": effects
        }

        if potion is not None:
            contents["potion"] = potion
            del nbt["Potion"]

        if color is not None:
            contents["custom_color"] = color
            del nbt["CustomPotionColor"]

        if len(effects) > 0:
            del nbt["custom_potion_effects"]

        components["minecraft:potion_contents"] = contents

    if pages := nbt.get("pages"):
        del nbt["pages"]

        filtered_pages = nbt.get("filtered_pages", [])
        title = nbt.get("title")
        filtered_title = nbt.get("filtered_title")
        author = nbt.get("author")
        generation = nbt.get("generation")
        resolved = nbt.get("resolved")

        component = {
            "pages": [],
        }

        for (text, filtered) in zip_longest(pages, filtered_pages):

            if filtered != None:
                page = {
                    "text": text,
                    "filtered": filtered
                }
            else:
                page = text

            component["pages"].append(page)

        if title != None or author != None or generation != None or resolved != None:
            if title != None and filtered_title != None:
                component["title"] = {
                    "text": title,
                    "filtered": filtered_title
                }

                del nbt["title"]
                del nbt["filtered_title"]
            elif title:
                component["title"] = title
                del nbt["title"]

            if author:
                component["author"] = author
                del nbt["author"]

            if generation:
                del nbt["generation"]

            component["generation"] = generation if generation else 0

            if resolved:
                del nbt["resolved"]
            component["resolved"] = resolved

            components["minecraft:written_book_contents"] = component
        else:
            components["minecraft:writable_book_contents"] = component
    
    if trim := nbt.get('Trim'):
        components["minecraft:trim"] = trim
        del nbt['Trim']

    if effects := nbt.get('effects'):
        components["minecraft:suspicious_stew"] = effects
        del nbt['effects']

    if debug_property := nbt.get("DebugProperty"):
        components["minecraft:debug_stick_state"] = debug_property
        del nbt['DebugProperty']

    if entity_tag := nbt.get("EntityTag"):
        if "id" not in entity_tag:
            entity_tag["id"] = "UNKNOWN_ENTITY"
        components["minecraft:entity_data"] = entity_tag
        del nbt["EntityTag"]
    
    if instrument := nbt.get("instrument"):
        components["minecraft:instrument"] = instrument
        del nbt["instrument"]

    if recipes := nbt.get("Recipes"):
        components["minecraft:recipes"] = recipes
        del nbt["Recipes"]

    if pos := nbt.get("LodestonePos"):
        dim = nbt.get("LodestoneDimension")
        tracked = nbt.get("LodestoneTracked", 1)

        components["minecraft:lodestone_target"] = {
            "pos": [pos.get("X", 0), pos.get("Y", 0), pos.get("Z", 0)],
            "dimension": dim,
            "tracked": True if tracked == 1 else False
        }

        del nbt["LodestonePos"]
        del nbt["LodestoneDimension"]

        if "LodestoneTracked" in nbt:
            del nbt["LodestoneTracked"]
    
    if explosion := nbt.get("Explosion"):
        components["minecraft:firework_explosion"] = handle_explosion(explosion)
        del nbt["Explosion"]
    
    if fireworks := nbt.get("Fireworks"):
        components["minecraft:fireworks"] = {
            "explosions": [handle_explosion(e) for e in fireworks.get("Explosions", [])],
            "flight_duration": fireworks.get("Flight")
        }
        del nbt["Fireworks"]

    if skull_owner := nbt.get("SkullOwner"):
        component = {
            name: skull_owner.get("Name") 
        }

        if id := skull_owner.get("Id"):
            component["id"] = id.tolist()
        
        if properties := skull_owner.get("Properties"):
            component["properties"] = properties

        components["minecraft:profile"] = component
        del nbt["SkullOwner"]

    if block_entity_tag := nbt.get("BlockEntityTag"):
        if note_block_sound := block_entity_tag.get("note_block_sound"):
            components["minecraft:note_block_sound"] = note_block_sound
            del block_entity_tag["note_block_sound"]
        
        if base_color := block_entity_tag.get("Base"):
            components["minecraft:base_color"] = BASE_COLORS[base_color.as_unsigned]
            del block_entity_tag["Base"]

        if patterns := block_entity_tag.get("Patterns"):
            for p in patterns:
                p['pattern'] = p['Pattern']
                p['color'] = BASE_COLORS[p['Color'].as_unsigned]
                del p['Pattern']
                del p['Color']

            del block_entity_tag["Patterns"]
            components["minecraft:banner_patterns"] = patterns

        if pot_decorations := block_entity_tag.get("sherds"):
            components["minecraft:pot_decorations"] = pot_decorations
            del block_entity_tag["sherds"]
        
        if items := block_entity_tag.get("Items"):
            components["minecraft:container"] = [handle_slotted_item(i) for i in items]
            del block_entity_tag["Items"]
        
        if bees := block_entity_tag.get("Bees"):
            for bee in bees:
                bee['entity_data'] = bee['EntityData']
                del bee['EntityData']

                if 'id' not in bee['entity_data']:
                    bee['entity_data']['id'] = "UNKNOWN_ENTITY"

                bee['ticks_in_hive'] = bee['TicksInHive']
                del bee['TicksInHive']
                bee['min_ticks_in_hive'] = bee['MinOccupationTicks']
                del bee['MinOccupationTicks']
            
            components["minecraft:bees"] = bees
            del block_entity_tag["Bees"]

        if lock := block_entity_tag.get("Lock"):
            components["minecraft:lock"] = lock
            del block_entity_tag["Lock"]

        if loot_table := block_entity_tag.get("LootTable"):
            components["minecraft:container_loot"] = {
                "loot_table": loot_table,
                "seed": block_entity_tag.get("LootTableSeed", 0)
            }
            del block_entity_tag["LootTable"]

        if len(block_entity_tag.values()) > 0:
            components["minecraft:block_entity_data"] = block_entity_tag

        del nbt["BlockEntityTag"]

    if block_state := nbt.get("BlockStateTag"):
        components["minecraft:block_state"] = block_state
        del nbt['BlockStateTag']
        
        
    if hide_flags := nbt.get("HideFlags"):
        hide_flags: int = hide_flags.as_unsigned

        enchantments = True if hide_flags & 0b0000001 > 0 else False
        modifiers = True if hide_flags & 0b0000010 > 0 else False
        unbreakable = True if hide_flags & 0b0000100 > 0 else False
        can_destroy = True if hide_flags & 0b0001000 > 0 else False
        can_place = True if hide_flags & 0b0010000 > 0 else False
        additional = True if hide_flags & 0b0100000 > 0 else False
        dye = True if hide_flags & 0b1000000 > 0 else False

        if enchantments:
            components.setdefault(
                (
                    "minecraft:enchantments"
                    if "minecraft:stored_enchantments" not in components
                    else "minecraft:stored_enchantments"
                ),
                {"levels": {}},
            )["show_in_tooltip"] = False

        if modifiers:
            components.setdefault("minecraft:attribute_modifiers", {"modifiers": []})[
                "show_in_tooltip"
            ] = False

        # if unbreakable and "!minecraft:damage" in components:
        #     components["minecraft:unbreakable"][
        #         "show_in_tooltip"
        #     ] = False

        if can_destroy:
            components.setdefault("minecraft:can_break", {})["show_in_tooltip"] = False

        if can_place:
            components.setdefault("minecraft:can_place_on", {})[
                "show_in_tooltip"
            ] = False

        if additional:
            components.setdefault("minecraft:hide_additional_tooltip", {})

        if dye:
            components.setdefault("minecraft:dyed_color", {"color": 0})[
                "show_in_tooltip"
            ] = False

        del nbt["HideFlags"]

    return (serialize_tag(nbt, compact=True), components)

def handle_explosion(explosion):
    return {
            "shape": FIREWORK_EXPLOSION_SHAPES[explosion.get("Type")],
            "colors": explosion.get("Colors", IntArray([])).tolist(),
            "fade_colors": explosion.get("FadeColors", IntArray([])).tolist(),
            "has_trail": True if explosion.get("Trail").as_unsigned == 1 else False,
            "has_flicker": True if explosion.get("Flicker").as_unsigned == 1 else False
        }


def handle_enchantments(nbt, components, enchantments):
    ench_component = {
        "levels": {},
    }

    for e in enchantments:
        id: str = e.get("id", "")
        if id == "":
            components["minecraft:enchantment_glint_override"] = True
            continue

        if not id.startswith("minecraft:"):
            id = "minecraft:" + id

        ench_component["levels"][id] = e.get("lvl", Short(1)).as_unsigned
    return ench_component


def handle_loot_entry(entry: dict):
    type: str = entry["type"].split(":")[-1]

    if type == "alternatives" or type == "group":
        for c in entry["children"]:
            handle_loot_entry(c)
        return

    # if type == "item":
    #     entry["id"] = entry["name"]
    #     del entry["name"]

    if type == "loot_table":
        entry["value"] = entry["name"]
        del entry["name"]

    if "functions" not in entry:
        return

    handle_common_loot_dict(entry)


def handle_function_list(functions: list[dict]) -> list[dict]:
    new_functions = []

    for function in functions:
        handle_function(new_functions, function)

    return new_functions


def handle_loot_table(path: str, loot_table: LootTable):
    print(f"Loot Table: {path}")
    data = loot_table.data
    handle_common_loot_dict(data)

    pools = data["pools"]
    for pool in pools:
        handle_common_loot_dict(pool)
        for entry in pool["entries"]:
            handle_loot_entry(entry)

    return LootTable(data)


def handle_common_loot_dict(dict: dict):
    if functions := dict.get("functions"):
        dict["functions"] = handle_function_list(functions)

    if conditions := dict.get("conditions"):
        for c in conditions:
            handle_condition_predicate(c)


def handle_function(function_list: list[dict], function: dict):
    function_list.append(function)
    type = function["function"].split(":")[-1]

    handle_common_loot_dict(function)

    match type:
        case "set_nbt":
            function["function"] = "minecraft:set_custom_data"
            (new_tag, components) = find_components(function["tag"])

            if new_tag == "{}":
                function_list.pop()
            else:
                function["tag"] = new_tag

            if len(components.keys()) > 0:
                function_list.append(
                    {
                        "function": "minecraft:set_components",
                        "components": components,
                    }
                )

            if "conditions" in function:
                function_list[-1]["conditions"] = function["conditions"]

        case "copy_nbt":
            function["function"] = "minecraft:copy_custom_data"

        case "set_attributes":
            for modifier in function["modifiers"]:
                handle_attribute_modifier(modifier)


def handle_attribute_modifier(modifier):
    if "attributename" in modifier:
        modifier["type"] = modifier["attributename"]
        del modifier["attributename"]

    if modifier["operation"] == "addition" or modifier["operation"] == 0:
        modifier["operation"] = "add_value"

    elif modifier["operation"] == "multiply_base" or modifier["operation"] == 1:
        modifier["operation"] = "add_multiplied_base"

    elif modifier["operation"] == "multiply_total" or modifier["operation"] == 2:
        modifier["operation"] = "add_multiplied_total"


def handle_slotted_item(slotted_item): 
    
    if "Slot" in slotted_item:
        slot = slotted_item["Slot"].as_unsigned
        del slotted_item["Slot"]
    else:
        slot = 0
    handle_item_data(slotted_item, data_holder="tag")

    return {
        "slot": slot,
        "item": slotted_item
    }

"""
Converts item nbt to components and custom_data
"""
def handle_item_data(item: dict, allow_air=True, data_holder="nbt"):
    if "item" in item:
        item["id"] = item["item"]
        del item["item"]

    if "id" in item and item["id"] == "minecraft:air" and not allow_air:
        item["id"] = "minecraft:stone"

    if "Count" in item:
        item["count"] = item["Count"].as_unsigned
        del item["Count"]

    if data_holder not in item:
        return item
    
    (custom_data, components) = find_components(item[data_holder])
    del item[data_holder]

    if custom_data != "{}":
        item["custom_data"] = custom_data
    if len(components.keys()) > 0:
        item["components"] = components

    return item


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


def handle_advancement_trigger(trigger: dict):
    if "conditions" not in trigger:
        return

    conditions = trigger["conditions"]

    if item := conditions.get("item"):
        handle_item_data(item)

    if items := conditions.get("items"):
        for i in items:
            handle_item_data(i)

    if pred := conditions.get("entity"):
        handle_legacy_or_list(pred)

    if pred := conditions.get("player"):
        handle_legacy_or_list(pred)


def handle_legacy_or_list(pred: Union[list, dict]):
    if isinstance(pred, dict):
        handle_entity_properties_predicate(pred)
    else:
        for c in pred:
            handle_condition_predicate(c)

def handle_location_predicate(predicate: dict):
    if structure := predicate.get('structure'):
        del predicate['structure']
        predicate['structures'] = structure

    if biome := predicate.get('biome'):
        del predicate['biome']
        predicate['biomes'] = biome

    if block := predicate.get('block'):
        if 'tag' in block:
            block['block'] = '#' + block['tag']
            del block['tag']    

    if fluid := predicate.get('fluid'):
        if 'tag' in fluid:
            fluid['fluid'] = '#' + fluid['tag']
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
        case "location":
            handle_location_predicate(c["predicate"])


def handle_advancement(path: str, advancement: Advancement):
    print(f"Advancement: {path}")
    data = advancement.data

    if display := data.get("display"):
        if icon := display.get("icon"):

            handle_item_data(icon, allow_air=False)

    if criteria := data.get("criteria"):
        for trigger in criteria.values():
            handle_advancement_trigger(trigger)

    return Advancement(data)


def handle_predicate(path: str, predicate: Predicate):
    print(f"Predicate: {path}")
    data = predicate.data

    if isinstance(data, list):
        for c in data:
            handle_condition_predicate(c)
    else:
        handle_condition_predicate(data)

    return Predicate(data)


def handle_recipe(path: str, recipe: Recipe):
    print(f"Recipe: {path}")
    data = recipe.data

    if result := data.get("result"):
        if isinstance(result, str) and data["type"].split(":")[-1] == "stonecutting":
            data["result"] = {"id": result, "count": data.get("count", 1)}

            if "count" in data:
                del data["count"]
        else:
            handle_item_data(result)

    return Recipe(data)

def handle_item_modifier(path: str, modifer: ItemModifier):
    data = modifer.data

    if isinstance(data, list):
        modifers = []
        for f in data:
            handle_function(modifers, f)
        data = modifers
    else:
        modifers = []
        handle_function(modifers,data)
        if len(modifers) > 1:
            data = modifers
        else:
            data = modifers[0]

    return ItemModifier(data)

def beet_default(ctx: Context):
    for l in ctx.data.loot_tables:
        ctx.data[l] = handle_loot_table(l, ctx.data.loot_tables[l])

    for l in ctx.data.advancements:
        ctx.data[l] = handle_advancement(l, ctx.data.advancements[l])

    for l in ctx.data.predicates:
        ctx.data[l] = handle_predicate(l, ctx.data.predicates[l])

    for l in ctx.data.recipes:
        ctx.data[l] = handle_recipe(l, ctx.data.recipes[l])

    for l in ctx.data.item_modifiers:
        ctx.data[l] = handle_item_modifier(l, ctx.data.item_modifiers[l])
    yield
