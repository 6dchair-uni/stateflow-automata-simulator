from .dfa import DFA, State, Transition


def generate_dfa(description: str) -> DFA:
    normalized = description.strip().lower()

    # --------------------------------------------------
    # Binary strings ending in 01
    # --------------------------------------------------

    if (
        "binary" in normalized
        and "ending" in normalized
        and "01" in normalized
    ):
        return DFA(
            states=[
                State("q0"),
                State("q1"),
                State("q2", accepting=True),
            ],
            alphabet=["0", "1"],
            transitions=[
                Transition("q0", "0", "q1"),
                Transition("q0", "1", "q0"),
                Transition("q1", "0", "q1"),
                Transition("q1", "1", "q2"),
                Transition("q2", "0", "q1"),
                Transition("q2", "1", "q0"),
            ],
            start_state="q0",
        )

    # --------------------------------------------------
    # Binary strings beginning with 1
    # --------------------------------------------------

    if (
        "binary" in normalized
        and (
            "beginning with 1" in normalized
            or "start with 1" in normalized
            or "starting with 1" in normalized
        )
    ):
        return DFA(
            states=[
                State("q0"),
                State("q1", accepting=True),
                State("q2"),
            ],
            alphabet=["0", "1"],
            transitions=[
                Transition("q0", "0", "q2"),
                Transition("q0", "1", "q1"),

                Transition("q1", "0", "q1"),
                Transition("q1", "1", "q1"),

                Transition("q2", "0", "q2"),
                Transition("q2", "1", "q2"),
            ],
            start_state="q0",
        )

    # --------------------------------------------------
    # Binary strings containing at least one 0
    # --------------------------------------------------

    if (
        "binary" in normalized
        and (
            "at least one 0" in normalized
            or "contain a 0" in normalized
            or "containing a 0" in normalized
        )
    ):
        return DFA(
            states=[
                State("q0"),
                State("q1", accepting=True),
            ],
            alphabet=["0", "1"],
            transitions=[
                Transition("q0", "0", "q1"),
                Transition("q0", "1", "q0"),

                Transition("q1", "0", "q1"),
                Transition("q1", "1", "q1"),
            ],
            start_state="q0",
        )

    # --------------------------------------------------
    # Binary strings with an even number of 1s
    # --------------------------------------------------

    if (
        "binary" in normalized
        and (
            "even number of 1" in normalized
            or "even number of ones" in normalized
        )
    ):
        return DFA(
            states=[
                State("q0", accepting=True),
                State("q1"),
            ],
            alphabet=["0", "1"],
            transitions=[
                Transition("q0", "0", "q0"),
                Transition("q0", "1", "q1"),

                Transition("q1", "0", "q1"),
                Transition("q1", "1", "q0"),
            ],
            start_state="q0",
        )

    # --------------------------------------------------
    # Binary strings with an odd number of 0s
    # --------------------------------------------------

    if (
        "binary" in normalized
        and (
            "odd number of 0" in normalized
            or "odd number of zeros" in normalized
        )
    ):
        return DFA(
            states=[
                State("q0"),
                State("q1", accepting=True),
            ],
            alphabet=["0", "1"],
            transitions=[
                Transition("q0", "0", "q1"),
                Transition("q0", "1", "q0"),

                Transition("q1", "0", "q0"),
                Transition("q1", "1", "q1"),
            ],
            start_state="q0",
        )

    raise ValueError(
        "I don't recognize this language description yet."
    )

def generate_count_mod_dfa(
    alphabet: list[str],
    symbol: str,
    modulus: int,
    remainder: int,
) -> DFA:

    if modulus <= 0:
        raise ValueError(
            "Modulus must be greater than zero."
        )

    if remainder < 0 or remainder >= modulus:
        raise ValueError(
            "Remainder must be between 0 and modulus - 1."
        )

    if symbol not in alphabet:
        raise ValueError(
            f"Symbol '{symbol}' is not in the alphabet."
        )

    states = [
        State(
            f"q{i}",
            accepting=(i == remainder),
        )
        for i in range(modulus)
    ]

    transitions = []

    for i in range(modulus):

        for current_symbol in alphabet:

            if current_symbol == symbol:
                next_state = (i + 1) % modulus
            else:
                next_state = i

            transitions.append(
                Transition(
                    f"q{i}",
                    current_symbol,
                    f"q{next_state}",
                )
            )

    return DFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state="q0",
    )


def generate_from_description(description: str) -> DFA:
    normalized = description.strip().lower()

    # Number of 1s divisible by N
    if (
        "binary" in normalized
        and "1" in normalized
        and (
            "divisible by" in normalized
            or "multiple of" in normalized
        )
    ):
        import re

        match = re.search(
            r"(?:divisible by|multiple of)\s+(\d+)",
            normalized,
        )

        if match:
            modulus = int(match.group(1))

            return generate_count_mod_dfa(
                alphabet=["0", "1"],
                symbol="1",
                modulus=modulus,
                remainder=0,
            )

    return generate_dfa(description)




from .dfa import DFA, State, Transition


