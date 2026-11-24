import json
from services.prompts import ROUTER_PROMPT

class AgentRouter:
    """LLM-based router. It selects one of the two required specialized agents."""
    def __init__(self, llm):
        self.llm = llm

    def route(self, question, document_available):
        raw = self.llm.complete(
            ROUTER_PROMPT,
            f"Document uploaded: {document_available}\nUser request: {question}"
        )
        try:
            data = json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
        except Exception as exc:
            raise ValueError(f"Router returned invalid JSON: {raw}") from exc
        agent = data.get("agent")
        if agent not in ("weather", "document"):
            raise ValueError("Router must select either 'weather' or 'document'.")
        if agent == "document" and not document_available:
            raise ValueError("Please upload a PDF or TXT document before asking document questions.")
        task = data.get("task", "current")
        if task not in ("current", "forecast", "historical", "last_10_days"):
            task = "current"
        return {
            "agent": agent,
            "task": task,
            "location": data.get("location") or "Chennai",
            "date": data.get("date"),
            "visualization": data.get("visualization", "table"),
            "original_question": question,
        }
