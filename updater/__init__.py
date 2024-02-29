from beet import Context
from mecha import Mecha

from updater.advancement import handle_advancement
from updater.item_modifier import handle_item_modifier
from updater.loot_table import handle_loot_table
from updater.predicate import handle_predicate
from updater.recipe import handle_recipe
from updater.token import TokenReducer


def plugin(ctx: Context):
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

    mc = ctx.inject(Mecha)

    reducer = TokenReducer()

    for f in ctx.data.functions:
        lines = reducer.detect(mc.parse(ctx.data.functions[f]))
        if len(lines) > 0:
            print(f"Function: {f}")
            print("References tag on lines: " + ",".join(lines))
    yield