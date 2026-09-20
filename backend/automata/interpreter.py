import json
import os
import re

from openai import OpenAI


def interpret_with_ai(description: str) -> dict:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    system_prompt = """
You are an expert in formal languages and automata theory.

Convert the user's natural-language description into
a structured automata rule.

Return ONLY valid JSON.

The JSON must have this structure:

{
  "automaton_type": "DFA",
  "alphabet": ["0", "1"],
  "rule": {
    "type": "..."
  }
}

Supported automaton types:

DFA
NFA

Supported rule types:

count_mod:

{
  "type": "count_mod",
  "symbol": "1",
  "modulus": 3,
  "remainder": 0
}

count_exact:

{
  "type": "count_exact",
  "symbol": "1",
  "count": 2
}

starts_with:

{
  "type": "starts_with",
  "prefix": "101"
}

ends_with:

{
  "type": "ends_with",
  "suffix": "01"
}

contains:

{
  "type": "contains",
  "pattern": "101"
}

Examples:

"Binary strings with an even number of 1s"

means:

{
  "automaton_type": "DFA",
  "alphabet": ["0", "1"],
  "rule": {
    "type": "count_mod",
    "symbol": "1",
    "modulus": 2,
    "remainder": 0
  }
}

"Binary strings containing exactly two 1s"

means:

{
  "automaton_type": "DFA",
  "alphabet": ["0", "1"],
  "rule": {
    "type": "count_exact",
    "symbol": "1",
    "count": 2
  }
}

"Binary strings that start with 101"

means:

{
  "automaton_type": "DFA",
  "alphabet": ["0", "1"],
  "rule": {
    "type": "starts_with",
    "prefix": "101"
  }
}

"Binary strings ending in 01"

means:

{
  "automaton_type": "DFA",
  "alphabet": ["0", "1"],
  "rule": {
    "type": "ends_with",
    "suffix": "01"
  }
}

"Binary strings containing 101"

means:

{
  "automaton_type": "NFA",
  "alphabet": ["0", "1"],
  "rule": {
    "type": "contains",
    "pattern": "101"
  }
}

For "contains" rules, use an NFA.

For count_mod, count_exact, starts_with, and ends_with,
use a DFA.

Do not generate transitions.

Do not generate Python code.

Do not provide explanations.

Return only JSON.
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": description,
            },
        ],
    )

    return json.loads(response.output_text)


def interpret_language(description: str) -> dict:
    text = description.strip().lower()

    # ----------------------------------------
    # Alphabet
    # ----------------------------------------

    alphabet = ["0", "1"]

    # ----------------------------------------
    # Count modulo
    # ----------------------------------------

    match = re.search(r"(?:divisible by|multiple of)\s+(\d+)", text)

    if "binary" in text and "1" in text and match:
        return {
            "automaton_type": "DFA",
            "alphabet": alphabet,
            "rule": {
                "type": "count_mod",
                "symbol": "1",
                "modulus": int(match.group(1)),
                "remainder": 0,
            },
        }

    # ----------------------------------------
    # Count exact
    # ----------------------------------------

    match = re.search(r"(?:exactly|equal to)\s+(\d+)\s+1s?", text)

    if "binary" in text and match:
        return {
            "automaton_type": "DFA",
            "alphabet": alphabet,
            "rule": {
                "type": "count_exact",
                "symbol": "1",
                "count": int(match.group(1)),
            },
        }

    # ----------------------------------------
    # Starts with
    # ----------------------------------------

    match = re.search(
        r"(?:starts with|start with|begin with|begins with|beginning with)\s+([01]+)",
        text,
    )

    if match:
        return {
            "automaton_type": "DFA",
            "alphabet": alphabet,
            "rule": {
                "type": "starts_with",
                "prefix": match.group(1),
            },
        }

    # ----------------------------------------
    # Ends with
    # ----------------------------------------

    match = re.search(r"(?:ends with|ending in)\s+([01]+)", text)

    if match:
        return {
            "automaton_type": "DFA",
            "alphabet": alphabet,
            "rule": {
                "type": "ends_with",
                "suffix": match.group(1),
            },
        }

    # ----------------------------------------
    # Contains
    # ----------------------------------------

    match = re.search(r"(?:contains|contain|containing)\s+([01]+)", text)

    if match:
        return {
            "automaton_type": "DFA",
            "alphabet": alphabet,
            "rule": {
                "type": "contains",
                "pattern": match.group(1),
            },
        }

    raise ValueError("I could not interpret this language description.")