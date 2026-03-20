import os
import subprocess
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState

# Initialize LLM
llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0)


def coder_node(state: AgentState):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert {language} developer. Respond ONLY with the code block.",
            ),
            (
                "user",
                "User Story: {user_story}\nCurrent Code: {code}\nReviewer Feedback: {feedback}\nUnit Test Errors: {test_report}\n\nProvide the complete updated code inside triple backticks.",
            ),
        ]
    )

    input_data = {
        "user_story": state.get("user_story", ""),
        "language": state.get("language", "python"),
        "code": state.get("code", "No code written yet."),
        "feedback": state.get("feedback", "No feedback yet."),
        "test_report": state.get("test_report", "No errors yet."),
    }

    response = (prompt | llm).invoke(input_data)
    content = response.content

    # Extraction logic
    if "```" in content:
        code_block = content.split("```")[1]
        lang_tag = state["language"].lower()
        if code_block.lower().startswith(lang_tag):
            code_block = code_block[len(lang_tag) :].strip()
        else:
            code_block = code_block.strip()
    else:
        code_block = content.strip()

    return {
        "code": code_block,
        "iterations": state.get("iterations", 0) + 1,
        "feedback": "",
        "test_report": "",
    }


def reviewer_node(state: AgentState):
    prompt = ChatPromptTemplate.from_template(
        "Review this {language} code:\n{code}\n\nRequirement: {user_story}\nIf it is correct, reply 'PASSED'. If not, explain what to fix."
    )
    res = (prompt | llm).invoke(state).content
    return {"feedback": "" if "PASSED" in res.upper() else res}


def unit_tester_node(state: AgentState):
    if state["language"].lower() != "python":
        return {"is_passing": True, "test_report": "Skipping execution for non-python."}

    file_name = "temp_verify.py"
    with open(file_name, "w") as f:
        f.write(state["code"])

    try:
        result = subprocess.run(
            ["python3", file_name], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return {"is_passing": True, "test_report": "Execution Successful"}
        return {"is_passing": False, "test_report": result.stderr}
    except Exception as e:
        return {"is_passing": False, "test_report": str(e)}
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)


def file_saver_node(state: AgentState):
    extension_map = {
        "python": "py",
        "java": "java",
        "go": "go",
        "node": "js",
        "rust": "rs",
        "sql": "sql",
    }
    lang = state["language"].lower()
    ext = extension_map.get(lang, "txt")
    fname = f"final_script.{ext}"

    with open(fname, "w") as f:
        f.write(state["code"])
    print(f"\n✅ Success! Code saved to {fname}")
    return {"file_path": fname}
