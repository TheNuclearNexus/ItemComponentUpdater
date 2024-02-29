
from updater.components import find_components, handle_attribute_modifier
from updater.predicate import handle_condition_predicate




def handle_funcs_conds_dict(dict: dict):
    if functions := dict.get("functions"):
        dict["functions"] = handle_function_list(functions)

    if conditions := dict.get("conditions"):
        for c in conditions:
            handle_condition_predicate(c)


def handle_function_list(functions: list[dict]) -> list[dict]:
    new_functions = []

    for function in functions:
        handle_function(new_functions, function)

    return new_functions


def handle_function(function_list: list[dict], function: dict):
    function_list.append(function)
    type = function["function"].split(":")[-1]

    handle_funcs_conds_dict(function)

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
