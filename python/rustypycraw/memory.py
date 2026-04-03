"""
Memory hierarchy for RustyPyCraw - loads context from multiple levels
Based on agentic-ai-prompt-research Pattern 16
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any

class MemoryLoader:
    """Hierarchical memory loading - project -> session -> code context"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).expanduser()
        self.memory_stack = []

    def load_all_context(self, query: str = "") -> str:
        """Load context from all memory levels"""
        contexts = []

        vision_path = self.root_path / "VISION.md"
        if vision_path.exists():
            with open(vision_path, "r") as f:
                content = f.read()[:1500]
                contexts.append(f"[PROJECT VISION]\\n{content}")

        readme_path = self.root_path / "README.md"
        if readme_path.exists():
            with open(readme_path, "r") as f:
                content = f.read()[:1000]
                contexts.append(f"[PROJECT README]\\n{content}")

        session_memory = self._load_session_memory()
        if session_memory:
            contexts.append(f"[SESSION MEMORY]\\n{session_memory}")

        if query:
            code_context = self._load_code_context(query)
            if code_context:
                contexts.append(f"[CODE CONTEXT]\\n{code_context}")

        return "\\n\\n".join(contexts)

    def _load_session_memory(self) -> str:
        """Load recent conversation history"""
        memory_file = Path.home() / ".rustypycraw_memory.json"
        if memory_file.exists():
            with open(memory_file, "r") as f:
                data = json.load(f)
                recent = data.get("recent_questions", [])[-3:]
                if recent:
                    return "Recent discussions:\\n" + "\\n".join(f"- {q}" for q in recent)
        return ""

    def _load_code_context(self, query: str) -> str:
        """Load relevant code files based on query keywords"""
        keywords = query.lower().split()[:3]
        context = []

        for kw in keywords:
            for filepath in self.root_path.rglob("*.rs"):
                if filepath.stat().st_size > 50000:
                    continue
                try:
                    with open(filepath, "r") as f:
                        content = f.read()
                        if kw in content.lower():
                            lines = content.split("\\n")
                            for i, line in enumerate(lines):
                                if kw in line.lower():
                                    start = max(0, i-2)
                                    end = min(len(lines), i+3)
                                    excerpt = "\\n".join(lines[start:end])
                                    context.append(f"File: {filepath.name} (line {i+1})\\n{excerpt}")
                                    break
                            if len(context) >= 3:
                                break
                except:
                    pass
            if len(context) >= 3:
                break

        return "\\n\\n".join(context[:3])

    def save_to_memory(self, question: str, answer: str):
        """Save conversation to session memory"""
        memory_file = Path.home() / ".rustypycraw_memory.json"
        data = {}
        if memory_file.exists():
            with open(memory_file, "r") as f:
                data = json.load(f)

        if "recent_questions" not in data:
            data["recent_questions"] = []

        import time
        data["recent_questions"].append({
            "question": question[:100],
            "timestamp": str(time.time())
        })
        data["recent_questions"] = data["recent_questions"][-20:]

        with open(memory_file, "w") as f:
            json.dump(data, f, indent=2)
