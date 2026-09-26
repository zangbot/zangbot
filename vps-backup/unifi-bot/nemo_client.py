"""Nemo LLM Client - for bot intelligence"""
import os
import requests
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class NemoClient:
    """Client for Nemo LLM (OpenAI-compatible)"""
    
    def __init__(self):
        self.endpoint = os.getenv("NEMO_ENDPOINT", "http://localhost:1234/v1")
        self.model = os.getenv("NEMO_MODEL", "nemo-7b")
    
    def ask(self, prompt: str, system: str = None, temperature: float = 0.7) -> Optional[str]:
        """Ask Nemo a question"""
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 500,
                "top_p": 0.9
            }
            
            logger.info(f"Calling Nemo: {prompt[:50]}...")
            resp = requests.post(
                f"{self.endpoint}/chat/completions",
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            
            answer = data['choices'][0]['message']['content']
            logger.info(f"✓ Nemo response: {answer[:100]}")
            return answer
            
        except Exception as e:
            logger.error(f"✗ Nemo call failed: {e}")
            return None
    
    def decide_action(self, context: dict) -> dict:
        """Use Nemo to decide if action should be approved"""
        system = """You are a network automation assistant. Analyze the action request and determine if it's safe to execute.
        
        Respond ONLY with JSON (no markdown, no extra text):
        {"approved": true/false, "reason": "explanation", "confidence": 0.0-1.0}
        
        Rules:
        - Approve: Safe network changes, guest networks, monitoring
        - Reject: Destructive changes, modifying critical configs, unknown actions"""
        
        prompt = f"""Action: {context.get('action')}
Site: {context.get('site_id')}
Description: {context.get('description')}
Current devices: {context.get('device_count', 'unknown')}
Current clients: {context.get('client_count', 'unknown')}

Is this action safe to execute?"""
        
        response = self.ask(prompt, system=system, temperature=0.3)
        
        if not response:
            return {"approved": False, "reason": "Nemo unavailable", "confidence": 0.0}
        
        try:
            import json
            # Clean response (sometimes includes markdown)
            response = response.strip()
            if response.startswith('```'):
                response = response.split('\n', 1)[1].rsplit('\n', 1)[0]
            
            result = json.loads(response)
            logger.info(f"✓ Decision: approved={result.get('approved')}, confidence={result.get('confidence')}")
            return result
        except json.JSONDecodeError:
            logger.error(f"✗ Could not parse Nemo response: {response}")
            return {"approved": False, "reason": "Could not parse response", "confidence": 0.0}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    nemo = NemoClient()
    
    print("\n=== TESTING NemoClient ===\n")
    
    # Test 1: Simple ask
    print("[1] Simple question test...")
    answer = nemo.ask("What is a UniFi network?")
    if answer:
        print(f"✓ Nemo: {answer[:200]}...")
    else:
        print("✗ Nemo unavailable")
    
    print()
    
    # Test 2: Decision logic
    print("[2] Decision logic test...")
    context = {
        "action": "provision_guest_network",
        "site_id": "6726c7d95e28596cce79087f",
        "description": "Create guest WiFi for visitors",
        "device_count": 4,
        "client_count": 18
    }
    decision = nemo.decide_action(context)
    print(f"✓ Decision: {decision}")
    
    print("\n=== END TESTS ===\n")
