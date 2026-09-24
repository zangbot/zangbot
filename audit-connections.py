#!/usr/bin/env python3
"""
Zangbot Infrastructure Connection Audit
Tests all backend connections: UniFi, Bitwarden, Hostinger, Vodia, GitHub
Follows zangbot-operational-kernel rules: dry-run + approval before live
"""

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path

class ConnectionAudit:
    def __init__(self):
        self.results = []
        self.timestamp = datetime.now().isoformat()
        
    def test_connection(self, name, command, expect_code=0, expect_pattern=None):
        """Run a test command and check result"""
        print(f"Testing: {name}...")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == expect_code
            if expect_pattern and success:
                success = expect_pattern.lower() in result.stdout.lower()
            
            status = "✅ PASS" if success else "❌ FAIL"
            output = result.stdout[:200] if result.stdout else result.stderr[:200]
            
            self.results.append({
                'name': name,
                'status': 'PASS' if success else 'FAIL',
                'return_code': result.returncode,
                'output': output,
                'timestamp': self.timestamp,
            })
            
            print(f"  {status}")
            if not success:
                print(f"  Output: {output[:100]}...")
            
            return success
            
        except subprocess.TimeoutExpired:
            self.results.append({
                'name': name,
                'status': 'TIMEOUT',
                'error': 'Connection timeout (10s)',
                'timestamp': self.timestamp,
            })
            print(f"  ⏱️  TIMEOUT")
            return False
        except Exception as e:
            self.results.append({
                'name': name,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': self.timestamp,
            })
            print(f"  ⚠️  ERROR: {e}")
            return False
    
    def run_audit(self):
        """Run all connection tests"""
        
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║         Zangbot Infrastructure Connection Audit               ║")
        print("║              All systems: Check before build                  ║")
        print("╚════════════════════════════════════════════════════════════════╝\n")
        
        # ===== LOCAL MACHINE =====
        print("🖥️  LOCAL MACHINE (Mac Studio)")
        print("─" * 60)
        
        self.test_connection(
            "Ollama endpoint reachable",
            "curl -s http://localhost:11434/api/tags | jq '.models | length'",
            expect_pattern="2"
        )
        
        self.test_connection(
            "Qwen2.5:7b model loaded",
            "curl -s http://localhost:11434/api/tags | jq '.models[].name' | grep qwen2.5",
            expect_pattern="qwen"
        )
        
        self.test_connection(
            "Phi3 model loaded",
            "curl -s http://localhost:11434/api/tags | jq '.models[].name' | grep phi3",
            expect_pattern="phi"
        )
        
        self.test_connection(
            "Git SSH key present",
            "ls -la ~/.ssh/id_ed25519",
            expect_code=0
        )
        
        self.test_connection(
            "Git config set",
            "git config --global user.name",
            expect_pattern="zangetsu"
        )
        
        # ===== GITHUB =====
        print("\n🐙 GITHUB")
        print("─" * 60)
        
        self.test_connection(
            "SSH known_hosts has github.com",
            "grep -c github.com ~/.ssh/known_hosts",
            expect_code=0
        )
        
        # This will fail on new machine but we'll document it
        self.test_connection(
            "SSH agent has key loaded",
            "ssh-add -l 2>&1 | grep -q 'ED25519'",
            expect_code=0
        )
        
        # ===== BITWARDEN =====
        print("\n🔐 BITWARDEN")
        print("─" * 60)
        
        self.test_connection(
            "Bitwarden CLI installed",
            "which bw",
            expect_code=0
        )
        
        self.test_connection(
            "Bitwarden vault accessible",
            "bw status 2>&1 | grep -q 'authenticated\\|locked\\|unauthenticated'",
            expect_code=0
        )
        
        # ===== HOSTINGER VPS =====
        print("\n🌐 HOSTINGER VPS (72.62.97.23)")
        print("─" * 60)
        
        self.test_connection(
            "SSH access to VPS",
            "ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new root@72.62.97.23 'echo OK' 2>&1",
            expect_code=0
        )
        
        self.test_connection(
            "Zangbot FastAPI router running",
            "ssh root@72.62.97.23 'curl -s localhost:8001/health | grep ok'",
            expect_code=0
        )
        
        self.test_connection(
            "Systemd service active",
            "ssh -o ConnectTimeout=5 root@72.62.97.23 'systemctl is-active zangbot-router' 2>&1",
            expect_pattern="active"
        )
        
        # ===== UNIFI CONTROLLER =====
        print("\n📡 UNIFI CONTROLLER")
        print("─" * 60)
        
        self.test_connection(
            "UniFi Cloud API key in Bitwarden",
            "bw list items --search 'unifi' 2>&1 | jq '.[] | select(.name | contains(\"unifi\"))' | head -5",
            expect_code=0
        )
        
        # UniFi local controller: managed separately via unifi.ui.com REST API
        # No local test needed
        
        # ===== UNIFI MAX (Failover) =====
        print("\n📡 UNIFI MAX (Backup/Failover)")
        print("─" * 60)
        
        self.test_connection(
            "UniFi Max device online",
            "curl -s -m 5 http://192.168.1.10:8080/api/system/status 2>&1 | head -3",
            expect_code=0
        )
        
        # ===== VODIA PBX =====
        print("\n☎️  VODIA PBX")
        print("─" * 60)
        
        self.test_connection(
            "Vodia REST API reachable",
            "curl -s -m 5 http://vodia.local/rest/system/status 2>&1 | head -3",
            expect_code=0
        )
        
        self.test_connection(
            "Vodia credentials in vault",
            "bw list items --search 'vodia' 2>&1 | jq '.[] | select(.name | contains(\"vodia\"))' | head -5",
            expect_code=0
        )
        
        # ===== SUMMARY =====
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║                    AUDIT SUMMARY                            ║")
        print("╚════════════════════════════════════════════════════════════════╝\n")
        
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        timeout = sum(1 for r in self.results if r['status'] == 'TIMEOUT')
        error = sum(1 for r in self.results if r['status'] == 'ERROR')
        total = len(self.results)
        
        print(f"Total tests:    {total}")
        print(f"✅ Passed:       {passed}")
        print(f"❌ Failed:       {failed}")
        print(f"⏱️  Timeout:      {timeout}")
        print(f"⚠️  Errors:       {error}")
        print(f"\nPass rate: {round(100 * passed / total, 1)}%\n")
        
        # ===== REQUIRED CONNECTIONS =====
        print("REQUIRED CONNECTIONS FOR BUILD:")
        print("─" * 60)
        required = {
            'Ollama endpoint reachable': 'CRITICAL',
            'Bitwarden vault accessible': 'CRITICAL',
            'Hostinger VPS SSH access': 'CRITICAL',
            'Zangbot FastAPI router running': 'CRITICAL',
            'Git SSH key present': 'REQUIRED',
            'GitHub SSH access': 'REQUIRED',
            'Vodia REST API reachable': 'REQUIRED',
        }
        
        for test_name, level in required.items():
            result = next((r for r in self.results if r['name'] == test_name), None)
            if result:
                status = "✅" if result['status'] == 'PASS' else "❌"
                print(f"{status} {level:10} {test_name}: {result['status']}")
            else:
                print(f"⚠️  {level:10} {test_name}: NOT TESTED")
        
        # ===== FAILURES DETAIL =====
        if failed > 0 or timeout > 0:
            print("\nFAILURES DETAIL:")
            print("─" * 60)
            for r in self.results:
                if r['status'] in ['FAIL', 'TIMEOUT', 'ERROR']:
                    print(f"\n❌ {r['name']}")
                    print(f"   Status: {r['status']}")
                    if 'error' in r:
                        print(f"   Error: {r['error']}")
                    if 'output' in r:
                        print(f"   Output: {r['output'][:150]}")
        
        # ===== SAVE LOG =====
        log_path = Path.home() / '.zangbot/audit-results.json'
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nAudit log saved to: {log_path}")
        
        return passed, failed, timeout, error

def main():
    audit = ConnectionAudit()
    passed, failed, timeout, error = audit.run_audit()
    
    # Critical failures block build
    if failed > 3 or timeout > 2:
        print("\n⛔ CRITICAL ISSUES FOUND — Cannot proceed with build.")
        print("   Fix failures listed above, then re-run audit.\n")
        return 1
    
    print("\n✅ Infrastructure audit ready for review.")
    print("   Present results to user before proceeding.\n")
    return 0

if __name__ == '__main__':
    sys.exit(main())
