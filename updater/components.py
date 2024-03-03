from nbtlib import parse_nbt, Compound, Int, serialize_tag, Byte, List, Short, IntArray, Float, Double
from itertools import zip_longest
from .constants import BASE_COLORS, DECORATION_IDS, FIREWORK_EXPLOSION_SHAPES

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


def find_components(nbt: Compound|str) -> tuple[str, dict]:
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
        components["minecraft:charged_projectiles"] = [handle_item_data(i) for i in charged_projectiles]
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

            components["minecraft:written_book_content"] = component
        else:
            components["minecraft:writable_book_content"] = component
    
    if trim := nbt.get('Trim'):
        components["minecraft:trim"] = {
            "material": trim.get("material", "UNKNOWN_MATERIAL"),
            "pattern": trim.get("pattern", "UNKNOWN_PATTERN")
        }
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
            "name": skull_owner.get("Name") 
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
            components.setdefault("minecraft:can_break", {
                "predciates": []
            })["show_in_tooltip"] = False

        if can_place:
            components.setdefault("minecraft:can_place_on", {
                "predciates": []
            })[
                "show_in_tooltip"
            ] = False

        if additional:
            components.setdefault("minecraft:hide_additional_tooltip", {})

        if dye:
            components.setdefault("minecraft:dyed_color", {"rgb": 0})[
                "show_in_tooltip"
            ] = False

        del nbt["HideFlags"]

    return (serialize_tag(nbt, compact=True), components)

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

def handle_attribute_modifier(modifier):
    if "attributename" in modifier:
        modifier["type"] = modifier["attributename"]
        del modifier["attributename"]

    if "operation" not in modifier:
        modifier["operation"] = "add_value"
    elif modifier["operation"] == "addition" or modifier["operation"] == 0:
        modifier["operation"] = "add_value"

    elif modifier["operation"] == "multiply_base" or modifier["operation"] == 1:
        modifier["operation"] = "add_multiplied_base"

    elif modifier["operation"] == "multiply_total" or modifier["operation"] == 2:
        modifier["operation"] = "add_multiplied_total"
