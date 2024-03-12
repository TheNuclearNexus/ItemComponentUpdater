
from typing import Union
from beet import Advancement
from updater.components import handle_item_data
from updater.predicate import handle_condition_predicate, handle_entity_properties_predicate


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

    if pred := conditions.get("location"):
        handle_legacy_or_list(pred)

def handle_legacy_or_list(pred: Union[list, dict]):
    if isinstance(pred, dict):
        handle_entity_properties_predicate(pred)
    else:
        for c in pred:
            handle_condition_predicate(c)


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