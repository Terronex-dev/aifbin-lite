# AIF-BIN Lite

Free and open source CLI for AI memory files.

## Installation

```bash
# Clone the repo
git clone https://github.com/terronexdev/aifbin-lite.git
cd aifbin-lite

# No dependencies required — just Python 3.8+
python3 aifbin.py --help
```

## Commands

```bash
# Convert markdown to AIF-BIN
python3 aifbin.py migrate notes.md

# View file info
python3 aifbin.py info notes.aif-bin

# Extract original content
python3 aifbin.py extract notes.aif-bin

# List chunks
python3 aifbin.py chunks notes.aif-bin
```

## Output Format

Lite uses v1 JSON format — human-readable and easy to inspect:

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

Need more power? AIF-BIN Pro includes:

- Semantic search — find by meaning, not keywords
- v2 binary format — 50% smaller, faster
- Batch processing — convert entire directories
- Watch mode — auto-sync on file changes
- Web Inspector — visual file analyzer
- 5 embedding models — choose quality vs speed

Get Pro: [aifbin.com](https://aifbin.com)

## License

MIT License — free to use, modify, and distribute.

---

AIF-BIN™ © 2026 Terronex.dev
