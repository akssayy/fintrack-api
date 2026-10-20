# DocuMind Lite API

A small backend project for uploading text-based PDFs, extracting text, splitting it into chunks, and retrieving relevant snippets using keyword overlap.

**Honest scope:** this repository is an initial retrieval MVP. It does not currently use embeddings, a vector database, or an LLM to generate answers. Those can be added as follow-up features after this version works.

## Features implemented
- Upload a PDF through a REST endpoint.
- Validate file extension and file size.
- Extract selectable text with `pypdf`.
- Split extracted text into overlapping chunks.
- Retrieve likely relevant chunks using keyword overlap.
- List and delete documents.
- Return clear HTTP errors for invalid files and missing documents.
- Interactive API docs and basic tests.

## Run locally
Python 3.11+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Try it
1. Use `POST /documents` to upload a text-based PDF.
2. Copy the returned document `id`.
3. Use `POST /documents/{document_id}/search` with:
```json
{
  "question": "What does the document say about database security?",
  "top_k": 3
}
```
4. Inspect the returned snippets and compare them with the PDF.

## Limitations
- Documents are stored in memory and disappear when the server restarts.
- Scanned PDFs do not work without OCR.
- Retrieval uses simple keyword overlap, not semantic embeddings.
- It returns snippets, not a generated LLM answer.
- This is a local learning project, not a production document service.

## Suggested next improvements
- Persist documents and chunks in a database.
- Add user authentication and per-user document access.
- Add OCR for scanned PDFs.
- Replace keyword overlap with embedding-based semantic retrieval.
- Add an optional LLM answer endpoint with citations to retrieved snippets.
- Add tests for uploads, search, deletion, and malformed PDFs.
