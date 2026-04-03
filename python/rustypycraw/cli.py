#!/usr/bin/env python3
"""
RustyPyCraw CLI - Hybrid code crawler
"""

import argparse
import sys
from .crawler import RustyPyCraw

def main():
    parser = argparse.ArgumentParser(description="RustyPyCraw - Hybrid code crawler")
    parser.add_argument("path", nargs="?", default=".", help="Path to crawl")
    parser.add_argument("--stats", action="store_true", help="Show codebase statistics")
    parser.add_argument("--search", "-s", help="Search for pattern in files")
    parser.add_argument("--grep", "-g", help="Search with context lines")
    parser.add_argument("--context", "-c", type=int, default=2, help="Context lines for grep")
    parser.add_argument("--pinch", "-p", action="store_true", help="Find unnecessary .clone() calls")
    parser.add_argument("--ask", "-a", help="Ask AI about the codebase")
    parser.add_argument("--summary", action="store_true", help="Show detailed summary")
    
    args = parser.parse_args()
    
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
        
    elif args.summary:
        print(crawler.summary())
        
    elif args.search:
        results = crawler.search(args.search)
        print(f"\n🔍 Found {len(results)} files containing '{args.search}':")
        for r in results[:20]:
            print(f"  {r}")
        if len(results) > 20:
            print(f"  ... and {len(results) - 20} more")
            
    elif args.grep:
        results = crawler.grep(args.grep, args.context)
        print(f"\n🔍 Found {len(results)} matches for '{args.grep}':")
        for r in results[:30]:
            print(f"\n  📄 {r['file']}:{r['line']}")
            for before in r['before'][-2:]:
                print(f"     {before}")
            print(f"  ➤ {r['content']}")
            for after in r['after'][:2]:
                print(f"     {after}")
                
    elif args.pinch:
        bugs = crawler.pinch()
        print(f"\n🦞 Found {len(bugs)} unnecessary .clone() calls:")
        for b in bugs[:30]:
            print(f"  📄 {b['file']}:{b['line']}")
            print(f"     ⚠️  {b['message']}")
            print(f"     💡 {b['suggestion']}")
            
    elif args.ask:
        print(f"\n🤖 {crawler.ask(args.ask)}\n")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
