"""
Knowledge base with indexed online references for all supported languages
"""

KNOWLEDGE_BASE = {
    "rust": {
        "book": "https://doc.rust-lang.org/book/",
        "std": "https://doc.rust-lang.org/std/",
        "crates": "https://crates.io/",
        "rust_by_example": "https://doc.rust-lang.org/rust-by-example/",
        "rust_nomicon": "https://doc.rust-lang.org/nomicon/",
        "rust_embedded": "https://docs.rust-embedded.org/book/",
    },
    "cosmwasm": {
        "book": "https://book.cosmwasm.com/",
        "docs": "https://docs.cosmwasm.com/",
        "github": "https://github.com/CosmWasm/cosmwasm",
        "cw_plus": "https://github.com/CosmWasm/cw-plus",
        "wasmd": "https://github.com/CosmWasm/wasmd",
    },
    "cpp": {
        "reference": "https://en.cppreference.com/",
        "learn": "https://www.learncpp.com/",
        "core_guidelines": "https://isocpp.github.io/CppCoreGuidelines/",
        "cplusplus": "https://cplusplus.com/",
    },
    "typescript": {
        "handbook": "https://www.typescriptlang.org/docs/handbook/",
        "deep_dive": "https://basarat.gitbook.io/typescript/",
        "release_notes": "https://devblogs.microsoft.com/typescript/",
    },
    "javascript": {
        "mdn": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "javascript_info": "https://javascript.info/",
        "nodejs": "https://nodejs.org/en/docs/",
    },
    "visual_basic": {
        "microsoft_docs": "https://docs.microsoft.com/en-us/dotnet/visual-basic/",
        "language_ref": "https://docs.microsoft.com/en-us/dotnet/visual-basic/language-reference/",
        "vb6_docs": "https://docs.microsoft.com/en-us/previous-versions/visualstudio/visual-basic-6/",
    },
    "go": {
        "tour": "https://go.dev/tour/",
        "docs": "https://go.dev/doc/",
        "standard_lib": "https://pkg.go.dev/std",
    },
    "solidity": {
        "docs": "https://docs.soliditylang.org/",
        "remix": "https://remix.ethereum.org/",
        "openzeppelin": "https://docs.openzeppelin.com/",
    },
    "python": {
        "docs": "https://docs.python.org/3/",
        "pypi": "https://pypi.org/",
        "peps": "https://peps.python.org/",
    },
    "general": {
        "stackoverflow": "https://stackoverflow.com/",
        "github": "https://github.com/",
        "freecodecamp": "https://www.freecodecamp.org/",
        "w3schools": "https://www.w3schools.com/",
    }
}

def get_references(language: str) -> dict:
    """Get references for a specific language"""
    return KNOWLEDGE_BASE.get(language.lower(), KNOWLEDGE_BASE["general"])

def list_languages() -> list:
    """List all languages with references"""
    return list(KNOWLEDGE_BASE.keys())

def search_references(query: str) -> list:
    """Search for relevant references based on query"""
    results = []
    query_lower = query.lower()
    
    for lang, refs in KNOWLEDGE_BASE.items():
        if lang in query_lower:
            for name, url in refs.items():
                results.append(f"[{lang.upper()}] {name}: {url}")
    
    if not results:
        # Return general resources
        for name, url in KNOWLEDGE_BASE["general"].items():
            results.append(f"[General] {name}: {url}")
    
    return results
