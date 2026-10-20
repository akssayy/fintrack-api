from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from pypdf import PdfReader
from io import BytesIO
import re

app = FastAPI(
    title="DocuMind Lite API",
    description="PDF text extraction and keyword-based retrieval API. This version does not call an LLM.",
    version="1.0.0",
)

# In-memory store for a simple local demo. Restarting the app clears uploaded documents.
documents: dict[str, dict] = {}
MAX_FILE_BYTES = 8 * 1024 * 1024

class SearchRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks

def score_chunk(question: str, chunk: str) -> int:
    words = {w.lower() for w in re.findall(r"\b[a-zA-Z0-9]{3,}\b", question)}
    chunk_words = {w.lower() for w in re.findall(r"\b[a-zA-Z0-9]{3,}\b", chunk)}
    return len(words & chunk_words)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/documents")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")
    raw = await file.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="PDF must be 8 MB or smaller")
    try:
        reader = PdfReader(BytesIO(raw))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read this PDF") from exc
    if not text:
        raise HTTPException(status_code=422, detail="No extractable text found; scanned PDFs need OCR")
    doc_id = str(uuid4())
    chunks = chunk_text(text)
    documents[doc_id] = {
        "id": doc_id,
        "filename": Path(file.filename).name,
        "page_count": len(reader.pages),
        "character_count": len(text),
        "chunks": chunks,
    }
    return {
        "id": doc_id,
        "filename": Path(file.filename).name,
        "page_count": len(reader.pages),
        "character_count": len(text),
        "chunk_count": len(chunks),
    }

@app.get("/documents")
def list_documents():
    return [
        {key: value for key, value in doc.items() if key != "chunks"}
        for doc in documents.values()
    ]

@app.post("/documents/{document_id}/search")
def search_document(document_id: str, payload: SearchRequest):
    doc = documents.get(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    ranked = [
        {"score": score_chunk(payload.question, chunk), "text": chunk}
        for chunk in doc["chunks"]
    ]
    ranked.sort(key=lambda item: item["score"], reverse=True)
    matches = [item for item in ranked[:payload.top_k] if item["score"] > 0]
    return {
        "document_id": document_id,
        "question": payload.question,
        "retrieval_method": "keyword_overlap",
        "matches": matches,
        "note": "This MVP retrieves relevant text snippets; it does not generate an LLM answer."
    }

@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    if documents.pop(document_id, None) is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True, "document_id": document_id}
