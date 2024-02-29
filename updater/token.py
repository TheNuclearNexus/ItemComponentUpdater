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


class TokenReducer(Reducer):
    lines: dict[str, list[str]] = {}

    def detect(self, node) -> dict[str, list[str]]:
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
            self.lines.setdefault(str(node.location.lineno), []).append(final)


# 1-1-1
