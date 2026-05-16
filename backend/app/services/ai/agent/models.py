from pydantic import BaseModel, Field


class AgentStep(BaseModel):
    step_type: str = Field(description="tool | thought")
    tool_name: str | None = None
    input: dict | None = None
    output: str | None = None


class AgentResult(BaseModel):
    answer: str
    message: str
    model: str
    mode: str = "standard"
    steps: list[AgentStep] = Field(default_factory=list)
    character_id: str | None = None
    context_used: bool = False
