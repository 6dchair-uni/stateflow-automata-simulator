from dataclasses import dataclass


@dataclass
class State:
    id: str
    accepting: bool = False


@dataclass
class Transition:
    from_state: str
    symbol: str
    to_state: str


class DFA:
    def __init__(
        self,
        states: list[State],
        alphabet: list[str],
        transitions: list[Transition],
        start_state: str,
    ):
        self.states = {state.id: state for state in states}
        self.alphabet = alphabet
        self.start_state = start_state

        self.transitions = {
            (transition.from_state, transition.symbol): transition.to_state
            for transition in transitions
        }

    def transition(self, state: str, symbol: str) -> str | None:
        return self.transitions.get((state, symbol))

    def accepts(self, input_string: str) -> bool:
        current = self.start_state

        for symbol in input_string:
            next_state = self.transition(current, symbol)

            if next_state is None:
                return False

            current = next_state

        return self.states[current].accepting