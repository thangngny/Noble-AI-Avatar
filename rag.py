"""
RAG pipeline cho LiveTalking
- Extract text từ PDF bằng pymupdf
- Embed bằng Ollama (all-minilm) 
- Lưu/query ChromaDB
"""
import os
import re
import chromadb
from chromadb.config import Settings

# ── Cấu hình ────────────────────────────────────────────────────────────────
PDF_PATH = os.path.join(os.path.dirname(__file__), "Dự án.pdf")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "du_an"
EMBED_MODEL = "all-minilm"   # Ollama embedding model (đã có sẵn)
CHUNK_SIZE = 400              # ký tự mỗi chunk
CHUNK_OVERLAP = 60
TOP_K = 4                     # số đoạn trả về khi truy vấn

# ── ChromaDB client (singleton) ──────────────────────────────────────────────
_client = None
_collection = None

def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    _client = chromadb.PersistentClient(path=CHROMA_DIR)
    _collection = _client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


# ── Embedding qua Ollama ─────────────────────────────────────────────────────
def _embed(texts: list[str]) -> list[list[float]]:
    import ollama
    embeddings = []
    for text in texts:
        resp = ollama.embeddings(model=EMBED_MODEL, prompt=text)
        embeddings.append(resp["embedding"])
    return embeddings


# ── Chunk văn bản ────────────────────────────────────────────────────────────
def _chunk_text(text: str) -> list[str]:
    # Chia theo lượng ký tự cố định để đảm bảo max CHUNK_SIZE và an toàn
    chunks = []
    text_length = len(text)
    stride = CHUNK_SIZE - CHUNK_OVERLAP
    if stride <= 0:
        stride = CHUNK_SIZE

    start = 0
    while start < text_length:
        end = min(start + CHUNK_SIZE, text_length)
        chunk = text[start:end].strip()
        if len(chunk) > 10:  # bỏ qua chunk quá ngắn
            chunks.append(chunk)
        start += stride

    return chunks


# ── Build index từ du_an_content.py ──────────────────────────────────────────
def build_index():
    """Load nội dung dự án → chunk → embed → lưu vào ChromaDB"""
    from du_an_content import DU_AN_TEXT
    col = _get_collection()

    clean_text = DU_AN_TEXT.strip()
    chunks = _chunk_text(clean_text)
    print(f"[RAG] Tổng {len(chunks)} chunks từ nội dung dự án")

    # Embed và lưu theo batch
    batch = 16
    for i in range(0, len(chunks), batch):
        batch_chunks = chunks[i:i + batch]
        embeddings = _embed(batch_chunks)
        ids = [f"chunk_{i + j}" for j in range(len(batch_chunks))]
        col.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=batch_chunks,
        )
        print(f"[RAG] Indexed {min(i + batch, len(chunks))}/{len(chunks)} chunks")

    print("[RAG] Index built thành công!")


# ── Truy vấn context ─────────────────────────────────────────────────────────
def retrieve_context(query: str, n: int = TOP_K) -> str:
    """Trả về đoạn text liên quan nhất từ PDF để đưa vào prompt LLM"""
    col = _get_collection()
    if col.count() == 0:
        return ""  # Chưa có index

    query_emb = _embed([query])[0]
    results = col.query(
        query_embeddings=[query_emb],
        n_results=min(n, col.count()),
    )
    docs = results.get("documents", [[]])[0]
    return "\n---\n".join(docs)


# ── Main: chạy trực tiếp để build index ─────────────────────────────────────
if __name__ == "__main__":
    build_index()
