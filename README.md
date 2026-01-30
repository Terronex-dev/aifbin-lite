# AIF-BIN Lite

**Free & Open Source CLI for AI Memory Files**

AIF-BIN (AI-Interchange Binary) is a file format for storing AI-ready memories with semantic chunks. Think of it as a smarter way to store notes, documents, and knowledge for AI systems.

## Installation

```bash
# Clone the repo
git clone https://github.com/terronexdev/aifbin-lite.git
cd aifbin-lite

# No dependencies required! Just Python 3.8+
python3 aifbin.py --help
```

## Quick Start

```bash
# Convert a markdown file to AIF-BIN
python3 aifbin.py migrate notes.md

# View file info
python3 aifbin.py info notes.aif-bin

# Extract original content
python3 aifbin.py extract notes.aif-bin

# List chunks
python3 aifbin.py chunks notes.aif-bin
```

## Commands

| Command | Description |
|---------|-------------|
| `migrate <file>` | Convert markdown to AIF-BIN |
| `info <file>` | Show file metadata |
| `extract <file>` | Recover original content |
| `chunks <file>` | List content chunks |

## Format

Lite uses **v1 JSON format** — human-readable and easy to inspect:

```json
{
  "version": "1.0.0-lite",
  "format": "json",
  "metadata": {
    "source_file": "notes.md",
    "created_at": "2026-01-30T10:00:00",
    "chunk_count": 3
  },
  "chunks": [
    {"id": 0, "content": "...", "type": "text"}
  ],
  "original_raw": "# Original content..."
}
```

## Upgrade to Pro

Need more power? **AIF-BIN Pro** includes:

- 🔍 **Semantic Search** — Find memories by meaning, not keywords
- ⚡ **v2 Binary Format** — 50% smaller, faster parsing
- 📦 **Batch Processing** — Convert entire directories in parallel
- 👁️ **Watch Mode** — Auto-sync when files change
- 🖥️ **Web Inspector** — Visual GUI for exploring files
- 🧠 **5 Embedding Models** — Choose quality vs speed

**Get Pro:** [https://aifbin.dev](https://aifbin.dev)

## Use Cases

- **Personal Knowledge Base** — Store notes with semantic chunks
- **AI Context** — Pre-process documents for LLM consumption  
- **Documentation** — Archive docs in a searchable format
- **Research** — Chunk papers and articles for analysis

## License

MIT License — Free to use, modify, and distribute.

## Links

- 🏠 **Website:** [aifbin.dev](https://aifbin.dev)
- 💎 **Pro Version:** [aifbin.dev](https://aifbin.dev)
- 🐛 **Issues:** [GitHub Issues](https://github.com/terronexdev/aifbin-lite/issues)

---

Made with 🐾 by [Terronex.dev](https://terronex.dev)
