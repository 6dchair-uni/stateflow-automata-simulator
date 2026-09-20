from dataclasses import dataclass
from typing import Literal


@dataclass
class CountModRule:
    symbol: str
    modulus: int
    remainder: int


@dataclass
class LanguageSpecification:
    automaton_type: Literal["DFA", "NFA", "PDA"]
    alphabet: list[str]
    rule_type: str
    count_mod: CountModRule | None = None
