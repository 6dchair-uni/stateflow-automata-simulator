from .dfa import DFA


# def simulate(dfa: DFA, input_string: str):
#     current = dfa.start_state
#     steps = [current]

#     for symbol in input_string:
#         next_state = dfa.transition(current, symbol)

#         if next_state is None:
#             return {
#                 "accepted": False,
#                 "steps": steps,
#                 "error": f"No transition for '{symbol}' from {current}",
#             }

#         current = next_state
#         steps.append(current)

#     return {
#         "accepted": dfa.states[current].accepting,
#         "steps": steps,
#     }

from .dfa import DFA


def simulate(dfa: DFA, input_string: str):
    current = dfa.start_state
    steps = [current]
    symbols = []

    for symbol in input_string:
        next_state = dfa.transition(current, symbol)

        if next_state is None:
            return {
                "accepted": False,
                "steps": steps,
                "symbols": symbols,
                "error": f"No transition for '{symbol}' from {current}",
            }

        symbols.append(symbol)
        current = next_state
        steps.append(current)

    return {
        "accepted": dfa.states[current].accepting,
        "steps": steps,
        "symbols": symbols,
    }


# NFA SIMULATOR

from .nfa import NFA


def simulate_nfa(
    nfa: NFA,
    input_string: str,
):
    current_states = {
        nfa.start_state
    }

    steps = [
        sorted(current_states)
    ]

    symbols = []

    for symbol in input_string:

        next_states = nfa.transition(
            current_states,
            symbol,
        )

        symbols.append(symbol)

        current_states = next_states

        steps.append(
            sorted(current_states)
        )

        if not current_states:
            break

    accepted = any(
        nfa.states[state].accepting
        for state in current_states
    )

    return {
        "accepted": accepted,
        "steps": steps,
        "symbols": symbols,
    }