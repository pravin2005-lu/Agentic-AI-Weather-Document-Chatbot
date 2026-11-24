from io import BytesIO
from pypdf import PdfReader

def extract_text(filename, content):
    if filename.lower().endswith(".txt"):
        text = content.decode("utf-8", errors="replace")
    elif filename.lower().endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        raise ValueError("Only PDF and TXT files are supported.")
    if not text.strip():
        raise ValueError("No readable text found. The PDF may be scanned; OCR is not included.")
    return text

def chunk_text(text, chunk_size=1100, overlap=180):
    text = " ".join(text.split())
    chunks, start = [], 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks

def retrieve_relevant(text, question, top_k=4):
    chunks = chunk_text(text)
    terms = {w.lower().strip(".,?!:;()[]") for w in question.split() if len(w) > 2}
    scored = []
    for index, chunk in enumerate(chunks):
        words = set(w.lower().strip(".,?!:;()[]") for w in chunk.split())
        score = len(terms & words)
        scored.append((score, index, chunk))
    scored.sort(reverse=True)
    selected = [(i, c) for score, i, c in scored[:top_k] if score > 0]
    return selected or [(i, c) for i, c in enumerate(chunks[:2])]
