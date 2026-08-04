"""AI 383 v4.0 - RAG Engine (Retrieval-Augmented Generation)
Doc tai lieu PDF/TXT/MD/CSV, chia chunk, truy van TF-IDF."""
import hashlib, math, re
from collections import Counter
from agent import database as db
from config import RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP

def load_document(filepath, file_type="txt"):
    content = ""
    if file_type == "pdf":
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(filepath)
            content = "\n".join(page.extract_text() or "" for page in reader.pages)
        except: content = f"[Loi doc PDF: {filepath}]"
    elif file_type == "csv":
        import csv
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            content = "\n".join(",".join(row) for row in reader)
    else:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    return content

def chunk_text(text, chunk_size=None, overlap=None):
    chunk_size = chunk_size or RAG_CHUNK_SIZE
    overlap = overlap or RAG_CHUNK_OVERLAP
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current, current_len = [], [], 0
    for sent in sentences:
        if current_len + len(sent) > chunk_size and current:
            chunks.append(" ".join(current))
            overlap_text = " ".join(current)[-overlap:] if overlap > 0 else ""
            current = [overlap_text] if overlap_text else []
            current_len = len(overlap_text)
        current.append(sent)
        current_len += len(sent)
    if current:
        chunks.append(" ".join(current))
    return chunks

def _tfidf_score(query_terms, doc_terms, all_docs_terms):
    score = 0
    doc_counter = Counter(doc_terms)
    n_docs = len(all_docs_terms)
    for term in query_terms:
        tf = doc_counter.get(term, 0) / max(len(doc_terms), 1)
        df = sum(1 for d in all_docs_terms if term in d)
        idf = math.log((n_docs + 1) / (df + 1)) + 1
        score += tf * idf
    return score

async def ingest_document(filepath, file_type=None):
    if not file_type:
        ext = filepath.rsplit(".", 1)[-1].lower()
        file_type = ext if ext in ("pdf", "csv", "md", "txt") else "txt"
    content = load_document(filepath, file_type)
    if not content.strip():
        return {"status": "error", "message": "Tai lieu trong"}
    doc_hash = hashlib.md5(content.encode()).hexdigest()[:16]
    doc_name = filepath.rsplit("/", 1)[-1] if "/" in filepath else filepath
    chunks = chunk_text(content)
    # Save metadata
    await db.add_document_chunk(document_name=doc_name, chunk_index=-1, chunk_text=f"Metadata: {doc_name}", file_path=filepath, file_type=file_type, doc_hash=doc_hash, total_chunks=len(chunks), is_metadata=True)
    for i, chunk in enumerate(chunks):
        await db.add_document_chunk(document_name=doc_name, chunk_index=i, chunk_text=chunk, file_path=filepath, file_type=file_type, doc_hash=doc_hash, total_chunks=len(chunks))
    return {"status": "success", "message": f"Da doc '{doc_name}': {len(chunks)} doan", "doc_hash": doc_hash, "chunks": len(chunks)}

async def query_documents(query="", top_k=5, document_id=None):
    if not query: return {"status": "error", "message": "Can cau hoi"}
    chunks = await db.get_document_chunks(document_id=document_id)
    if not chunks: return {"status": "error", "message": "Chua co tai lieu nao"}
    query_terms = query.lower().split()
    all_docs_terms = [c["chunk_text"].lower().split() for c in chunks]
    scored = []
    for i, chunk in enumerate(chunks):
        doc_terms = chunk["chunk_text"].lower().split()
        score = _tfidf_score(query_terms, doc_terms, all_docs_terms)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]
    context = "\n---\n".join(c["chunk_text"][:500] for _, c in top)
    return {"status": "success", "query": query, "context": context, "matches": [{"score": round(s, 3), "text": c["chunk_text"][:200], "doc": c["document_name"], "chunk_idx": c["chunk_index"]} for s, c in top]}
