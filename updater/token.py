from dataclasses import dataclass
from mecha import AstNbtPath, Reducer, rule

@dataclass
class TokenReducer(Reducer):
    lines = []
    def detect(self, node) -> list[str]:
        self.lines = []
        self.__call__(node)
        return self.lines

    @rule(AstNbtPath)
    def path(self, node: AstNbtPath):
        for key in node.components:
            try:
                if key.value == 'tag':
                    self.lines.append(str(key.location.lineno))
            except:
                pass
# 1-1-1