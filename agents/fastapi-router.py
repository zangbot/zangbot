#!/usr/bin/env python3
"""
Zangbot Ticket Router: FastAPI + RAG-backed event processor.

Routes infrastructure events (UniFi, Vodia, Hostinger) → LLM decision layer → actions.
No auto-execution: all state changes require user approval.

Webhook endpoints:
  POST /webhook/unifi    - UniFi network events
  POST /webhook/vodia    - Vodia PBX events
  POST /webhook/hostinger - Hostinger system events

Query endpoints:
  POST /query            - RAG-backed question
  GET  /tickets          - List pending decisions
  POST /tickets/{id}/approve - User approval for action
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import json
import uuid
import sys
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Zangbot Router", version="0.2.0")

# In-memory ticket store (upgrade to DB for production)
tickets = {}

# RAG system — loaded once at startup
_rag_collection = None

# Event schemas
class WebhookPayload(BaseModel):
    source: str  # unifi, vodia, hostinger
    event: str
    device_id: Optional[str] = None
    details: dict
    timestamp: Optional[str] = None

class QueryPayload(BaseModel):
    question: str
    context: Optional[dict] = None

class ApprovalPayload(BaseModel):
    approved: bool
    reason: Optional[str] = None


@app.on_event("startup")
async def startup():
    """Initialize RAG system on startup."""
    global _rag_collection
    print("Zangbot Router starting...")
    try:
        import chromadb
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        db_path = Path(__file__).parent.parent / "rag" / "chroma_db"
        if db_path.exists():
            client = chromadb.PersistentClient(path=str(db_path))
            _rag_collection = client.get_or_create_collection(
                name="zangbot_infrastructure",
                metadata={"hnsw:space": "cosine"},
                embedding_function=DefaultEmbeddingFunction(),
            )
            print(f"RAG loaded - {_rag_collection.count()} chunks ready")
        else:
            print(f"RAG db not found at {db_path} - run rag/vector-db-init.py first")
    except Exception as e:
        print(f"RAG init failed (non-fatal): {e}")


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "service": "zangbot-router"}


@app.post("/webhook/unifi")
async def webhook_unifi(payload: WebhookPayload):
    """Handle UniFi network events."""
    print(f"📡 UniFi event: {payload.event}")
    
    # Create ticket for decision
    ticket_id = str(uuid.uuid4())[:8]
    tickets[ticket_id] = {
        "id": ticket_id,
        "source": "unifi",
        "event": payload.event,
        "payload": payload.dict(),
        "created_at": datetime.now().isoformat(),
        "status": "pending_decision",
        "suggested_action": f"[RAG] Analyze UniFi event: {payload.event}",
        "approved": False
    }
    
    return {
        "ticket_id": ticket_id,
        "status": "pending_decision",
        "message": "Event received. Awaiting user approval."
    }


@app.post("/webhook/vodia")
async def webhook_vodia(payload: WebhookPayload):
    """Handle Vodia PBX events."""
    print(f"☎️  Vodia event: {payload.event}")
    
    ticket_id = str(uuid.uuid4())[:8]
    tickets[ticket_id] = {
        "id": ticket_id,
        "source": "vodia",
        "event": payload.event,
        "payload": payload.dict(),
        "created_at": datetime.now().isoformat(),
        "status": "pending_decision",
        "suggested_action": f"[RAG] Analyze Vodia event: {payload.event}",
        "approved": False
    }
    
    return {
        "ticket_id": ticket_id,
        "status": "pending_decision",
        "message": "Event received. Awaiting user approval."
    }


@app.post("/webhook/hostinger")
async def webhook_hostinger(payload: WebhookPayload):
    """Handle Hostinger system events."""
    print(f"🖥️  Hostinger event: {payload.event}")
    
    ticket_id = str(uuid.uuid4())[:8]
    tickets[ticket_id] = {
        "id": ticket_id,
        "source": "hostinger",
        "event": payload.event,
        "payload": payload.dict(),
        "created_at": datetime.now().isoformat(),
        "status": "pending_decision",
        "suggested_action": f"[RAG] Analyze Hostinger event: {payload.event}",
        "approved": False
    }
    
    return {
        "ticket_id": ticket_id,
        "status": "pending_decision",
        "message": "Event received. Awaiting user approval."
    }


@app.post("/query")
async def query_rag(payload: QueryPayload):
    """RAG-backed question about infrastructure."""
    print(f"Query: {payload.question}")

    if _rag_collection is None:
        return {
            "question": payload.question,
            "error": "RAG not loaded - run rag/vector-db-init.py on VPS first",
            "results": []
        }

    results = _rag_collection.query(query_texts=[payload.question], n_results=3)
    formatted = []
    if results and results["documents"][0]:
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            formatted.append({
                "source":   meta.get("source", "unknown"),
                "category": meta.get("category", "unknown"),
                "snippet":  doc[:500],
            })

    return {
        "question": payload.question,
        "results":  formatted,
        "count":    len(formatted),
    }


@app.get("/tickets")
async def list_tickets(status: Optional[str] = None):
    """List pending decision tickets."""
    filtered = tickets.values()
    
    if status:
        filtered = [t for t in filtered if t["status"] == status]
    
    return {
        "count": len(list(filtered)),
        "tickets": list(filtered)
    }


@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Get ticket details."""
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return tickets[ticket_id]


@app.post("/tickets/{ticket_id}/approve")
async def approve_ticket(ticket_id: str, approval: ApprovalPayload):
    """User approves or rejects a decision."""
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket = tickets[ticket_id]
    ticket["approved"] = approval.approved
    ticket["status"] = "approved" if approval.approved else "rejected"
    ticket["approval_reason"] = approval.reason
    ticket["approved_at"] = datetime.now().isoformat()
    
    # TODO: Execute action if approved
    # if approval.approved:
    #     await execute_action(ticket)
    
    return {
        "ticket_id": ticket_id,
        "status": ticket["status"],
        "message": f"Ticket {'approved' if approval.approved else 'rejected'}"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
