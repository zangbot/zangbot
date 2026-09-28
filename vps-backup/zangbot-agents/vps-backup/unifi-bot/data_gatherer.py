"""UniFi Data Gatherer with Llama2 Suggestions"""
import os
import json
import requests
import logging
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class UniFiDataGatherer:
    """Gathers UniFi data and gets Llama suggestions"""
    
    def __init__(self):
        self.api_key = os.getenv("UNIFI_API_KEY")
        self.api_base = os.getenv("UNIFI_API_BASE_URL", "https://api.ui.com")
        self.llama_endpoint = "http://localhost:11434/api/generate"
    
    def get_all_sites(self) -> List[Dict]:
        """Get all sites with full data"""
        headers = {"X-API-KEY": self.api_key, "Accept": "application/json"}
        resp = requests.get(f"{self.api_base}/v1/sites", headers=headers, timeout=10, verify=False)
        resp.raise_for_status()
        return resp.json().get('data', [])
    
    def format_site_data(self, site: Dict) -> str:
        """Format site data for Llama"""
        meta = site.get('meta', {})
        stats = site.get('statistics', {}).get('counts', {})
        
        return f"""
Site: {meta.get('name', 'Unknown')}
ID: {site.get('siteId')}
Location: {meta.get('timezone', 'Unknown')}
Gateway: {meta.get('gatewayMac', 'N/A')}

Current State:
- Total Devices: {stats.get('totalDevice', 0)}
- WiFi APs: {stats.get('wifiDevice', 0)}
- Wired Devices: {stats.get('wiredDevice', 0)}
- WiFi Clients: {stats.get('wifiClient', 0)}
- Wired Clients: {stats.get('wiredClient', 0)}
- Offline Devices: {stats.get('offlineDevice', 0)}
- Pending Updates: {stats.get('pendingUpdateDevice', 0)}
- Critical Notifications: {stats.get('criticalNotification', 0)}

Network Config:
- LAN Configs: {stats.get('lanConfiguration', 0)}
- WAN Configs: {stats.get('wanConfiguration', 0)}
- WiFi Networks: {stats.get('wifiConfiguration', 0)}
"""
    
    def get_llama_suggestion(self, site_data: str, question: str) -> Dict:
        """Get Llama's suggestion on site actions"""
        prompt = f"""{site_data}

Question: {question}

Based on the network state above, provide a brief suggestion (1-2 sentences) and a confidence score (0-1).
Format: SUGGESTION: [text] | CONFIDENCE: [0.0-1.0]"""
        
        try:
            resp = requests.post(
                self.llama_endpoint,
                json={
                    "model": "llama2:7b",
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3
                },
                timeout=30
            )
            resp.raise_for_status()
            response_text = resp.json().get('response', '')
            
            # Parse response
            suggestion = ""
            confidence = 0.0
            
            if "SUGGESTION:" in response_text:
                parts = response_text.split("CONFIDENCE:")
                suggestion = parts[0].replace("SUGGESTION:", "").strip()
                try:
                    confidence = float(parts[1].strip())
                except:
                    confidence = 0.5
            
            return {
                "suggestion": suggestion,
                "confidence": min(1.0, max(0.0, confidence)),
                "raw_response": response_text
            }
        
        except Exception as e:
            logger.error(f"Llama error: {e}")
            return {
                "suggestion": "Llama unavailable",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def gather_and_suggest(self) -> Dict:
        """Gather all data and get suggestions"""
        logger.info("Starting data gathering...")
        
        sites = self.get_all_sites()
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_sites": len(sites),
            "sites": []
        }
        
        for site in sites:
            site_data = self.format_site_data(site)
            
            # Get Llama's suggestion for this site
            question = "Should we provision a guest network or any immediate action needed?"
            suggestion = self.get_llama_suggestion(site_data, question)
            
            summary["sites"].append({
                "site_id": site['siteId'],
                "name": site['meta'].get('name'),
                "formatted_data": site_data,
                "llama_suggestion": suggestion
            })
            
            logger.info(f"✓ Gathered data + suggestion for {site['meta'].get('name')}")
        
        return summary

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gatherer = UniFiDataGatherer()
    
    print("\n=== TESTING DATA GATHERER ===\n")
    data = gatherer.gather_and_suggest()
    print(json.dumps(data, indent=2))
