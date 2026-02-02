#!/usr/bin/env python3
"""
AIF-BIN Lite — Free & Open Source CLI
======================================
Basic AI memory file management.

For semantic search, batch processing, watch mode, and the 
Web Inspector, upgrade to AIF-BIN Pro: https://aifbin.dev

MIT License — Free to use, modify, and distribute.
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

__version__ = "1.0.0"

# ============================================================
# V1 JSON FORMAT (Lite uses JSON, Pro uses binary)
# ============================================================

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks if chunks else [text]

def create_aifbin_lite(source_path: str, output_path: str) -> Dict[str, Any]:
    """Create an AIF-BIN file (v1 JSON format, no embeddings)."""
    # Try UTF-8 first, fall back to other encodings (handles Windows BOM, etc.)
    content = None
    for encoding in ['utf-8-sig', 'utf-8', 'utf-16', 'latin-1']:
        try:
            with open(source_path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if content is None:
        raise ValueError(f"Could not decode {source_path} with any supported encoding")
    
    text_chunks = chunk_text(content)
    
    aifbin_data = {
        "version": "1.0.0-lite",
        "format": "json",
        "metadata": {
            "source_file": str(source_path),
            "created_at": datetime.now().isoformat(),
            "chunk_count": len(text_chunks),
            "file_hash": hashlib.md5(content.encode()).hexdigest()
        },
        "chunks": [
            {
                "id": i,
                "content": chunk,
                "type": "text"
            }
            for i, chunk in enumerate(text_chunks)
        ],
        "original_raw": content
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(aifbin_data, f, indent=2)
    
    return {
        "source": source_path,
        "output": output_path,
        "chunks": len(text_chunks),
        "size": os.path.getsize(output_path)
    }

def load_aimf(filepath: str) -> Dict[str, Any]:
    """Load an AIMF file (v1 JSON format only)."""
    # First check if it's binary (v2)
    with open(filepath, 'rb') as f:
        first_bytes = f.read(8)
    
    if first_bytes.startswith(b'AIFBIN'):
        print("⚠️  This is a v2 binary file (.aif-bin). Use AIF-BIN Pro to read it.")
        print("   Lite only supports v1 JSON files (.aimf)")
        print("   Get Pro: https://aifbin.dev")
        sys.exit(1)
    
    # It's JSON, load normally
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# ============================================================
# COMMANDS
# ============================================================

def cmd_migrate(args):
    """Convert a markdown file to AIMF format (v1 JSON)."""
    source = Path(args.source)
    
    if not source.exists():
        print(f"❌ File not found: {source}")
        sys.exit(1)
    
    if source.is_dir():
        print("❌ Lite version only supports single files.")
        print("   For batch processing, upgrade to Pro: https://aifbin.dev")
        sys.exit(1)
    
    if args.output:
        output = Path(args.output)
    else:
        output = source.with_suffix('.aimf')
    
    print(f"📄 Converting: {source.name}")
    result = create_aifbin_lite(str(source), str(output))
    print(f"✅ Created: {output.name} ({result['chunks']} chunks, {result['size']} bytes)")
    print(f"   Format: AIMF v1 (JSON, human-readable)")

def cmd_info(args):
    """Show information about an AIMF file."""
    filepath = Path(args.file)
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)
    
    data = load_aimf(str(filepath))
    meta = data.get('metadata', {})
    chunks = data.get('chunks', [])
    
    print(f"\n📦 AIMF File Info (v1 JSON)")
    print(f"{'─' * 40}")
    print(f"  File:      {filepath.name}")
    print(f"  Version:   {data.get('version', 'unknown')}")
    print(f"  Format:    {data.get('format', 'json')}")
    print(f"  Created:   {meta.get('created_at', 'Unknown')}")
    print(f"  Source:    {meta.get('source_file', 'Unknown')}")
    print(f"  Chunks:    {len(chunks)}")
    print(f"  Has Raw:   {'Yes' if data.get('original_raw') else 'No'}")
    print(f"\n  💡 Upgrade to .aif-bin (v2) for semantic search")
    print()

def cmd_extract(args):
    """Extract original content from an AIF-BIN file."""
    filepath = Path(args.file)
    data = load_aimf(str(filepath))
    
    if data.get('original_raw'):
        content = data['original_raw']
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Extracted to {args.output}")
        else:
            print(content)
    else:
        print("❌ No original content found in file")
        sys.exit(1)

def cmd_chunks(args):
    """List chunks in an AIMF file."""
    filepath = Path(args.file)
    data = load_aimf(str(filepath))
    chunks = data.get('chunks', [])
    
    print(f"\n📦 Chunks in {filepath.name} (AIMF v1)")
    print(f"{'─' * 50}")
    
    for chunk in chunks[:args.limit]:
        content = chunk.get('content', '')[:100]
        print(f"\n  [{chunk.get('id', '?')}] {chunk.get('type', 'text')}")
        print(f"      {content}...")
    
    if len(chunks) > args.limit:
        print(f"\n  ... and {len(chunks) - args.limit} more chunks")
        print(f"  (use --limit to see more)")

def cmd_version(args):
    """Show version information."""
    print(f"""
AIF-BIN Lite v{__version__}
Free & Open Source CLI for AI Memory Files

📦 Format: AIMF v1 (.aimf) — JSON, human-readable
📄 License: MIT

Upgrade path:
  .aimf (v1 JSON) → .aif-bin (v2 binary) → semantic search

For advanced features, upgrade to Pro:
  • Semantic search (find by meaning)
  • v2 binary format (smaller, faster)  
  • Batch parallel processing
  • Watch mode (auto-sync)
  • Web Inspector GUI

🔗 https://aifbin.dev
""")

# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        prog='aifbin-lite',
        description='AIF-BIN Lite — Free AI Memory File CLI',
        epilog='For Pro features (search, batch, watch): https://aifbin.dev'
    )
    parser.add_argument('--version', '-v', action='store_true', help='Show version')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # migrate
    p_migrate = subparsers.add_parser('migrate', help='Convert file to AIMF (v1 JSON)')
    p_migrate.add_argument('source', help='Source markdown file')
    p_migrate.add_argument('-o', '--output', help='Output file (default: same name with .aimf)')
    
    # info
    p_info = subparsers.add_parser('info', help='Show file info')
    p_info.add_argument('file', help='AIMF file (.aimf)')
    
    # extract
    p_extract = subparsers.add_parser('extract', help='Extract original content')
    p_extract.add_argument('file', help='AIMF file (.aimf)')
    p_extract.add_argument('-o', '--output', help='Output file (default: stdout)')
    
    # chunks
    p_chunks = subparsers.add_parser('chunks', help='List chunks')
    p_chunks.add_argument('file', help='AIMF file (.aimf)')
    p_chunks.add_argument('-l', '--limit', type=int, default=10, help='Max chunks to show')
    
    args = parser.parse_args()
    
    if args.version:
        cmd_version(args)
        return
    
    if not args.command:
        parser.print_help()
        print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AIF-BIN Lite — Free & Open Source
  
  📦 Output: .aimf (v1 JSON, human-readable)
  
  ✅ Included: migrate, info, extract, chunks
  
  🔒 Pro Only: search, batch, watch, .aif-bin (v2)
     Upgrade: https://aifbin.dev
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        return
    
    commands = {
        'migrate': cmd_migrate,
        'info': cmd_info,
        'extract': cmd_extract,
        'chunks': cmd_chunks,
    }
    
    commands[args.command](args)

if __name__ == '__main__':
    main()
