
from beet import ItemModifier

from updater.generic import handle_function


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