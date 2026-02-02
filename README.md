# AIF-BIN Lite

**Free & Open Source** CLI for AI memory files.

[![Patent Pending](https://img.shields.io/badge/Patent-Pending-blue.svg)](https://www.terronex.dev)

| Version | Extension | Full Name | Format |
|---------|-----------|-----------|--------|
| v1 | `.aimf` | AI Memory Format | JSON |
| v2 | `.aif-bin` | AI Formatted - Binary | Binary (MessagePack) |

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## Documentation

- [Technical Whitepaper](docs/whitepaper.html) - Full specification and theory

## What is AIF-BIN?

A file format specification with two versions:
- **AIMF** (.aimf) - AI Memory Format, v1 JSON encoding for simplicity
- **AIF-BIN** (.aif-bin) - AI Formatted - Binary, v2 binary encoding for performance

A single `.aimf` or `.aif-bin` file contains:

- **Original document** — The source file preserved
- **Extracted content** — Text parsed into searchable chunks
- **Metadata** — Title, timestamps, checksums

This is the **free, open source** implementation. For semantic search, batch processing, and the desktop app, see [AIF-BIN Pro](https://github.com/terronexdev/aifbin-pro).

---

## Format Versions

This repository contains both format versions:

| Version | Extension | File | Full Name | Format |
|---------|-----------|------|-----------|--------|
| **v1** | `.aimf` | `aifbin_v1.py` | AI Memory Format | JSON |
| **v2** | `.aif-bin` | `aifbin_v2.py` | AI Formatted - Binary | Binary (MessagePack) |

### AIMF - AI Memory Format (v1)

Simple, human-readable JSON. Uses `.aimf` extension. Great for learning and debugging.

```json
{
  "version": "1.0.0-lite",
  "format": "json",
  "metadata": {
    "source_file": "sample.md",
    "created_at": "2026-01-30T10:00:00"
  },
  "chunks": [
    {"id": 0, "content": "...", "type": "text"}
  ],
  "original_raw": "# Original content..."
}
```

### AIF-BIN - AI Formatted - Binary (v2)

Compact binary format with MessagePack encoding. Uses `.aif-bin` extension. Used by AIF-BIN Pro and Studio.

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
```

### Windows (PowerShell/CMD)

```powershell
# v1 - No dependencies
python aifbin_v1.py --help

# v2 - Install msgpack first
pip install msgpack
python aifbin_v2.py --help
```

### Linux / macOS / WSL

```bash
# v1 - No dependencies
python3 aifbin_v1.py --help

# v2 - Install msgpack first
pip3 install msgpack                           # macOS
pip install msgpack --break-system-packages    # Debian/Ubuntu/WSL
python3 aifbin_v2.py --help
```

---

## Usage

### AIMF Commands (aifbin_v1.py)

**Windows:**
```powershell
python aifbin_v1.py migrate sample.md      # Convert to AIMF (JSON)
python aifbin_v1.py info sample.aimf       # View file info
python aifbin_v1.py chunks sample.aimf     # List chunks
python aifbin_v1.py extract sample.aimf    # Extract original content
```

**Linux / macOS / WSL:**
```bash
python3 aifbin_v1.py migrate sample.md      # Convert to AIMF (JSON)
python3 aifbin_v1.py info sample.aimf       # View file info
python3 aifbin_v1.py chunks sample.aimf     # List chunks
python3 aifbin_v1.py extract sample.aimf    # Extract original content
```

### AIF-BIN Commands (aifbin_v2.py)

**Windows:**
```powershell
python aifbin_v2.py migrate sample.md              # Convert to AIF-BIN (binary)
python aifbin_v2.py info sample.aif-bin            # View file info
python aifbin_v2.py chunks sample.aif-bin          # List chunks
python aifbin_v2.py extract sample.aif-bin         # Extract original content
python aifbin_v2.py upgrade sample.aimf            # Upgrade v1 to v2
```

**Linux / macOS / WSL:**
```bash
python3 aifbin_v2.py migrate sample.md              # Convert to AIF-BIN (binary)
python3 aifbin_v2.py info sample.aif-bin            # View file info
python3 aifbin_v2.py chunks sample.aif-bin          # List chunks
python3 aifbin_v2.py extract sample.aif-bin         # Extract original content
python3 aifbin_v2.py upgrade sample.aimf            # Upgrade v1 to v2
```

---

## Troubleshooting

### `error: externally-managed-environment` (Debian/Ubuntu/WSL)

This error occurs when `pip` tries to install packages system-wide in environments where Python packages are managed by the OS.

**Solution 1:** Use the `--break-system-packages` flag:
```bash
pip install msgpack --break-system-packages
```

**Solution 2:** Use a Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install msgpack
python3 aifbin_v2.py --help
# Deactivate when done:
deactivate
```

### `python3` not found on Windows

On Windows, use `python` instead of `python3`:
```powershell
python aifbin_v1.py --help
```

---

## Migrating from AIMF to AIF-BIN

### Why Migrate?

- **50% smaller files** — Binary format is more compact
- **Faster parsing** — Fixed-offset headers enable direct seeks
- **Checksums** — CRC64 verification for data integrity
- **Embeddings** — AIF-BIN supports vector embeddings for semantic search
- **Typed chunks** — TEXT, TABLE, IMAGE, AUDIO, VIDEO, CODE

### How to Migrate

**Option 1: Using the CLI (Recommended)**

```bash
# Windows
python aifbin_v2.py upgrade sample.aimf -o sample.aif-bin

# Linux / macOS / WSL
python3 aifbin_v2.py upgrade sample.aimf -o sample.aif-bin
```

**Option 2: Programmatically**

```python
from aifbin_v2 import migrate_from_v1

migrate_from_v1('sample.aimf', 'sample.aif-bin')
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