def generate_count_exact_dfa(
    alphabet: list[str],
    symbol: str,
    count: int,
) -> DFA:
    states = [
        State(f"q{i}", accepting=(i == count))
        for i in range(count + 1)
    ]

    transitions = []

    for i in range(count + 1):
        # Counting the target symbol
        if i < count:
            transitions.append(
                Transition(
                    f"q{i}",
                    symbol,
                    f"q{i + 1}",
                )
            )
        else:
            # Once we exceed the required count,
            # go to a dead state.
            transitions.append(
                Transition(
                    f"q{i}",
                    symbol,
                    "dead",
                )
            )

        # Other symbols do not change the count.
        for other in alphabet:
            if other != symbol:
                transitions.append(
                    Transition(
                        f"q{i}",
                        other,
                        f"q{i}",
                    )
                )

    # Dead state
    states.append(
        State("dead", accepting=False)
    )

    for symbol_value in alphabet:
        transitions.append(
            Transition(
                "dead",
                symbol_value,
                "dead",
            )
        )

    return DFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state="q0",
    )


def generate_starts_with_dfa(
    alphabet: list[str],
    prefix: str,
) -> DFA:
    states = []

    for i in range(len(prefix) + 1):
        states.append(
            State(
                f"q{i}",
                accepting=(i == len(prefix)),
            )
        )

    states.append(
        State("dead", accepting=False)
    )

    transitions = []

    for i in range(len(prefix)):
        expected = prefix[i]

        for symbol in alphabet:
            if symbol == expected:
                transitions.append(
                    Transition(
                        f"q{i}",
                        symbol,
                        f"q{i + 1}",
                    )
                )
            else:
                transitions.append(
                    Transition(
                        f"q{i}",
                        symbol,
                        "dead",
                    )
                )

    # Once the prefix has been matched,
    # everything is accepted.
    for symbol in alphabet:
        transitions.append(
            Transition(
                f"q{len(prefix)}",
                symbol,
                f"q{len(prefix)}",
            )
        )

        transitions.append(
            Transition(
                "dead",
                symbol,
                "dead",
            )
        )

    return DFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state="q0",
    )


def generate_ends_with_dfa(
    alphabet: list[str],
    suffix: str,
) -> DFA:
    """
    DFA for strings ending with the given suffix.

    Uses the longest suffix/prefix relationship
    to determine the next state.
    """

    states = [
        State(
            f"q{i}",
            accepting=(i == len(suffix)),
        )
        for i in range(len(suffix) + 1)
    ]

    transitions = []

    for i in range(len(suffix) + 1):
        for symbol in alphabet:
            candidate = suffix[:i] + symbol

            next_state = 0

            for j in range(
                min(len(suffix), len(candidate)),
                -1,
                -1,
            ):
                if candidate.endswith(
                    suffix[:j]
                ):
                    next_state = j
                    break

            transitions.append(
                Transition(
                    f"q{i}",
                    symbol,
                    f"q{next_state}",
                )
            )

    return DFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state="q0",
    )


def generate_contains_dfa(
    alphabet: list[str],
    pattern: str,
) -> DFA:
    """
    DFA that accepts strings containing
    the given pattern.
    """

    states = [
        State(
            f"q{i}",
            accepting=(i == len(pattern)),
        )
        for i in range(len(pattern) + 1)
    ]

    transitions = []

    for i in range(len(pattern) + 1):
        for symbol in alphabet:
            if i == len(pattern):
                next_state = len(pattern)
            else:
                candidate = pattern[:i] + symbol

                next_state = 0

                for j in range(
                    min(len(pattern), len(candidate)),
                    -1,
                    -1,
                ):
                    if candidate.endswith(
                        pattern[:j]
                    ):
                        next_state = j
                        break

            transitions.append(
                Transition(
                    f"q{i}",
                    symbol,
                    f"q{next_state}",
                )
            )

    return DFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state="q0",
    )


def generate_from_rule(rule: dict, alphabet: list[str]) -> DFA:
    rule_type = rule["type"]

    if rule_type == "count_mod":
        return generate_count_mod_dfa(
            alphabet=alphabet,
            symbol=rule["symbol"],
            modulus=rule["modulus"],
            remainder=rule["remainder"],
        )

    if rule_type == "count_exact":
        return generate_count_exact_dfa(
            alphabet=alphabet,
            symbol=rule["symbol"],
            count=rule["count"],
        )

    if rule_type == "starts_with":
        return generate_starts_with_dfa(
            alphabet=alphabet,
            prefix=rule["prefix"],
        )

    if rule_type == "ends_with":
        return generate_ends_with_dfa(
            alphabet=alphabet,
            suffix=rule["suffix"],
        )

    if rule_type == "contains":
        return generate_contains_dfa(
            alphabet=alphabet,
            pattern=rule["pattern"],
        )

    raise ValueError(
        f"Unsupported rule type: {rule_type}"
    )





# NFA GENERATOR

from .nfa import NFA, State as NFAState, Transition as NFATransition


def generate_contains_nfa(
    alphabet: list[str],
    pattern: str,
) -> NFA:
    """
    NFA that accepts strings containing
    the given pattern.
    """

    states = [
        NFAState(
            f"q{i}",
            accepting=(i == len(pattern)),
        )
        for i in range(len(pattern) + 1)
    ]

    transitions = []

    # q0 can keep consuming symbols while
    # nondeterministically choosing a position
    # where the pattern might begin.
    for symbol in alphabet:
        transitions.append(
            NFATransition(
                "q0",
                symbol,
                "q0",
            )
        )

    # Pattern matching path
    for i, symbol in enumerate(pattern):
        transitions.append(
            NFATransition(
                f"q{i}",
                symbol,
                f"q{i + 1}",
            )
        )

    # Once the pattern has been found,
    # remain accepting.
    for symbol in alphabet:
        transitions.append(
            NFATransition(
                f"q{len(pattern)}",
                symbol,
                f"q{len(pattern)}",
            )
        )

    return NFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state="q0",
    )