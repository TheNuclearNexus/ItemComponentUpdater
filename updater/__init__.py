from beet import Context

from updater.advancement import handle_advancement
from updater.item_modifier import handle_item_modifier
from updater.loot_table import handle_loot_table
from updater.predicate import handle_predicate
from updater.recipe import handle_recipe


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
    yield
