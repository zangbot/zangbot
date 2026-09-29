"""UniFi Security Auditor - Data Collection Only"""
import os
import json
import requests
import logging
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class UniFiSecurityAuditor:
    """Collects site data and runs security audits"""
    
    def __init__(self):
        self.api_key = os.getenv("UNIFI_API_KEY")
        self.api_base = os.getenv("UNIFI_API_BASE_URL", "https://api.ui.com")
    
    def get_all_sites(self) -> List[Dict]:
        """Fetch all sites"""
        headers = {"X-API-KEY": self.api_key, "Accept": "application/json"}
        resp = requests.get(f"{self.api_base}/v1/sites", headers=headers, timeout=10, verify=False)
        resp.raise_for_status()
        return resp.json().get('data', [])
    
    def audit_site_security(self, site: Dict) -> Dict:
        """Run security audit on a site"""
        meta = site.get('meta', {})
        stats = site.get('statistics', {}).get('counts', {})
        
        audit = {
            "site_id": site.get('siteId'),
            "site_name": meta.get('name', 'Unknown'),
            "location": meta.get('timezone', 'Unknown'),
            "gateway_mac": meta.get('gatewayMac', 'N/A'),
            "audit_timestamp": datetime.now().isoformat(),
            "device_inventory": {
                "total_devices": stats.get('totalDevice', 0),
                "wifi_aps": stats.get('wifiDevice', 0),
                "wired_devices": stats.get('wiredDevice', 0),
                "gateway_devices": stats.get('gatewayDevice', 0),
            },
            "client_inventory": {
                "wifi_clients": stats.get('wifiClient', 0),
                "wired_clients": stats.get('wiredClient', 0),
                "guest_clients": stats.get('guestClient', 0),
                "total_clients": stats.get('wifiClient', 0) + stats.get('wiredClient', 0)
            },
            "network_config": {
                "lan_configurations": stats.get('lanConfiguration', 0),
                "wan_configurations": stats.get('wanConfiguration', 0),
                "wifi_networks": stats.get('wifiConfiguration', 0),
            },
            "health_status": {
                "offline_devices": stats.get('offlineDevice', 0),
                "offline_wifi_devices": stats.get('offlineWifiDevice', 0),
                "offline_wired_devices": stats.get('offlineWiredDevice', 0),
                "offline_gateway": stats.get('offlineGatewayDevice', 0),
                "pending_updates": stats.get('pendingUpdateDevice', 0),
                "critical_notifications": stats.get('criticalNotification', 0),
            },
            "security_findings": [],
            "recommendations": []
        }
        
        # Run security checks
        self._run_security_checks(audit, stats)
        
        return audit
    
    def _run_security_checks(self, audit: Dict, stats: Dict):
        """Run security checks and populate findings"""
        findings = audit["security_findings"]
        recommendations = audit["recommendations"]
        
        # Check 1: Guest network presence
        guest_clients = stats.get('guestClient', 0)
        total_clients = stats.get('wifiClient', 0) + stats.get('wiredClient', 0)
        
        if guest_clients == 0 and total_clients > 0:
            findings.append({
                "id": "SEC001",
                "severity": "MEDIUM",
                "title": "No Guest Network Detected",
                "description": f"Site has {total_clients} clients but no dedicated guest network",
                "impact": "Unmanaged devices may access primary network"
            })
            recommendations.append({
                "id": "REC001",
                "priority": "MEDIUM",
                "action": "provision_guest_network",
                "description": "Create isolated guest network for visitor access"
            })
        
        # Check 2: Offline devices
        offline_total = stats.get('offlineDevice', 0)
        if offline_total > 0:
            findings.append({
                "id": "SEC002",
                "severity": "LOW",
                "title": f"{offline_total} Offline Devices",
                "description": f"Network has {offline_total} offline device(s)",
                "impact": "Potential network connectivity issues"
            })
            recommendations.append({
                "id": "REC002",
                "priority": "LOW",
                "action": "investigate_offline_devices",
                "description": "Review and remediate offline devices"
            })
        
        # Check 3: Pending updates
        pending = stats.get('pendingUpdateDevice', 0)
        if pending > 0:
            findings.append({
                "id": "SEC003",
                "severity": "MEDIUM",
                "title": f"{pending} Devices with Pending Updates",
                "description": f"Network has {pending} device(s) waiting for firmware updates",
                "impact": "Security vulnerabilities may persist"
            })
            recommendations.append({
                "id": "REC003",
                "priority": "HIGH",
                "action": "apply_pending_updates",
                "description": "Apply all pending firmware updates to network devices"
            })
        
        # Check 4: Critical notifications
        critical = stats.get('criticalNotification', 0)
        if critical > 0:
            findings.append({
                "id": "SEC004",
                "severity": "HIGH",
                "title": f"{critical} Critical Notification(s)",
                "description": f"Network has {critical} critical alert(s) requiring attention",
                "impact": "Immediate action may be required"
            })
            recommendations.append({
                "id": "REC004",
                "priority": "CRITICAL",
                "action": "investigate_critical_alerts",
                "description": "Investigate and resolve all critical notifications"
            })
        
        # Check 5: Network configuration baseline
        if stats.get('wifiConfiguration', 0) == 0:
            findings.append({
                "id": "SEC005",
                "severity": "HIGH",
                "title": "No WiFi Networks Configured",
                "description": "Site has no WiFi networks enabled",
                "impact": "WiFi connectivity not available"
            })
        
        # Check 6: WAN redundancy
        if stats.get('wanConfiguration', 0) < 2:
            findings.append({
                "id": "SEC006",
                "severity": "LOW",
                "title": "Limited WAN Configuration",
                "description": f"Site has only {stats.get('wanConfiguration', 0)} WAN config(s)",
                "impact": "No WAN redundancy - single point of failure"
            })
            recommendations.append({
                "id": "REC006",
                "priority": "LOW",
                "action": "add_wan_redundancy",
                "description": "Consider adding secondary WAN connection for resilience"
            })
        
        # Overall score
        if not findings:
            audit["security_score"] = 9.0
            audit["overall_status"] = "HEALTHY"
        elif len([f for f in findings if f["severity"] == "HIGH"]) > 0:
            audit["security_score"] = 4.0
            audit["overall_status"] = "AT_RISK"
        elif len([f for f in findings if f["severity"] == "MEDIUM"]) > 1:
            audit["security_score"] = 6.0
            audit["overall_status"] = "CAUTION"
        else:
            audit["security_score"] = 7.5
            audit["overall_status"] = "ACCEPTABLE"
    
    def run_full_audit(self) -> Dict:
        """Run complete audit on all sites"""
        logger.info("Starting full security audit...")
        
        sites = self.get_all_sites()
        report = {
            "audit_timestamp": datetime.now().isoformat(),
            "total_sites": len(sites),
            "total_findings": 0,
            "total_recommendations": 0,
            "sites": []
        }
        
        for site in sites:
            logger.info(f"Auditing site: {site['meta'].get('name')}")
            audit = self.audit_site_security(site)
            report["sites"].append(audit)
            report["total_findings"] += len(audit["security_findings"])
            report["total_recommendations"] += len(audit["recommendations"])
        
        return report
    
    def save_report(self, report: Dict, filename: str = "/opt/unifi-bot/security_audit_report.json"):
        """Save audit report to file"""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"✓ Report saved to {filename}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    auditor = UniFiSecurityAuditor()
    
    print("\n=== RUNNING SECURITY AUDIT ===\n")
    report = auditor.run_full_audit()
    auditor.save_report(report)
    
    print("\n=== AUDIT SUMMARY ===\n")
    print(f"Total Sites: {report['total_sites']}")
    print(f"Total Findings: {report['total_findings']}")
    print(f"Total Recommendations: {report['total_recommendations']}")
    
    for site in report['sites']:
        print(f"\n✓ {site['site_name']} ({site['site_id'][:8]}...)")
        print(f"  Status: {site['overall_status']} (Score: {site['security_score']}/10)")
        print(f"  Devices: {site['device_inventory']['total_devices']} | Clients: {site['client_inventory']['total_clients']}")
        print(f"  Findings: {len(site['security_findings'])} | Recommendations: {len(site['recommendations'])}")
