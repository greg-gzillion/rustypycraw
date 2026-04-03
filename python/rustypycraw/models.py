"""
Multi-Model Provider for RustyPyCraw
Supports: Groq API, Ollama (multiple models)
"""

import os
import requests
import json
from typing import Optional, Dict, Any, List

class ModelProvider:
    """Unified interface for multiple LLM providers"""
    
    def __init__(self):
        self.providers = {}
        self._check_groq()
        self._check_ollama()
    
    def _check_groq(self):
        """Check if Groq API is available"""
        try:
            from groq import Groq
            api_key = os.environ.get("GROQ_API_KEY")
            if api_key:
                self.providers['groq'] = {
                    'type': 'cloud',
                    'speed': 'fast (1-2s)',
                    'cost': 'free',
                    'models': ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'],
                    'client': Groq(api_key=api_key)
                }
                print("✅ Groq API available")
        except ImportError:
            pass
    
    def _check_ollama(self):
        """Check available Ollama models"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.providers['ollama'] = {
                    'type': 'local',
                    'speed': 'slow (30-120s)',
                    'cost': 'free',
                    'models': [m['name'] for m in models],
                    'model_details': {m['name']: m for m in models}
                }
                print(f"✅ Ollama available with {len(models)} models")
        except:
            pass
    
    def list_models(self) -> Dict:
        """List all available models"""
        all_models = {}
        for provider_name, provider in self.providers.items():
            for model in provider['models']:
                all_models[f"{provider_name}/{model}"] = {
                    'provider': provider_name,
                    'model': model,
                    'speed': provider['speed'],
                    'cost': provider['cost'],
                    'type': provider['type']
                }
        return all_models
    
    def ask(self, question: str, provider: str = None, model: str = None, context: str = "") -> str:
        """Ask a question using specified provider/model"""
        full_prompt = f"Context:\n{context}\n\nQuestion: {question}" if context else question
        
        # Auto-select best provider
        if not provider:
            if "code" in question.lower() or "rust" in question.lower():
                provider = "ollama"
                model = model or "codellama:7b"
            else:
                provider = "groq"
        
        if provider == "groq" and provider in self.providers:
            return self._ask_groq(full_prompt, model)
        elif provider == "ollama" and provider in self.providers:
            return self._ask_ollama(full_prompt, model)
        else:
            return f"Provider {provider} not available. Available: {list(self.providers.keys())}"
    
    def _ask_groq(self, prompt: str, model: str = None) -> str:
        """Query Groq API"""
        try:
            groq = self.providers['groq']['client']
            model = model or "llama-3.3-70b-versatile"
            response = groq.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Groq Error: {e}"
    
    def _ask_ollama(self, prompt: str, model: str = None) -> str:
        """Query local Ollama"""
        try:
            model = model or "codellama:7b"
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=120
            )
            if response.status_code == 200:
                return response.json()["response"]
            return f"Ollama Error: HTTP {response.status_code}"
        except Exception as e:
            return f"Ollama Error: {e}"
    
    def compare(self, question: str) -> Dict:
        """Compare responses from different models"""
        results = {}
        if 'groq' in self.providers:
            results['groq/llama-3.3-70b'] = self._ask_groq(question)
        if 'ollama' in self.providers:
            for model in self.providers['ollama']['models'][:2]:
                results[f'ollama/{model}'] = self._ask_ollama(question, model)
        return results

# Test the provider
if __name__ == "__main__":
    print("=" * 50)
    print("Model Provider Test")
    print("=" * 50)
    provider = ModelProvider()
    print("\nAvailable models:")
    for name, info in provider.list_models().items():
        print(f"  • {name} ({info['speed']})")
