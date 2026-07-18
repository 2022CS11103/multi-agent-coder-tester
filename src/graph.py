"""
graph.py
--------
Wires the Coder agent, Tester agent, human approval gate, and sandboxed
execution into one LangGraph workflow.

Flow:

    write_code (Coder)
         |
    human_approval  <-- pauses and waits for you to type "yes"/"no"
         |
    write_tests (Tester)
         |
    execute_in_sandbox (Docker)
         |
     passed? ----yes----> DONE
         |
         no
         |
    analyze_failure (Tester explains the bug)
         |
    back to write_code (Coder tries again, using feedback)
      ... up to MAX_ITERATIONS times
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from src.config import MAX_ITERATIONS, GENERATED_DIR
from src.agents import write_code, write_tests, analyze_failure
from src.sandbox import run_in_docker, save_final_files


class TeamState(TypedDict):
    task: str
    code: str
    test_code: str
    feedback: Optional[str]
    iteration: int
    passed: bool
    last_output: str
    aborted: bool


def node_coder(state: TeamState) -> TeamState:
    print(f"\n🧑‍💻 Coder agent is writing a solution (attempt {state['iteration'] + 1})...")
    code = write_code(state["task"], feedback=state.get("feedback"))
    print("\n--- Coder's solution ---\n")
    print(code)
    return {**state, "code": code, "iteration": state["iteration"] + 1}


def node_human_approval(state: TeamState) -> TeamState:
    print("\n🙋 HUMAN APPROVAL NEEDED (Human-in-the-loop safety gate)")
    answer = input("Run this code in a sandboxed Docker container to test it? [y/n]: ").strip().lower()
    if answer != "y":
        print("❌ Human rejected running this code. Stopping.")
        return {**state, "aborted": True}
    return state


def node_tester_writes_tests(state: TeamState) -> TeamState:
    print("\n🧪 Tester agent is writing unit tests...")
    test_code = write_tests(state["task"], state["code"])
    print("\n--- Tester's tests ---\n")
    print(test_code)
    return {**state, "test_code": test_code}


def node_execute(state: TeamState) -> TeamState:
    print("\n🐳 Running tests inside a sandboxed Docker container...")
    result = run_in_docker(state["code"], state["test_code"])
    print("\n--- Test output ---\n")
    print(result["output"])
    return {**state, "passed": result["passed"], "last_output": result["output"]}


def node_analyze_failure(state: TeamState) -> TeamState:
    print("\n🔍 Tester agent is diagnosing the failure...")
    feedback = analyze_failure(state["task"], state["code"], state["last_output"])
    print("\n--- Tester's feedback to Coder ---\n")
    print(feedback)
    return {**state, "feedback": feedback}


def route_after_approval(state: TeamState) -> str:
    return "aborted" if state.get("aborted") else "continue"


def route_after_execute(state: TeamState) -> str:
    if state["passed"]:
        return "done"
    if state["iteration"] >= MAX_ITERATIONS:
        return "give_up"
    return "retry"


def build_graph():
    graph = StateGraph(TeamState)

    graph.add_node("coder", node_coder)
    graph.add_node("human_approval", node_human_approval)
    graph.add_node("tester_writes_tests", node_tester_writes_tests)
    graph.add_node("execute", node_execute)
    graph.add_node("analyze_failure", node_analyze_failure)

    graph.set_entry_point("coder")
    graph.add_edge("coder", "human_approval")

    graph.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {"continue": "tester_writes_tests", "aborted": END},
    )

    graph.add_edge("tester_writes_tests", "execute")

    graph.add_conditional_edges(
        "execute",
        route_after_execute,
        {"done": END, "retry": "analyze_failure", "give_up": END},
    )

    graph.add_edge("analyze_failure", "coder")

    return graph.compile()


def run_team(task: str):
    app = build_graph()
    initial_state: TeamState = {
        "task": task,
        "code": "",
        "test_code": "",
        "feedback": None,
        "iteration": 0,
        "passed": False,
        "last_output": "",
        "aborted": False,
    }
    final_state = app.invoke(initial_state, config={"recursion_limit": 50})

    print("\n" + "=" * 60)
    if final_state.get("aborted"):
        print("🛑 Run stopped by human — nothing was saved.")
    elif final_state["passed"]:
        print(f"✅ Tests passed after {final_state['iteration']} attempt(s)!")
        save_final_files(final_state["code"], final_state["test_code"], GENERATED_DIR)
        print(f"📁 Saved solution.py and test_solution.py to ./{GENERATED_DIR}/")
    else:
        print(f"⚠️ Gave up after {final_state['iteration']} attempts — tests still failing.")
        save_final_files(final_state["code"], final_state["test_code"], GENERATED_DIR)
        print(f"📁 Saved the last attempt to ./{GENERATED_DIR}/ for you to review manually.")
    print("=" * 60)

    return final_state
