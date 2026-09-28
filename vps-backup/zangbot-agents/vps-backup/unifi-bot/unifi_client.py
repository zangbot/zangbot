"""UniFi API Client - handles both Site Manager and Local Network APIs"""
import os
import requests
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class UniFiClient:
    """Client for UniFi APIs"""
    
    def __init__(self):
        self.site_manager_base = os.getenv("UNIFI_API_BASE_URL", "https://api.ui.com")
        self.api_key = os.getenv("UNIFI_API_KEY")
        self.local_controller = os.getenv("UNIFI_LOCAL_CONTROLLER_URL", "https://192.168.5.1")
        self.username = os.getenv("UNIFI_USERNAME")
        self.password = os.getenv("UNIFI_PASSWORD")
        self.local_token = None
        
    def get_site_manager_headers(self) -> Dict:
        """Headers for Site Manager API"""
        return {
            "X-API-KEY": self.api_key,
            "Accept": "application/json"
        }
    
    def list_sites(self) -> List[Dict]:
        """List all sites via Site Manager API"""
        try:
            url = f"{self.site_manager_base}/v1/sites"
            resp = requests.get(url, headers=self.get_site_manager_headers(), timeout=10, verify=False)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"✓ Listed {len(data.get('data', []))} sites")
            return data.get('data', [])
        except Exception as e:
            logger.error(f"✗ Error listing sites: {e}")
            raise
    
    def login_local(self) -> bool:
        """Login to local controller and get token"""
        try:
            url = f"{self.local_controller}/api/auth/login"
            payload = {
                "username": self.username,
                "password": self.password
            }
            resp = requests.post(url, json=payload, timeout=10, verify=False)
            resp.raise_for_status()
            data = resp.json()
            self.local_token = data.get('data', {}).get('sessionId') or data.get('sessionId')
            if self.local_token:
                logger.info(f"✓ Local controller login successful")
                return True
            else:
                logger.error(f"✗ No session token in response: {data}")
                return False
        except Exception as e:
            logger.error(f"✗ Local controller login failed: {e}")
            return False
    
    def get_local_devices(self, site_id: str = "default") -> List[Dict]:
        """Get devices from local controller"""
        if not self.local_token:
            if not self.login_local():
                return []
        
        try:
            url = f"{self.local_controller}/api/v2/sites/{site_id}/devices"
            headers = {
                "X-CSRF-TOKEN": self.local_token,
                "Accept": "application/json"
            }
            resp = requests.get(url, headers=headers, timeout=10, verify=False)
            resp.raise_for_status()
            data = resp.json()
            devices = data.get('data', [])
            logger.info(f"✓ Retrieved {len(devices)} devices from {site_id}")
            return devices
        except Exception as e:
            logger.error(f"✗ Error getting devices: {e}")
            return []
    
    def get_local_networks(self, site_id: str = "default") -> List[Dict]:
        """Get networks from local controller"""
        if not self.local_token:
            if not self.login_local():
                return []
        
        try:
            url = f"{self.local_controller}/api/v2/sites/{site_id}/networks"
            headers = {
                "X-CSRF-TOKEN": self.local_token,
                "Accept": "application/json"
            }
            resp = requests.get(url, headers=headers, timeout=10, verify=False)
            resp.raise_for_status()
            data = resp.json()
            networks = data.get('data', [])
            logger.info(f"✓ Retrieved {len(networks)} networks from {site_id}")
            return networks
        except Exception as e:
            logger.error(f"✗ Error getting networks: {e}")
            return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = UniFiClient()
    
    print("\n=== TESTING UniFiClient ===\n")
    
    # Test 1: Site Manager
    print("[1] Testing Site Manager API...")
    try:
        sites = client.list_sites()
        print(f"✓ Found {len(sites)} site(s)")
        for site in sites:
            print(f"  - {site['meta']['name']} (ID: {site['siteId']})")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 2: Local Controller Login
    print("\n[2] Testing Local Controller Login...")
    if client.login_local():
        print(f"✓ Authenticated to {client.local_controller}")
    else:
        print(f"✗ Authentication failed")
    
    # Test 3: Local Devices
    print("\n[3] Testing Local Device Fetch...")
    devices = client.get_local_devices("default")
    if devices:
        print(f"✓ Retrieved {len(devices)} device(s):")
        for dev in devices[:3]:  # Show first 3
            print(f"  - {dev.get('name', 'N/A')} ({dev.get('type', 'N/A')})")
    else:
        print(f"✗ No devices or connection failed")
    
    # Test 4: Local Networks
    print("\n[4] Testing Local Network Fetch...")
    networks = client.get_local_networks("default")
    if networks:
        print(f"✓ Retrieved {len(networks)} network(s):")
        for net in networks[:3]:  # Show first 3
            print(f"  - {net.get('name', 'N/A')} ({net.get('networktype', 'N/A')})")
    else:
        print(f"✗ No networks or connection failed")
    
    print("\n=== END TESTS ===\n")
