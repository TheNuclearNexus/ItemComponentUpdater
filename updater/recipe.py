
from beet import Recipe

from updater.components import handle_item_data


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