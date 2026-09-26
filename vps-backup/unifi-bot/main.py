"""UniFi Bot Service - Main v2 (Site Manager Focus)"""
import os
import logging
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import sqlite3

# Load env
load_dotenv()

app = FastAPI(title="UniFi Bot", version="0.2.0")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
UNIFI_API_KEY = os.getenv("UNIFI_API_KEY")
UNIFI_API_BASE = os.getenv("UNIFI_API_BASE_URL", "https://api.ui.com")
LOG_FILE = os.getenv("BOT_LOG_FILE", "/opt/unifi-bot/bot.log")

# Approval DB
DB_FILE = "/opt/unifi-bot/approvals.db"

def init_db():
    """Initialize approval database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS approvals (
        id TEXT PRIMARY KEY,
        action TEXT NOT NULL,
        site_id TEXT,
        description TEXT,
        status TEXT DEFAULT 'pending',
        requested_at TIMESTAMP,
        approved_at TIMESTAMP,
        approved_by TEXT
    )
    """)
    conn.commit()
    conn.close()

def log_action(action: str, details: dict):
    """Log all actions to file and DB"""
    log_entry = f"[{datetime.now().isoformat()}] {action}: {json.dumps(details)}\n"
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)
    logger.info(f"{action}: {details}")

# Models
class SiteQuery(BaseModel):
    """Query for site info"""
    site_id: str

class ApprovalRequest(BaseModel):
    """Request approval for action"""
    action: str
    site_id: str
    description: str

# Initialize
init_db()

# Endpoints
@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok", "service": "unifi-bot", "version": "0.2.0"}

@app.get("/sites")
def list_sites():
    """List all UniFi sites via Site Manager API"""
    if not UNIFI_API_KEY:
        raise HTTPException(status_code=400, detail="UNIFI_API_KEY not set")
    
    headers = {"X-API-KEY": UNIFI_API_KEY, "Accept": "application/json"}
    
    try:
        resp = requests.get(f"{UNIFI_API_BASE}/v1/sites", headers=headers, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()
        sites = data.get('data', [])
        
        log_action("LIST_SITES", {"count": len(sites), "status": "success"})
        
        return {
            "status": "success",
            "count": len(sites),
            "sites": [
                {
                    "siteId": s['siteId'],
                    "name": s['meta'].get('name', 'Unknown'),
                    "timezone": s['meta'].get('timezone', 'Unknown'),
                    "devices_total": s['statistics']['counts'].get('totalDevice', 0),
                    "wifi_clients": s['statistics']['counts'].get('wifiClient', 0),
                    "wired_clients": s['statistics']['counts'].get('wiredClient', 0)
                }
                for s in sites
            ]
        }
    except Exception as e:
        logger.error(f"Error listing sites: {e}")
        log_action("LIST_SITES", {"status": "error", "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sites/{site_id}")
def get_site(site_id: str):
    """Get detailed info for a site"""
    headers = {"X-API-KEY": UNIFI_API_KEY, "Accept": "application/json"}
    
    try:
        resp = requests.get(f"{UNIFI_API_BASE}/v1/sites", headers=headers, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()
        
        site = next((s for s in data.get('data', []) if s['siteId'] == site_id), None)
        if not site:
            raise HTTPException(status_code=404, detail=f"Site {site_id} not found")
        
        log_action("GET_SITE", {"site_id": site_id, "status": "success"})
        
        return {
            "status": "success",
            "site": {
                "siteId": site['siteId'],
                "name": site['meta'].get('name'),
                "timezone": site['meta'].get('timezone'),
                "gateway_mac": site['meta'].get('gatewayMac'),
                "devices": site['statistics']['counts'],
                "raw": site
            }
        }
    except Exception as e:
        logger.error(f"Error getting site {site_id}: {e}")
        log_action("GET_SITE", {"site_id": site_id, "status": "error", "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/approve")
def request_approval(req: ApprovalRequest):
    """Request approval for an action"""
    import uuid
    approval_id = str(uuid.uuid4())[:8]
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO approvals (id, action, site_id, description, status, requested_at)
    VALUES (?, ?, ?, ?, 'pending', ?)
    """, (approval_id, req.action, req.site_id, req.description, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    log_action("APPROVAL_REQUESTED", {"approval_id": approval_id, "action": req.action, "site_id": req.site_id})
    
    return {
        "status": "pending",
        "approval_id": approval_id,
        "action": req.action,
        "description": req.description,
        "site_id": req.site_id
    }

@app.get("/approvals/{approval_id}")
def get_approval(approval_id: str):
    """Get approval status"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"Approval {approval_id} not found")
    
    return {
        "approval_id": row[0],
        "action": row[1],
        "site_id": row[2],
        "description": row[3],
        "status": row[4],
        "requested_at": row[5]
    }

@app.get("/logs")
def get_logs(lines: int = 50):
    """Get recent bot logs"""
    try:
        with open(LOG_FILE, 'r') as f:
            all_lines = f.readlines()
        recent = all_lines[-lines:]
        return {
            "status": "success",
            "total_lines": len(all_lines),
            "returned": len(recent),
            "logs": recent
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
