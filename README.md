
## 📦 Installation

```bash
git clone https://github.com/greg-gzillion/rustypycraw.git
cd rustypycraw
python3 -m venv .venv
source .venv/bin/activate
pip install -e . maturin requests groq
cd rustypycraw-core
maturin develop --release
cd ..
```

## 🚀 Quick Start

```bash
./rustypycraw --list-models
./rustypycraw ~/dev/TX --stats
./rustypycraw ~/dev/TX --search "collateral"
./rustypycraw ~/dev/TX --pinch
./rustypycraw --groq --ask 'What is PHNX?'
```

## 🤖 Supported Models

| Model | Provider | Speed | Best For |
|-------|----------|-------|----------|
| llama-3.3-70b | Groq | 1-2 sec | General Q&A |
| deepseek-coder:6.7b | Ollama | 30-60 sec | Code generation |
| codellama:7b | Ollama | 30-60 sec | Rust debugging |
| llama3.2:3b | Ollama | 15-30 sec | Fast local |

## 📝 License

MIT
