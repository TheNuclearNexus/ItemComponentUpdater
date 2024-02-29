

from beet import LootTable
from updater.generic import handle_funcs_conds_dict


def handle_loot_entry(entry: dict):
    type: str = entry["type"].split(":")[-1]

    if type == "alternatives" or type == "group" or type == "sequence":
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

    handle_funcs_conds_dict(entry)

def handle_loot_table(path: str, loot_table: LootTable):
    print(f"Loot Table: {path}")
    data = loot_table.data
    handle_funcs_conds_dict(data)

    pools = data["pools"]
    for pool in pools:
        handle_funcs_conds_dict(pool)
        for entry in pool["entries"]:
            handle_loot_entry(entry)

    return LootTable(data)
