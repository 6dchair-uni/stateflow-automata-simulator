# from fastapi import FastAPI
# from pydantic import BaseModel

# from automata.dfa import DFA, State, Transition
# from automata.simulator import simulate

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from automata.dfa import DFA, State, Transition
from automata.nfa import NFA, State as NFAState, Transition as NFATransition
from automata.simulator import simulate, simulate_nfa

from automata.interpreter import interpret_language
from automata.generator import generate_from_rule

from automata.interpreter import interpret_with_ai


app = FastAPI(title="Automata Lab")

# Cache AI interpretations so repeated descriptions
# do not consume another API request.
interpretation_cache = {}

#ADDED FOR BACKEND ERROR, SAME WITH NEW IMPORT SET
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
########


class SimulationRequest(BaseModel):
    input: str
    automaton: dict


class GenerateRequest(BaseModel):
    description: str

# Example DFA:
# Binary strings ending in "01"
current_dfa = DFA(
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


@app.get("/")
def root():
    return {
        "name": "Automata Lab",
        "status": "running",
    }


# @app.post("/simulate")
# def run_simulation(request: SimulationRequest):
#     try:
#         interpretation = interpret_with_ai(
#             request.description
#         )

#         rule = interpretation["rule"]

#         automaton = generate_from_rule(
#             rule,
#             interpretation["alphabet"],
#         )

#         return simulate(
#             automaton,
#             request.input,
#         )

#     except Exception as error:
#         return {
#             "error": str(error)
#         }

@app.post("/simulate")
def run_simulation(request: SimulationRequest):
    try:
        automaton_data = request.automaton
        automaton_type = automaton_data["type"]

        states = automaton_data["states"]
        alphabet = automaton_data["alphabet"]
        start_state = automaton_data["start_state"]
        transitions = automaton_data["transitions"]

        # ----------------------------------------
        # NFA
        # ----------------------------------------

        if automaton_type == "NFA":
            nfa_states = [
                NFAState(
                    state["id"],
                    state.get("accepting", False),
                )
                for state in states
            ]

            nfa_transitions = [
                NFATransition(
                    transition["from"],
                    transition["symbol"],
                    transition["to"],
                )
                for transition in transitions
            ]

            automaton = NFA(
                states=nfa_states,
                alphabet=alphabet,
                transitions=nfa_transitions,
                start_state=start_state,
            )

            return simulate_nfa(
                automaton,
                request.input,
            )

        # ----------------------------------------
        # DFA
        # ----------------------------------------

        if automaton_type == "DFA":
            dfa_states = [
                State(
                    state["id"],
                    state.get("accepting", False),
                )
                for state in states
            ]

            dfa_transitions = [
                Transition(
                    transition["from"],
                    transition["symbol"],
                    transition["to"],
                )
                for transition in transitions
            ]

            automaton = DFA(
                states=dfa_states,
                alphabet=alphabet,
                transitions=dfa_transitions,
                start_state=start_state,
            )

            return simulate(
                automaton,
                request.input,
            )

        raise ValueError(
            f"Unsupported automaton type: {automaton_type}"
        )

    except Exception as error:
        return {
            "error": str(error)
        }
    
@app.get("/automaton")
def get_automaton():
    return {
        "type": "DFA",
        "language": "Binary strings ending in 01",

        "states": [
            {
                "id": state.id,
                "accepting": state.accepting,
            }
            for state in current_dfa.states.values()
        ],

        "alphabet": current_dfa.alphabet,

        "start_state": current_dfa.start_state,

        "transitions": [
            {
                "from": from_state,
                "symbol": symbol,
                "to": to_state,
            }
            for (from_state, symbol), to_state
            in current_dfa.transitions.items()
        ],
    }   

@app.post("/generate")
def generate(request: GenerateRequest):
    try:
        description = request.description.strip()

        # ----------------------------------------
        # Check cache first
        # ----------------------------------------

        if description in interpretation_cache:
            interpretation = interpretation_cache[description]

        else:
            # ----------------------------------------
            # Ask AI only when not cached
            # ----------------------------------------

            interpretation = interpret_with_ai(
                description
            )

            # Save interpretation for future requests
            interpretation_cache[description] = interpretation

        rule = interpretation["rule"]
        alphabet = interpretation["alphabet"]
        automaton_type = interpretation["automaton_type"]

        if rule["type"] == "unsupported":
            return {
                "error": (
                    "The AI could not convert this language "
                    "into a supported automaton rule."
                )
            }

        # ----------------------------------------
        # Generate automaton
        # ----------------------------------------

        if automaton_type == "NFA":
            from automata.generator import generate_contains_nfa

            if rule["type"] != "contains":
                raise ValueError(
                    f"Unsupported NFA rule: {rule['type']}"
                )

            automaton = generate_contains_nfa(
                alphabet,
                rule["pattern"],
            )

        else:
            automaton = generate_from_rule(
                rule,
                alphabet,
            )

        # ----------------------------------------
        # Return automaton
        # ----------------------------------------

        return {
            "type": automaton_type,
            "language": description,

            "states": [
                {
                    "id": state.id,
                    "accepting": state.accepting,
                }
                for state in automaton.states.values()
            ],

            "alphabet": automaton.alphabet,

            "start_state": automaton.start_state,

            "transitions": [
                {
                    "from": from_state,
                    "symbol": symbol,
                    "to": to_state,
                }
                for (from_state, symbol), destinations
                in automaton.transitions.items()
                for to_state in (
                    destinations
                    if isinstance(destinations, set)
                    else [destinations]
                )
            ],
        }

    except Exception as error:
        error_message = str(error)

        # ----------------------------------------
        # Friendly rate-limit message
        # ----------------------------------------

        if (
            "429" in error_message
            or "rate limit" in error_message.lower()
            or "rate_limit_exceeded" in error_message
        ):
            return {
                "error": (
                    "AI generation is temporarily unavailable "
                    "because the AI request limit has been reached. "
                    "Please try again later."
                )
            }

        return {
            "error": error_message
        }