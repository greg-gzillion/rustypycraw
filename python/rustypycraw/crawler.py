"""
RustyPyCraw - Hybrid code crawler with Rust speed and Python AI
Supports both Groq API (fast) and Ollama (local, free)
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Try Rust core
try:
    from rustypycrawcore import Crawler as RustCrawler
    RUST_AVAILABLE = True
except ImportError:
    print("⚠️ Rust core not built. Run: cd rustypycraw-core && maturin develop")
    RUST_AVAILABLE = False

class RustyPyCraw:
    """Hybrid code crawler with Rust speed and Python AI"""
    
    def __init__(self, root_path: str, use_ollama: bool = False):
        self.root_path = os.path.expanduser(root_path)
        self.rust = RustCrawler(self.root_path) if RUST_AVAILABLE else None
        self.use_ollama = use_ollama
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Initialize AI
        self.ai = None
        if not use_ollama and GROQ_AVAILABLE:
            self.ai = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            self.ai_type = "Groq"
        elif use_ollama:
            self.ai_type = "Ollama"
        else:
            self.ai_type = None
        
        self._session_history = []
    
    # ============ SEARCH FEATURES ============
    
    def search(self, pattern: str, file_types: List[str] = None) -> List[str]:
        """Fast parallel search for files containing pattern"""
        if self.rust:
            results = self.rust.fast_search(pattern)
            # Filter by file type if specified
            if file_types:
                filtered = []
                for r in results:
                    for ft in file_types:
                        if r.endswith(ft):
                            filtered.append(r)
                            break
                return filtered
            return results
        return []
    
    def search_rust_only(self, pattern: str) -> List[str]:
        """Search only Rust files"""
        return self.search(pattern, ['.rs'])
    
    def grep(self, pattern: str, context: int = 2) -> List[Dict]:
        """Search with context lines"""
        if self.rust:
            results = self.rust.search_with_context(pattern, context)
            return [{
                'file': r.file,
                'line': r.line,
                'content': r.content,
                'before': r.context_before,
                'after': r.context_after
            } for r in results]
        return []
    
    # ============ BUG DETECTION (PINCH) ============
    
    def pinch(self) -> List[Dict]:
        """Find unnecessary .clone() calls in Rust files"""
        if self.rust:
            bugs = self.rust.pinch_clones()
            return [{
                'file': b.file,
                'line': b.line,
                'column': b.column,
                'message': b.message,
                'severity': b.severity,
                'suggestion': b.suggestion
            } for b in bugs]
        return []
    
    # ============ STATISTICS ============
    
    def stats(self) -> Dict:
        """Get comprehensive codebase statistics"""
        if not self.rust:
            return {"error": "Rust core not available"}
        
        by_lang = self.rust.count_by_language()
        total_lines = self.rust.total_lines()
        
        languages = {}
        for k, v in by_lang.items():
            languages[k] = v
        
        return {
            'root_path': self.root_path,
            'total_lines': total_lines,
            'languages': languages,
            'rust_available': RUST_AVAILABLE,
            'ai_type': self.ai_type,
            'ai_available': self.ai is not None or self.use_ollama
        }
    
    # ============ AI FEATURES ============
    
    def _ask_groq(self, prompt: str) -> str:
        """Query Groq API (fast)"""
        try:
            response = self.ai.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Groq Error: {e}"
    
    def _ask_ollama(self, prompt: str) -> str:
        """Query local Ollama (slower but free)"""
        import requests
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": "codellama:7b", "prompt": prompt, "stream": False},
                timeout=120
            )
            if response.status_code == 200:
                return response.json()["response"]
            return f"Ollama Error: HTTP {response.status_code}"
        except Exception as e:
            return f"Ollama Error: {e}"
    
    def ask(self, question: str, use_context: bool = True) -> str:
        """Ask AI about the codebase - prioritizes Rust files"""
        if not self.ai_type:
            return "ERROR: No AI backend available. Set GROQ_API_KEY or use_ollama=True"
        
        context = ""
        if use_context and self.rust:
            # First, search for relevant Rust files
            keywords = question.lower().split()[:3]
            rust_files = []
            for kw in keywords:
                results = self.search_rust_only(kw)
                rust_files.extend(results[:3])
            
            # Read relevant Rust files for context
            for filepath in list(set(rust_files))[:3]:
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()[:2000]  # First 2000 chars
                        context += f"\n=== {os.path.basename(filepath)} ===\n{content}\n"
                except:
                    pass
            
            # Also search for VISION.md for token info
            vision_path = os.path.join(self.root_path, "VISION.md")
            if os.path.exists(vision_path) and any(kw in question.lower() for kw in ['phnx', 'token', 'vision']):
                with open(vision_path, 'r') as f:
                    context += f"\n=== VISION.md ===\n{f.read()[:2000]}\n"
        
        if context:
            prompt = f"""You are RustyPyCraw, a PhoenixPME blockchain expert. Use this code context:

