from typing import TypedDict, Optional


class AgentState(TypedDict):
    user_story: str
    language: str
    code: str
    feedback: str
    test_report: str
    iterations: int
    is_passing: bool
    file_path: Optional[str]
