#!/usr/bin/env python3
"""
Initialize Zangbot RAG vector database.

Indexes reference guides into a vector store for LLM-backed queries.
Supports: Chroma, Pinecone, FAISS

Phase 1: Load reference guides from disk
Phase 2: Embed with local Mistral or OpenAI API
Phase 3: Store in vector DB
Phase 4: Query via RAG agent
"""

import os
import json
from pathlib import Path
from typing import Optional

# Vector DB options (install as needed)
try:
    import chromadb
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False

try:
    from langchain.document_loaders import DirectoryLoader
    from langchain.text_splitter import MarkdownHeaderTextSplitter
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False


class ZangbotRAG:
    """RAG system for Zangbot infrastructure knowledge."""
    
    def __init__(self, ref_dir: str = "../reference-guides", db_path: str = "./chroma_db"):
        """
        Args:
            ref_dir: Path to reference guides
            db_path: Path to Chroma vector DB
        """
        self.ref_dir = Path(ref_dir)
        self.db_path = db_path
        self.client = None
        self.collection = None
        
    def load_references(self) -> list[dict]:
        """Load reference guides from disk."""
        docs = []
        
        if not self.ref_dir.exists():
            print(f"Reference directory not found: {self.ref_dir}")
            return docs
            
        for guide_file in self.ref_dir.glob("**/*.md"):
            if guide_file.name == "INDEX.md":
                continue
                
            with open(guide_file, 'r') as f:
                content = f.read()
                docs.append({
                    "id": guide_file.stem,
                    "source": str(guide_file),
                    "category": guide_file.parent.name,
                    "content": content
                })
        
        print(f"Loaded {len(docs)} reference guides")
        return docs
    
    def initialize_chroma(self):
        """Initialize Chroma vector DB."""
        if not HAS_CHROMA:
            print("ERROR: Chroma not installed. Run: pip install chromadb")
            return False
        
        # Create persistent client
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="zangbot_infrastructure",
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"Initialized Chroma DB at {self.db_path}")
        return True
    
    def index_documents(self, docs: list[dict]) -> bool:
        """Add documents to vector store."""
        if not self.collection:
            print("ERROR: Vector DB not initialized")
            return False
        
        # For now, store metadata + raw content
        # Full embedding happens when we wire up LLM backend
        for doc in docs:
            try:
                self.collection.add(
                    ids=[doc["id"]],
                    documents=[doc["content"]],
                    metadatas=[{
                        "source": doc["source"],
                        "category": doc["category"]
                    }]
                )
            except Exception as e:
                print(f"Failed to index {doc['id']}: {e}")
                return False
        
        print(f"Indexed {len(docs)} documents in vector store")
        return True
    
    def query(self, query: str, n_results: int = 3) -> list[dict]:
        """Query the RAG system."""
        if not self.collection:
            return []
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        formatted = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                })
        
        return formatted
    
    def run(self) -> bool:
        """Full pipeline: load → index → ready."""
        print("🚀 Zangbot RAG Initialization")
        print("-" * 40)
        
        # Step 1: Load references
        docs = self.load_references()
        if not docs:
            print("No references to index")
            return False
        
        # Step 2: Initialize vector DB
        if not self.initialize_chroma():
            return False
        
        # Step 3: Index documents
        if not self.index_documents(docs):
            return False
        
        print("-" * 40)
        print("✓ RAG system ready")
        print(f"Query example: rag.query('How do I configure UniFi VLAN?')")
        return True


if __name__ == "__main__":
    rag = ZangbotRAG()
    success = rag.run()
    
    if success:
        # Test query
        print("\n📖 Test Query")
        results = rag.query("How do I reset a Vodia extension?")
        for i, result in enumerate(results, 1):
            source = result["metadata"].get("source", "unknown")
            print(f"\n  [{i}] {source}")
            print(f"      {result['content'][:200]}...")
