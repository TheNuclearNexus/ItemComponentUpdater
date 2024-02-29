from dataclasses import dataclass
from mecha import (
    AstNbtCompound,
    AstNbtPath,
    AstNbtPathKey,
    AstNbtPathSubscript,
    Reducer,
    rule,
)
from nbtlib import Compound, List, serialize_tag

PATH_MAPPINGS = [("tag." + i[0], "components." + i[1]) for i in [
    ('Damage', '"minecraft:damage"'),
    ('CustomModelData', '"minecraft:custom_model_data"'),
    ('Enchantments', '"minecraft:enchantments"'),
    ('StoredEnchantments', '"minecraft:stored_enchantments"'),
    ('RepairCost', '"minecraft:repair_cost"'),
    ('AttributeModifiers', '"minecraft:attribute_modifiers"'),
    ('Unbreakable', '"minecraft:unbreakable"'),
    ('display.Name', '"minecraft:custom_name"'),
    ('display.Lore', '"minecraft:lore"'),
    ('display.color', '"minecraft:dyed_color"'),
    ('display.MapColor', '"minecraft:map_color"'),
    ('ChargedProjectiles', '"minecraft:charged_projectiles"'),
    ('Items', '"minecraft:bundle_contents"'),
    ('Decorations', '"minecraft:map_decorations"'),
    ('map', '"minecraft:map_id"'),
    ('Potion', '"minecraft:potion_contents".potion'),
    ('CustomPotionColor', '"minecraft:potion_contents".custom_color'),
    ('custom_effects', '"minecraft:potion_contents".custom_effects'),
    ('Trim', '"minecraft:trim"'),
    ('effects', '"minecraft:suspicious_stew"'),
    ('DebugProperty', '"minecraft:debug_stick_state"'),
    ('EntityTag', '"minecraft:entity_data"'),
    ('instrument', '"minecraft:instrument"'),
    ('Recipes', '"minecraft:recipes"'),
    ('LodestonePos.X', '"minecraft:lodestone_target".pos[0]'),
    ('LodestonePos.Y', '"minecraft:lodestone_target".pos[1]'),
    ('LodestonePos.Z', '"minecraft:lodestone_target".pos[2]'),
    ('LodestonePos', '"minecraft:lodestone_target".pos'),
    ('LodestoneDim', '"minecraft:lodestone_target".dimension'),
    ('LodestoneTracked', '"minecraft:lodestone_target".tracked'),
    ('Explosion', '"minecraft:firework_explosion"'),
    ('Fireworks', '"minecraft:fireworks"'),
    ('SkullOwner.Name', '"minecraft:profile".name'),
    ('SkullOwner.Id', '"minecraft:profile".id'),
    ('SkullOwner', '"minecraft:profile"'),
    ('BlockEntityTag.note_block_sound', '"minecraft:note_block_sound"'),
    ('BlockEntityTag.Base', '"minecraft:base_color"'),
    ('BlockEntityTag.Patterns', '"minecraft:banner_patterns"'),
    ('BlockEntityTag.sherds', '"minecraft:pot_decorations"'),
    ('BlockEntityTag.Items', '"minecraft:container"'),
    ('BlockEntityTag.Bees', '"minecraft:bees"'),
    ('BlockEntityTag.Lock', '"minecraft:lock"'),
    ('BlockEntityTag.LootTable', '"minecraft:loot_table".loot_table'),
    ('BlockEntityTag.LootTableSeed', '"minecraft:loot_table".seed'),
    ('BlockEntityTag', '"minecraft:block_entity_data"'),
    ('BlockStateTag', '"minecraft:block_state"'),
]]
PATH_MAPPINGS.append(('tag.', 'components."minecraft:custom_data".'))


class TokenReducer(Reducer):
    lines: dict[str, list[tuple[str, str]]] = {}

    def detect(self, node) -> dict[str, list[tuple[str, str]]]:
        self.lines = {}
        self.__call__(node)
        return self.lines
    
    def search(self, value: Compound|List) -> Compound|None:
        if isinstance(value, Compound):
            for k in value.keys():
                if k == 'tag':
                    return value[k]
                if tag := self.search(value[k]):
                    return tag
                
        if isinstance(value, List):
            for k in value:
                if tag := self.search(k):
                    return tag

        return None
    
    def correct(self, path: str) -> str:
        for kv in PATH_MAPPINGS:
            path = path.replace(kv[0], kv[1])
        return path
    @rule(AstNbtPath)
    def path(self, node: AstNbtPath):
        path = []
        found_tag = False
        for key in node.components:
            if isinstance(key, AstNbtPathKey):
                if key.value == "tag":
                    found_tag = True
                path.append(key.value)
            elif isinstance(key, AstNbtPathSubscript):
                if key.index == None:
                    value = "[]"
                elif isinstance(key.index, AstNbtCompound):
                    nbt = key.index.evaluate()
                    value = f"[{serialize_tag(nbt)}]"

                    if self.search(nbt):
                        found_tag = True

                else:
                    value = f"[{key.index.value}]"

                if len(path) >= 1:
                    prev = path[-1]
                    path[-1] = prev + value
                else:
                    path.append(value)
            elif isinstance(key, AstNbtCompound):
                nbt = key.evaluate()
                value = serialize_tag(nbt)
                if self.search(nbt):
                    found_tag = True

                if len(path) >= 1:
                    prev = path[-1]
                    path[-1] = prev + value
                else:
                    path.append(value)

        if found_tag:
            final = '.'.join(path)
            self.lines.setdefault(str(node.location.lineno), []).append((final, self.correct(final)))


# 1-1-1
