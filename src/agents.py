"""
agents.py
---------
Defines the two AI "team members":

  CODER AGENT  -> writes a Python solution for the task
  TESTER AGENT -> writes unit tests for that solution, and later reads
                  test failures to explain what went wrong (bug report)

Both agents are just the same LLM (Groq) given different instructions
("system prompts") — this is what makes them feel like a "team" even
though it's one model wearing two hats.
"""

import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from src.config import GROQ_API_KEY, GROQ_MODEL


def _llm(temperature: float = 0.2):
    return ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=temperature)


def _extract_code(text: str) -> str:
    """Pull code out of a ```python ... ``` block. Falls back to raw text
    if the model didn't wrap it in a code fence."""
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


# --------------------------------------------------------------------
# CODER AGENT
# --------------------------------------------------------------------

_CODER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a careful Python developer (the 'Coder' agent on a small team). "
            "Write a single, complete, self-contained Python solution for the given task. "
            "Rules:\n"
            "- Put the main logic in a function (or a few functions) with clear names.\n"
            "- Add a short docstring explaining what the code does.\n"
            "- No input()/print() side effects unless explicitly asked.\n"
            "- Return ONLY a single Python code block, nothing else.",
        ),
        (
            "human",
            "Task: {task}\n\n"
            "{feedback_section}",
        ),
    ]
)


def write_code(task: str, feedback: str | None = None) -> str:
    """Coder agent: write (or rewrite, using tester feedback) a solution."""
    feedback_section = (
        f"The previous attempt failed testing. Fix it using this feedback from the Tester:\n{feedback}"
        if feedback
        else "This is the first attempt."
    )
    llm = _llm(temperature=0.2)
    chain = _CODER_PROMPT | llm
    result = chain.invoke({"task": task, "feedback_section": feedback_section})
    return _extract_code(result.content)


# --------------------------------------------------------------------
# TESTER AGENT
# --------------------------------------------------------------------

_TEST_WRITER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a meticulous QA engineer (the 'Tester' agent on a small team). "
            "Given a task and a Coder's solution, write a Python test file using the "
            "built-in `unittest` module that thoroughly checks correctness, including "
            "edge cases. Assume the solution file is importable as `solution` "
            "(e.g. `from solution import my_function`). "
            "Return ONLY a single Python code block, nothing else.",
        ),
        (
            "human",
            "Task: {task}\n\nSolution code:\n```python\n{code}\n```",
        ),
    ]
)


def write_tests(task: str, code: str) -> str:
    """Tester agent: generate unit tests for the coder's solution."""
    llm = _llm(temperature=0.2)
    chain = _TEST_WRITER_PROMPT | llm
    result = chain.invoke({"task": task, "code": code})
    return _extract_code(result.content)


_BUG_ANALYST_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the same QA engineer (Tester agent). The tests you wrote just "
            "failed when run. Read the task, the solution, and the raw test output, "
            "then explain CONCISELY (3-5 bullet points max) what is wrong and what the "
            "Coder should change. Be specific and actionable. Do not repeat the whole "
            "code back, just the diagnosis and fix instructions.",
        ),
        (
            "human",
            "Task: {task}\n\n"
            "Solution:\n```python\n{code}\n```\n\n"
            "Test output (stdout+stderr):\n{output}",
        ),
    ]
)


def analyze_failure(task: str, code: str, output: str) -> str:
    """Tester agent: turn a raw test failure/traceback into clear feedback
    for the Coder agent to act on (this is the 'Self-Fixing Loop')."""
    llm = _llm(temperature=0.2)
    chain = _BUG_ANALYST_PROMPT | llm
    result = chain.invoke({"task": task, "code": code, "output": output})
    return result.content.strip()
