from dataclasses import dataclass
from typing import Union

from leaf_focus.report.input.line import Line
from leaf_focus.report.output.definition import DefinitionLine, DefinitionTable


@dataclass
class Match:
    line: Line
    definition: Union[DefinitionLine, DefinitionTable]
    index: int
    data: Union[bool, dict, list[dict]]

    def __str__(self):
        if isinstance(self.data, dict):
            return "; ".join(
                (
                    str(i)
                    for i in [
                        f"line {self.line.index}",
                        self.data,
                        self.definition,
                        self.index,
                    ]
                )
            )
        else:
            return "; ".join((str(i) for i in [self.line, self.definition, self.index]))
