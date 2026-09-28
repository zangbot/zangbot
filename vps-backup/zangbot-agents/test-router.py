#!/usr/bin/env python3
"""
Zangbot Router Decision Engine
Test the router config against real tasks
"""

import json
import yaml
import sys
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path.home() / ".zangbot/router-config.yaml"
LOG_PATH = Path.home() / ".zangbot/router-decisions.log"

class RouterEngine:
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.decisions = []
    
    def analyze_query(self, prompt, context=None):
        """Analyze a query and decide: local or claude"""
        
        # Extract features
        prompt_tokens = len(prompt.split())  # Rough estimate
        keywords = set(prompt.lower().split())
        
        # Check each decision rule
        for rule in self.config['decision_rules']:
            name = rule['name']
            triggers = rule.get('triggers', {})
            
            matched = True
            
            # Check token length trigger
            if 'prompt_length_tokens' in triggers:
                min_t, max_t = triggers['prompt_length_tokens']
                if not (min_t <= prompt_tokens <= max_t):
                    matched = False
            
            # Check keywords_all trigger (all must be present)
            if matched and 'keywords_all' in triggers:
                rule_keywords = set(triggers['keywords_all'])
                if not rule_keywords <= keywords:  # Is subset
                    matched = False
            
            # Check keywords_any trigger (at least one must be present)
            if matched and 'keywords_any' in triggers:
                rule_keywords = set(triggers['keywords_any'])
                if not rule_keywords & keywords:  # Has intersection
                    matched = False
            
            # Check keywords_not trigger (none must be present)
            if matched and 'keywords_not' in triggers:
                exclude_keywords = set(triggers['keywords_not'])
                if exclude_keywords & keywords:  # Has intersection with exclude list
                    matched = False
            
            if matched:
                # Rule matched!
                backend = rule['backend']
                decision = {
                    'timestamp': datetime.now().isoformat(),
                    'rule_matched': name,
                    'backend': backend,
                    'prompt_length': prompt_tokens,
                    'reasoning': rule.get('reasoning', ''),
                    'post_action': rule.get('post_action'),
                }
                
                self.decisions.append(decision)
                return backend, decision
        
        # Fallback rule
        fallback = self.config['decision_rules'][-1]
        backend = fallback['backend']
        decision = {
            'timestamp': datetime.now().isoformat(),
            'rule_matched': fallback['name'],
            'backend': backend,
            'prompt_length': prompt_tokens,
            'reasoning': 'No specific rule matched, using fallback',
        }
        self.decisions.append(decision)
        return backend, decision
    
    def log_decision(self, decision):
        """Log decision to file"""
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, 'a') as f:
            f.write(json.dumps(decision) + '\n')
    
    def get_stats(self):
        """Return routing statistics"""
        if not self.decisions:
            return {}
        
        local_count = sum(1 for d in self.decisions if d['backend'] == 'local')
        claude_count = sum(1 for d in self.decisions if d['backend'] == 'claude')
        
        return {
            'total_decisions': len(self.decisions),
            'local_count': local_count,
            'claude_count': claude_count,
            'local_percentage': round(100 * local_count / len(self.decisions), 1),
            'target_local_percentage': self.config['cost_control']['local_queries_target'],
        }

# Test cases
TEST_CASES = [
    {
        'name': 'Quick log grep',
        'prompt': 'Show me the last 10 lines of the Vodia error log',
        'expected_backend': 'local',
    },
    {
        'name': 'Planning a VLAN change',
        'prompt': 'Plan a VLAN migration strategy for 3 sites',
        'expected_backend': 'local',
    },
    {
        'name': 'Code review',
        'prompt': 'Review this Python function and suggest optimizations',
        'expected_backend': 'local',
    },
    {
        'name': 'Business strategy',
        'prompt': 'How should we approach pricing our managed services to compete with larger MSPs?',
        'expected_backend': 'claude',
    },
    {
        'name': 'Infrastructure troubleshooting',
        'prompt': 'Extension 201 keeps dropping calls on VLAN 30, where should I check?',
        'expected_backend': 'local',
    },
    {
        'name': 'Writing a client proposal',
        'prompt': 'Write a professional proposal for upgrading a client\'s network infrastructure',
        'expected_backend': 'claude',
    },
    {
        'name': 'Diff analysis',
        'prompt': 'diff: what changed in this UniFi config between versions?',
        'expected_backend': 'local',
    },
]

def main():
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          Zangbot Router Decision Engine — Test Suite           ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    router = RouterEngine(CONFIG_PATH)
    
    print(f"Config loaded from: {CONFIG_PATH}\n")
    
    results = []
    for i, test in enumerate(TEST_CASES, 1):
        name = test['name']
        prompt = test['prompt']
        expected = test['expected_backend']
        
        backend, decision = router.analyze_query(prompt)
        router.log_decision(decision)
        
        match = "✅" if backend == expected else "❌"
        status = "PASS" if backend == expected else "FAIL"
        
        print(f"{i}. {name}")
        print(f"   Prompt: {prompt[:60]}...")
        print(f"   Expected: {expected:8} | Got: {backend:8} | {match} {status}")
        print(f"   Rule: {decision['rule_matched']}")
        print()
        
        results.append({
            'test': name,
            'status': status,
            'expected': expected,
            'got': backend,
        })
    
    # Summary
    stats = router.get_stats()
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                      RESULTS SUMMARY                          ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"\nTests passed: {passed}/{total}")
    print(f"Local queries: {stats['local_count']}/{stats['total_decisions']} ({stats['local_percentage']}%)")
    print(f"Claude queries: {stats['claude_count']}/{stats['total_decisions']}")
    print(f"Target local usage: {stats['target_local_percentage']}")
    print(f"\nDecisions logged to: {LOG_PATH}")
    print(f"\nRouter config: {CONFIG_PATH}")
    
    if passed == total:
        print("\n✅ All tests PASSED. Router ready for integration.\n")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) FAILED. Review decision rules.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
