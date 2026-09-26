"""
Vodia Bot - Main Application Entry Point
Handles all Vodia PBX automation tasks
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VodiaBot:
    """
    Complete Vodia PBX automation bot.
    
    Provides:
    - Ring group management (create, update, delete)
    - Extension management
    - Webhook receiving
    - Monitoring & health checks
    """
    
    def __init__(
        self,
        vodia_host: str = None,
        vodia_user: str = None,
        vodia_pass: str = None,
        default_domain: str = None
    ):
        """Initialize Vodia Bot with credentials."""
        
        # Get credentials from environment or parameters
        self.host = vodia_host or os.getenv('VODIA_HOST', 'lab.getqts.com')
        self.user = vodia_user or os.getenv('VODIA_USER', 'QTS Lab')
        self.password = vodia_pass or os.getenv('VODIA_PASS')
        self.default_domain = default_domain or os.getenv('VODIA_DOMAIN', 'houseoflaw.clearvoipusa.com')
        
        # API configuration
        self.base_url = f'https://{self.host}/rest'
        self.auth = (self.user, self.password)
        
        # State
        self.session_active = False
        self.last_sync = None
        self.domains_cache = {}
        
        logger.info(f"VodiaBot initialized for {self.host}")
        logger.info(f"Default domain: {self.default_domain}")
    
    def test_connection(self) -> bool:
        """
        Test API connection.
        
        Returns:
            bool: True if connection successful
        """
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        try:
            resp = requests.get(
                f'{self.base_url}/system/domains',
                auth=self.auth,
                verify=False,
                timeout=5
            )
            
            if resp.status_code == 200:
                logger.info(f"✅ Connection successful - {len(resp.json())} domains found")
                self.session_active = True
                return True
            else:
                logger.error(f"❌ Connection failed - HTTP {resp.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connection error: {str(e)}")
            return False
    
    def list_domains(self) -> Dict[str, Any]:
        """
        List all domains (tenants).
        
        Returns:
            dict: Domain mapping {id: {name, display, ...}}
        """
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        try:
            resp = requests.get(
                f'{self.base_url}/system/domains',
                auth=self.auth,
                verify=False,
                timeout=5
            )
            
            if resp.status_code == 200:
                domains = resp.json()
                self.domains_cache = domains
                logger.info(f"Retrieved {len(domains)} domains")
                return domains
            else:
                logger.error(f"Failed to list domains: HTTP {resp.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error listing domains: {str(e)}")
            return {}
    
    def list_extensions(self, domain: str = None) -> Dict[str, Any]:
        """
        List extensions in domain.
        
        Args:
            domain: Domain name (uses default if not specified)
            
        Returns:
            dict: Extension mapping {ext: {name, type, ...}}
        """
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        domain = domain or self.default_domain
        
        try:
            resp = requests.get(
                f'{self.base_url}/domain/{domain}/userlist/extensions',
                auth=self.auth,
                verify=False,
                timeout=5
            )
            
            if resp.status_code == 200:
                extensions = resp.json()
                logger.info(f"Retrieved {len(extensions)} extensions from {domain}")
                return extensions
            else:
                logger.error(f"Failed to list extensions: HTTP {resp.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error listing extensions: {str(e)}")
            return {}
    
    def list_ring_groups(self, domain: str = None) -> Dict[str, Any]:
        """
        List ring groups in domain.
        
        Args:
            domain: Domain name (uses default if not specified)
            
        Returns:
            dict: Ring group mapping {ext: {name, type, ...}}
        """
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        domain = domain or self.default_domain
        
        try:
            resp = requests.get(
                f'{self.base_url}/domain/{domain}/userlist/hunts',
                auth=self.auth,
                verify=False,
                timeout=5
            )
            
            if resp.status_code == 200:
                groups = resp.json()
                logger.info(f"Retrieved {len(groups)} ring groups from {domain}")
                return groups
            else:
                logger.error(f"Failed to list ring groups: HTTP {resp.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error listing ring groups: {str(e)}")
            return {}
    
    def get_account(self, ext: str, domain: str = None) -> Dict[str, Any]:
        """
        Get account/extension details.
        
        Args:
            ext: Extension number
            domain: Domain name (uses default if not specified)
            
        Returns:
            dict: Account details
        """
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        domain = domain or self.default_domain
        
        try:
            resp = requests.get(
                f'{self.base_url}/domain/{domain}/user_settings/{ext}',
                auth=self.auth,
                verify=False,
                timeout=5
            )
            
            if resp.status_code == 200:
                account = resp.json()
                logger.info(f"Retrieved account {ext}")
                return account
            else:
                logger.error(f"Failed to get account {ext}: HTTP {resp.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting account: {str(e)}")
            return {}
    
    def create_ring_group(
        self,
        ring_group_num: str,
        domain: str = None,
        name: str = None,
        **kwargs
    ) -> bool:
        """
        Create a new ring group.
        
        Args:
            ring_group_num: Ring group number (e.g., '199')
            domain: Domain name (uses default if not specified)
            name: Display name (optional)
            **kwargs: Additional parameters
            
        Returns:
            bool: True if successful
        """
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        domain = domain or self.default_domain
        
        try:
            payload = {
                'type': 'hunts',
                'account': ring_group_num,
                **kwargs
            }
            
            resp = requests.post(
                f'{self.base_url}/domain/{domain}/addacc',
                json=payload,
                auth=self.auth,
                verify=False,
                timeout=5
            )
            
            if resp.status_code == 200:
                logger.info(f"✅ Created ring group {ring_group_num} in {domain}")
                return True
            else:
                logger.error(f"Failed to create ring group: HTTP {resp.status_code}")
                logger.error(f"Response: {resp.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating ring group: {str(e)}")
            return False
    
    def update_account(
        self,
        ext: str,
        domain: str = None,
        **kwargs
    ) -> bool:
        """
        Update account settings.
        
        Args:
            ext: Extension number
            domain: Domain name (uses default if not specified)
            **kwargs: Settings to update (e.g., st1_ext='101', st1_dur='20')
            
        Returns:
            bool: True if successful
        """
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        domain = domain or self.default_domain
        
        try:
            resp = requests.put(
                f'{self.base_url}/domain/{domain}/user_settings/{ext}',
                json=kwargs,
                auth=self.auth,
                verify=False,
                timeout=5
            )
            
            if resp.status_code == 200:
                logger.info(f"✅ Updated account {ext}")
                return True
            else:
                logger.error(f"Failed to update account {ext}: HTTP {resp.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating account: {str(e)}")
            return False
    
    def delete_account(
        self,
        ext: str,
        domain: str = None
    ) -> bool:
        """
        Delete account/extension.
        
        Args:
            ext: Extension number
            domain: Domain name (uses default if not specified)
            
        Returns:
            bool: True if successful
        """
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        domain = domain or self.default_domain
        
        try:
            resp = requests.delete(
                f'{self.base_url}/domain/{domain}/addacc/{ext}',
                auth=self.auth,
                verify=False,
                timeout=5
            )
            
            if resp.status_code == 200:
                logger.info(f"✅ Deleted account {ext}")
                return True
            else:
                logger.error(f"Failed to delete account {ext}: HTTP {resp.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting account: {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get bot status for monitoring.
        
        Returns:
            dict: Status information
        """
        return {
            'status': 'running' if self.session_active else 'offline',
            'host': self.host,
            'domain': self.default_domain,
            'timestamp': datetime.now().isoformat(),
            'last_sync': self.last_sync
        }


def main():
    """Main entry point for Vodia Bot."""
    
    logger.info("=" * 80)
    logger.info("VODIA BOT - Initialization")
    logger.info("=" * 80)
    
    # Initialize bot
    bot = VodiaBot()
    
    # Test connection
    if not bot.test_connection():
        logger.error("Cannot connect to Vodia API. Check credentials.")
        return False
    
    # List available domains
    domains = bot.list_domains()
    if domains:
        logger.info(f"Available domains: {list(domains.values())}")
    
    # List extensions in default domain
    extensions = bot.list_extensions()
    if extensions:
        logger.info(f"Extensions: {len(extensions)} found")
    
    # List ring groups in default domain
    groups = bot.list_ring_groups()
    if groups:
        logger.info(f"Ring groups: {len(groups)} found")
    
    logger.info("=" * 80)
    logger.info("Vodia Bot ready for operations")
    logger.info("=" * 80)
    
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
