#!/usr/bin/env python3
"""
Zangbot RAG - Infrastructure Knowledge Base
=============================================
Indexes reference guides into ChromaDB using fastembed (CPU-only, no torch).
No langchain. No GPU. Runs on VPS fine.

Usage:
    python vector-db-init.py                    # index all guides
    python vector-db-init.py --query "How do I reset a Vodia extension?"
"""

import argparse
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

# ── Config ──────────────────────────────────────────────────────────────────
REF_DIR      = Path(__file__).parent.parent / "reference-guides"
DB_PATH      = Path(__file__).parent / "chroma_db"
COL_NAME     = "zangbot_infrastructure"
CHUNK_SIZE   = 800   # characters per chunk
CHUNK_OVERLAP = 100  # overlap between chunks


def load_guides(ref_dir: Path) -> list[dict]:
    """Walk reference-guides/, read every .md, split into overlapping chunks."""
    docs = []
    for md_file in sorted(ref_dir.glob("**/*.md")):
        if md_file.name == "INDEX.md":
            continue
        text = md_file.read_text(encoding="utf-8")
        category = md_file.parent.name
        for i, start in enumerate(range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP)):
            chunk = text[start : start + CHUNK_SIZE]
            if len(chunk) < 50:
                continue
            docs.append({
                "id":       f"{md_file.stem}_chunk{i}",
                "content":  chunk,
                "source":   str(md_file.relative_to(ref_dir.parent)),
                "category": category,
                "file":     md_file.name,
            })
    return docs


def get_collection(db_path: Path):
    """Return persistent ChromaDB collection (creates if missing)."""
    client = chromadb.PersistentClient(path=str(db_path))
    return client.get_or_create_collection(
        name=COL_NAME,
        metadata={"hnsw:space": "cosine"},
        embedding_function=DefaultEmbeddingFunction(),
    )


def index(ref_dir: Path, db_path: Path) -> bool:
    """Load -> embed -> store pipeline."""
    print("Zangbot RAG - Indexing reference guides")
    print(f"   Source : {ref_dir}")
    print(f"   DB     : {db_path}")
    print("-" * 48)

    docs = load_guides(ref_dir)
    if not docs:
        print("No .md files found - check reference-guides path")
        return False
    print(f"   Loaded {len(docs)} chunks")

    collection = get_collection(db_path)

    # Upsert in batches - avoids memory spikes on VPS
    batch_size = 50
    for start in range(0, len(docs), batch_size):
        batch = docs[start : start + batch_size]
        collection.upsert(
            ids=       [d["id"]      for d in batch],
            documents= [d["content"] for d in batch],
            metadatas= [{"source": d["source"], "category": d["category"], "file": d["file"]}
                        for d in batch],
        )
        print(f"   Indexed chunks {start+1}-{start+len(batch)}")

    print("-" * 48)
    print(f"Done - {collection.count()} chunks in ChromaDB at {db_path}")
    return True


def query(question: str, db_path: Path, n: int = 3):
    """Query the RAG - returns top-n relevant chunks."""
    collection = get_collection(db_path)
    results = collection.query(query_texts=[question], n_results=n)

    if not results or not results["documents"][0]:
        print("No results found.")
        return

    print(f"\nQuery: {question}")
    print("=" * 48)
    for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0]), 1):
        print(f"\n[{i}] {meta.get('source', '?')}  (category: {meta.get('category', '?')})")
        print("-" * 40)
        print(doc[:400])
        if len(doc) > 400:
            print("  ...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zangbot RAG")
    parser.add_argument("--query",   "-q", default=None, help="Ask a question")
    parser.add_argument("--ref-dir", default=str(REF_DIR))
    parser.add_argument("--db-path", default=str(DB_PATH))
    parser.add_argument("--results", "-n", type=int, default=3)
    args = parser.parse_args()

    ref = Path(args.ref_dir)
    db  = Path(args.db_path)

    if args.query:
        query(args.query, db, args.results)
    else:
        ok = index(ref, db)
        if ok:
            print("\nRunning test query...")
            query("How do I configure UniFi webhooks?", db)
