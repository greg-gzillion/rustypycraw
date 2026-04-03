#!/usr/bin/env python3
"""
RustyPyCraw CLI - Hybrid code crawler with shared memory
"""

import argparse
import sys
from .crawler import RustyPyCraw
from .knowledge import get_references, list_languages
from .shared_memory import SharedMemory

def show_references(language=None):
    """Display online references for a language"""
    if language:
        refs = get_references(language)
        print(f"\n📚 References for {language.upper()}:")
        print("-" * 40)
        for name, url in refs.items():
            print(f"  {name}: {url}")
    else:
        print("\n📚 Available Languages with References:")
        print("-" * 40)
        for lang in list_languages():
            if lang != "general":
                print(f"  - {lang.upper()}")

def show_all_references():
    """Display all available documentation references"""
    from .knowledge import KNOWLEDGE_BASE
    print("\n📚 ALL DOCUMENTATION REFERENCES")
    print("=" * 50)
    for category, refs in KNOWLEDGE_BASE.items():
        print(f"\n🔹 {category.upper()}:")
        for name, url in refs.items():
            print(f"   • {name}: {url}")

def show_shared_memory_stats():
    """Show shared memory statistics"""
    memory = SharedMemory()
    stats = memory.get_stats()
    agents = memory.get_all_agents()
    
    print("\n📚 SHARED MEMORY STATISTICS")
    print("=" * 50)
    print(f"  Total memories: {stats['memories']}")
    print(f"  Total conversations: {stats['conversations']}")
    print(f"  Registered agents: {stats['agents']}")
    
    if agents:
        print("\n🦞 REGISTERED AGENTS:")
        for name, repo, caps in agents:
            print(f"  • {name}")
            print(f"    Repo: {repo}")
            print(f"    Capabilities: {caps[:80]}...")
    memory.close()

def remember_memory(key, value):
    """Store a memory in shared database"""
    memory = SharedMemory()
    memory.remember("rustypycraw", key, value)
    print(f"✅ Memory stored: {key} = {value}")
    memory.close()

def recall_memory(key):
    """Recall memories from shared database"""
    memory = SharedMemory()
    results = memory.recall(key)
    
    if results:
        print(f"\n📖 Memories matching '{key}':")
        print("=" * 50)
        for agent, mem_key, value, tags in results:
            print(f"\n🦞 {agent}: {mem_key}")
            print(f"   {value[:200]}...")
    else:
        print(f"No memories found for '{key}'")
    memory.close()

def main():
    parser = argparse.ArgumentParser(description="RustyPyCraw - Hybrid code crawler")
    parser.add_argument("path", nargs="?", default=".", help="Path to crawl")
    parser.add_argument("--stats", action="store_true", help="Show codebase statistics")
    parser.add_argument("--search", "-s", help="Search for pattern in files")
    parser.add_argument("--grep", "-g", help="Search with context lines")
    parser.add_argument("--context", "-c", type=int, default=2, help="Context lines for grep")
    parser.add_argument("--pinch", "-p", action="store_true", help="Find unnecessary .clone() calls")
    parser.add_argument("--ask", "-a", help="Ask AI about the codebase")
    parser.add_argument("--groq", action="store_true", help="Use Groq API (fast)")
    parser.add_argument("--ollama", action="store_true", help="Use Ollama (local)")
    parser.add_argument("--model", "-m", help="Specify model to use")
    parser.add_argument("--list-models", action="store_true", help="List all available models")
    parser.add_argument("--docs", "-d", help="Show documentation references for a language")
    parser.add_argument("--list-langs", action="store_true", help="List all languages with references")
    parser.add_argument("--summary", action="store_true", help="Show detailed summary")
    parser.add_argument("--all-docs", action="store_true", help="Show all documentation references")
    parser.add_argument("--shared-stats", action="store_true", help="Show shared memory statistics")
    parser.add_argument("--remember", nargs=2, metavar=('KEY', 'VALUE'), help="Store a memory in shared database")
    parser.add_argument("--recall", help="Recall memories by key")
    
    args = parser.parse_args()
    
    # Handle documentation commands
    if args.all_docs:
        show_all_references()
        return
    
    if args.list_langs:
        show_references()
        return
    
    if args.docs:
        show_references(args.docs)
        return
    
    if args.list_models:
        from .models import ModelProvider
        provider = ModelProvider()
        for name in provider.list_models():
            print(name)
        return
    
    # Handle shared memory commands
    if args.shared_stats:
        show_shared_memory_stats()
        return
    
    if args.remember:
        remember_memory(args.remember[0], args.remember[1])
        return
    
    if args.recall:
        recall_memory(args.recall)
        return
    
    # Initialize crawler for file operations
    crawler = RustyPyCraw(args.path)
    
    if args.stats:
        stats = crawler.stats()
        print("\n📊 RustyPyCraw Statistics")
        print(f"  Path: {stats.get('root_path', 'Unknown')}")
        print(f"  Total lines: {stats.get('total_lines', 0):,}")
        print(f"  Languages:")
        for lang, count in stats.get('languages', {}).items():
            print(f"    {lang}: {count}")
        print(f"  Rust core: {'✅' if stats.get('rust_available') else '❌'}")
        print(f"  AI available: {'✅' if stats.get('ai_available') else '❌'}")
        return
    
    if args.summary:
        print(crawler.summary())
        return
    
    if args.search:
        results = crawler.search(args.search)
        print(f"\n🔍 Found {len(results)} files containing '{args.search}':")
        for r in results[:20]:
            print(f"  {r}")
        if len(results) > 20:
            print(f"  ... and {len(results) - 20} more")
        return
    
    if args.grep:
        results = crawler.grep(args.grep, args.context)
        print(f"\n🔍 Found {len(results)} matches for '{args.grep}':")
        for r in results[:30]:
            print(f"\n  📄 {r['file']}:{r['line']}")
            for before in r['before'][-2:]:
                print(f"     {before}")
            print(f"  ➤ {r['content']}")
            for after in r['after'][:2]:
                print(f"     {after}")
        return
    
    if args.pinch:
        bugs = crawler.pinch()
        print(f"\n🦞 Found {len(bugs)} unnecessary .clone() calls:")
        for b in bugs[:30]:
            print(f"  📄 {b['file']}:{b['line']}")
            print(f"     ⚠️  {b['message']}")
            print(f"     💡 {b['suggestion']}")
        return
    
    if args.ask:
        from .models import ModelProvider
        provider = ModelProvider()
        
        if args.groq:
            result = provider.ask(args.ask, provider='groq', model=args.model)
        elif args.ollama:
            result = provider.ask(args.ask, provider='ollama', model=args.model or 'codellama:7b')
        else:
            result = provider.ask(args.ask)
        
        print(f"\n🤖 {result}\n")
        return
    
    parser.print_help()

if __name__ == "__main__":
    main()
