from beet import Context, TextFile
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


    content = ""
    for f in ctx.data.functions:
        try:
            lines = reducer.detect(mc.parse(ctx.data.functions[f]))
            if len(lines.keys()) > 0:
                content += f"- function: {f}\n"
                content += "  - tag_references:\n"

                for l in lines:
                    content += "    - line: " + l + "\n"
                    for p in lines[l]:
                        content += "      - path: " + p[0] + "\n"

                        if p[0] != p[1]:
                            content += "         fix: " + p[1] + "\n"
        except:
            content += f"- function: {f}\n"
            content += '  - tag_references: errored while parsing\n'


    ctx.data.extra["functions.yaml"] = TextFile(content)
    yield
