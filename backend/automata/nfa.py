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


class NFA:
    def __init__(
        self,
        states: list[State],
        alphabet: list[str],
        transitions: list[Transition],
        start_state: str,
    ):
        self.states = {
            state.id: state
            for state in states
        }

        self.alphabet = alphabet
        self.start_state = start_state

        self.transitions = {}

        for transition in transitions:
            key = (
                transition.from_state,
                transition.symbol,
            )

            if key not in self.transitions:
                self.transitions[key] = set()

            self.transitions[key].add(
                transition.to_state
            )

    def transition(
        self,
        states: set[str],
        symbol: str,
    ) -> set[str]:

        next_states = set()

        for state in states:
            destinations = self.transitions.get(
                (state, symbol),
                set(),
            )

            next_states.update(destinations)

        return next_states

    def accepts(
        self,
        input_string: str,
    ) -> bool:

        current_states = {
            self.start_state
        }

        for symbol in input_string:
            current_states = self.transition(
                current_states,
                symbol,
            )

            if not current_states:
                return False

        return any(
            self.states[state].accepting
            for state in current_states
        )