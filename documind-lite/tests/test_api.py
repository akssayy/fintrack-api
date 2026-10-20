from fastapi.testclient import TestClient
from app.main import app, chunk_text, score_chunk, documents

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_chunk_text():
    chunks = chunk_text("backend api database " * 100, chunk_size=100, overlap=10)
    assert len(chunks) > 1
    assert all(chunks)

def test_keyword_retrieval_score():
    assert score_chunk("database schema", "The database schema defines tables") >= 1

def test_reject_non_pdf():
    response = client.post(
        "/documents",
        files={"file": ("notes.txt", b"not a pdf", "text/plain")}
    )
    assert response.status_code == 400
