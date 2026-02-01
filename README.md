# AIF-BIN Lite

**Free & Open Source** CLI for AI memory files.

**AIF-BIN** = AI Formatted - Binary | **AIMF** = AI Memory Format

Both `.aif-bin` and `.aimf` extensions are synonymous and fully interchangeable.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## What is AIF-BIN?

AIF-BIN (AI Formatted - Binary), also known as AIMF (AI Memory Format), is a file format that makes documents AI-native. A single `.aif-bin` or `.aimf` file contains:

- **Original document** — The source file preserved
- **Extracted content** — Text parsed into searchable chunks
- **Metadata** — Title, timestamps, checksums

This is the **free, open source** implementation. For semantic search, batch processing, and the desktop app, see [AIF-BIN Pro](https://github.com/terronexdev/aifbin-pro).

---

## Format Versions

This repository contains both format versions:

| Version | File | Format | Features |
|---------|------|--------|----------|
| **v1** | `aifbin_v1.py` | JSON | Human-readable, simple |
| **v2** | `aifbin_v2.py` | Binary | 50% smaller, faster, embeddings |

### v1 JSON Format (Lite)

Simple, human-readable JSON. Great for learning and debugging.

```json
{
  "version": "1.0.0-lite",
  "format": "json",
  "metadata": {
    "source_file": "notes.md",
    "created_at": "2026-01-30T10:00:00"
  },
  "chunks": [
    {"id": 0, "content": "...", "type": "text"}
  ],
  "original_raw": "# Original content..."
}
```

### v2 Binary Format (Pro)

Compact binary format with MessagePack encoding. Used by AIF-BIN Pro and Studio.

```
[Header: 64 bytes]
  Magic: "AIFBIN\x00\x01"
  Version, Offsets, Size

[Metadata Section]
  MessagePack blob

[Original Raw Section]
  Preserved source file

[Content Chunks]
  Typed chunks with optional embeddings

[Footer]
  Index + CRC64 Checksum
```

---

## Installation

```bash
# Clone the repo
git clone https://github.com/terronexdev/aifbin-lite.git
cd aifbin-lite

# No dependencies for v1
python3 aifbin_v1.py --help

# For v2, install msgpack
pip install msgpack
python3 aifbin_v2.py --help
```

---

## Usage

### v1 Commands (aifbin_v1.py)

```bash
# Convert markdown to AIF-BIN (v1 JSON)
python3 aifbin_v1.py migrate notes.md

# View file info
python3 aifbin_v1.py info notes.aif-bin

# Extract original content
python3 aifbin_v1.py extract notes.aif-bin

# List chunks
python3 aifbin_v1.py chunks notes.aif-bin
```

### v2 Commands (aifbin_v2.py)

```bash
# Convert markdown to AIF-BIN (v2 binary)
python3 aifbin_v2.py migrate notes.md -o output/

# View file info
python3 aifbin_v2.py info notes.aif-bin

# Extract original content
python3 aifbin_v2.py extract notes.aif-bin

# Verify checksum
python3 aifbin_v2.py verify notes.aif-bin
```

---

## Migrating from v1 to v2

### Why Migrate?

- **50% smaller files** — Binary format is more compact
- **Faster parsing** — Fixed-offset headers enable direct seeks
- **Checksums** — CRC64 verification for data integrity
- **Embeddings** — v2 supports vector embeddings for semantic search
- **Typed chunks** — TEXT, TABLE, IMAGE, AUDIO, VIDEO, CODE

### How to Migrate

```python
import json
from aifbin_v2 import AifBinV2Writer

# Load v1 file
with open('notes.aif-bin', 'r') as f:
    v1_data = json.load(f)

# Create v2 file
writer = AifBinV2Writer()
writer.set_metadata({
    'title': v1_data['metadata'].get('source_file', 'Untitled'),
    'created': v1_data['metadata'].get('created_at'),
    'migrated_from': 'v1'
})

# Set original content
if 'original_raw' in v1_data:
    writer.set_original_raw(v1_data['original_raw'].encode('utf-8'))

# Add chunks
for chunk in v1_data.get('chunks', []):
    writer.add_chunk('TEXT', chunk['content'].encode('utf-8'), {
        'id': chunk.get('id'),
        'type': chunk.get('type', 'text')
    })

# Write v2 file
v2_data = writer.build()
with open('notes_v2.aif-bin', 'wb') as f:
    f.write(v2_data)
```

See `examples/migrate_v1_to_v2.py` for a complete migration script.

---

## Examples

| File | Description |
|------|-------------|
| `examples/quickstart_v1.py` | Basic v1 usage |
| `examples/quickstart_v2.py` | Basic v2 usage |
| `examples/migrate_v1_to_v2.py` | Migration script |

---

## Related Projects

| Project | Description |
|---------|-------------|
| [AIF-BIN Lite](https://github.com/terronexdev/aifbin-lite) | Free CLI (this repo) |
| [AIF-BIN Pro](https://github.com/terronexdev/aifbin-pro) | Pro CLI + Inspector |
| [AIF-BIN Studio](https://github.com/terronexdev/aifbin-studio) | Full desktop app |

---

## Upgrade to Pro

Need more power? [AIF-BIN Pro](https://github.com/terronexdev/aifbin-pro) includes:

- Semantic search (find by meaning)
- Batch processing (convert directories)
- Watch mode (auto-sync on changes)
- Web Inspector (visual analyzer)
- 5 embedding models

---

## Legal Notices

- This software is provided under the **MIT License** (see [LICENSE](LICENSE)).
- **AIF-BIN** is a trademark of Terronex.dev.
- See [NOTICE](NOTICE) for additional information.

---

## Links

- Website: [terronex.dev/aifbin](https://terronex.dev/aifbin/)
- Pro: [github.com/terronexdev/aifbin-pro](https://github.com/terronexdev/aifbin-pro)
- Studio: [github.com/terronexdev/aifbin-studio](https://github.com/terronexdev/aifbin-studio)
- Support: support@terronex.dev

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

(c) 2026 Terronex.dev. All rights reserved.