{context}

Question: {question}

Answer based on the actual code above. Be specific about values like 10% collateral, 1.1% fee, PHNX tokens."""
        else:
            prompt = question
        
        # Use selected AI backend
        if self.ai_type == "Groq" and self.ai:
            return self._ask_groq(prompt)
        elif self.use_ollama:
            return self._ask_ollama(prompt)
        else:
            return "No AI backend available"
    
    def ask_fast(self, question: str) -> str:
        """Fast AI query without code context search"""
        if self.ai_type == "Groq" and self.ai:
            return self._ask_groq(question)
        elif self.use_ollama:
            return self._ask_ollama(question)
        else:
            return "No AI backend available"
    
    # ============ UTILITIES ============
    
    def summary(self) -> str:
        """Generate a summary of the codebase"""
        stats = self.stats()
        rust_files = stats.get('languages', {}).get('Rust', 0)
        return f"""
RustyPyCraw Summary
===================
Path: {stats.get('root_path', 'Unknown')}
Total lines: {stats.get('total_lines', 0):,}
Rust files: {rust_files}
AI backend: {stats.get('ai_type', 'None')}
Rust core: {'✅' if stats.get('rust_available') else '❌'}
"""

    def analyze_cpp(self, filepath: str) -> str:
        """C++ specific analysis"""
        return self.ask(f"Analyze this C++ code for memory leaks, RAII violations, and undefined behavior:\n{self._read_file(filepath)}")
    
    def analyze_typescript(self, filepath: str) -> str:
        """TypeScript specific analysis"""
        return self.ask(f"Analyze this TypeScript code for type safety, null handling, and best practices:\n{self._read_file(filepath)}")
    
    def analyze_vb(self, filepath: str) -> str:
        """Visual Basic specific analysis"""
        return self.ask(f"Analyze this Visual Basic code for compatibility, error handling, and modern patterns:\n{self._read_file(filepath)}")
    
    def _read_file(self, filepath: str) -> str:
        """Helper to read file safely"""
        try:
            with open(filepath, 'r') as f:
                return f.read()[:3000]
        except:
            return "Error reading file"

    def languages_detailed(self) -> Dict:
        """Get detailed language breakdown including C++, TypeScript, VB"""
        if not self.rust:
            return {}
        
        files = self.rust.get_stats()
        lang_map = {
            'rs': 'Rust',
            'cpp': 'C++', 'cc': 'C++', 'cxx': 'C++', 'h': 'C++', 'hpp': 'C++',
            'ts': 'TypeScript', 'tsx': 'TypeScript',
            'js': 'JavaScript', 'jsx': 'JavaScript',
            'py': 'Python',
            'vb': 'Visual Basic', 'vbs': 'Visual Basic',
            'sol': 'Solidity',
            'go': 'Go',
            'md': 'Markdown',
            'toml': 'TOML',
            'json': 'JSON',
        }
        
        counts = {}
        for f in files:
            ext = f.path.split('.')[-1] if '.' in f.path else 'unknown'
            lang = lang_map.get(ext, 'Other')
            counts[lang] = counts.get(lang, 0) + 1
        
        return counts
