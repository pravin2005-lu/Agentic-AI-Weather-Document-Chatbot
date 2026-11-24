from services.document_store import retrieve_relevant
from services.prompts import DOCUMENT_QA_PROMPT

class DocumentAgent:
    """Retrieves relevant chunks and generates document-grounded answers."""
    def __init__(self, llm):
        self.llm = llm

    def handle(self, question, document_text):
        if not document_text:
            raise ValueError("Upload a PDF or TXT document first.")
        passages = retrieve_relevant(document_text, question)
        context = "\n\n".join(f"[Excerpt {i + 1}]\n{chunk}" for i, chunk in passages)
        answer = self.llm.complete(
            DOCUMENT_QA_PROMPT,
            f"Question: {question}\n\nDocument excerpts:\n{context}"
        )
        sources = ", ".join(f"Excerpt {i + 1}" for i, _ in passages)
        return {"answer": f"{answer}\n\n**Document evidence:** {sources}"}
