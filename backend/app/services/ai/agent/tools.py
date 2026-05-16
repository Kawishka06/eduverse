"""Tool registry for the EduVerse Learning Agent."""

from __future__ import annotations

import ast
import operator
from typing import Any, Callable, Awaitable

import httpx

from app.config import Settings

# Safe math operators for calculator
_SAFE_OPS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_math(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        left = _eval_math(node.left)
        right = _eval_math(node.right)
        return float(_SAFE_OPS[op_type](left, right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return float(_SAFE_OPS[op_type](_eval_math(node.operand)))
    raise ValueError("Only numeric expressions are allowed")


def run_calculator(expression: str) -> str:
    expr = expression.strip()
    if not expr:
        return "Error: empty expression"
    try:
        tree = ast.parse(expr, mode="eval")
        result = _eval_math(tree.body)
        if result == int(result):
            return str(int(result))
        return str(round(result, 10))
    except Exception as exc:
        return f"Error: {exc}"


def run_code_helper(code: str, language: str = "python", question: str | None = None) -> str:
    code = code.strip()
    if not code:
        return "Error: no code provided"
    lang = (language or "python").strip().lower()
    lines = len(code.splitlines())
    q = question.strip() if question else "Explain what this code does and any issues."
    return (
        f"[Code review · {lang} · {lines} lines — not executed]\n"
        f"Question: {q}\n\n"
        f"```{lang}\n{code[:4000]}\n```\n\n"
        "The agent will analyze this snippet in its reply. "
        "Common checks: logic, edge cases, readability, and expected output."
    )


async def run_search(query: str, settings: Settings) -> str:
    q = query.strip()
    if not q:
        return "Error: empty search query"

    if not settings.search_live:
        return (
            f"[MOCK Search] Top results for “{q}”:\n"
            "1. EduVerse mock — add TAVILY_API_KEY or SERPER_API_KEY to backend/.env for live search.\n"
            "2. Use textbooks and class materials for verified facts."
        )

    provider = (settings.search_provider or "tavily").lower()
    try:
        if provider == "serper":
            return await _search_serper(q, settings.search_api_key)
        return await _search_tavily(q, settings.search_api_key)
    except Exception as exc:
        return f"Search failed: {exc}"


async def _search_tavily(query: str, api_key: str) -> str:
    async with httpx.AsyncClient(timeout=20.0) as client:
        res = await client.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": 5},
        )
        res.raise_for_status()
        data = res.json()
    results = data.get("results") or []
    if not results:
        return f"No results for: {query}"
    lines = []
    for i, item in enumerate(results[:5], 1):
        title = item.get("title", "Untitled")
        snippet = (item.get("content") or item.get("snippet") or "")[:300]
        url = item.get("url", "")
        lines.append(f"{i}. {title}\n   {snippet}\n   {url}")
    return "\n\n".join(lines)


async def _search_serper(query: str, api_key: str) -> str:
    async with httpx.AsyncClient(timeout=20.0) as client:
        res = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query},
        )
        res.raise_for_status()
        data = res.json()
    organic = data.get("organic") or []
    if not organic:
        return f"No results for: {query}"
    lines = []
    for i, item in enumerate(organic[:5], 1):
        title = item.get("title", "Untitled")
        snippet = (item.get("snippet") or "")[:300]
        url = item.get("link", "")
        lines.append(f"{i}. {title}\n   {snippet}\n   {url}")
    return "\n\n".join(lines)


ToolHandler = Callable[..., Awaitable[str] | str]


class ToolRegistry:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def execute(self, name: str, tool_input: dict[str, Any]) -> str:
        name = name.strip().lower()
        if name == "calculator":
            return run_calculator(str(tool_input.get("expression", "")))
        if name == "code_helper":
            return run_code_helper(
                str(tool_input.get("code", "")),
                str(tool_input.get("language", "python")),
                tool_input.get("question"),
            )
        if name == "search":
            return await run_search(str(tool_input.get("query", "")), self.settings)
        return f"Unknown tool: {name}"
