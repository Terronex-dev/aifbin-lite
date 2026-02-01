#!/usr/bin/env python3
"""
Migrate AIF-BIN v1 (JSON) to v2 (Binary)
========================================

Usage:
    python3 migrate_v1_to_v2.py input.aif-bin output.aif-bin
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aifbin_v2 import AifBinV2Writer


def migrate_v1_to_v2(v1_path: str, v2_path: str) -> None:
    """Convert a v1 JSON AIF-BIN file to v2 binary format."""
    
    # Load v1 file
    with open(v1_path, 'r', encoding='utf-8') as f:
        v1_data = json.load(f)
    
    # Verify it's a v1 file
    version = v1_data.get('version', '')
    if not version.startswith('1.'):
        print(f"Warning: File version is '{version}', expected '1.x'")
    
    # Create v2 writer
    writer = AifBinV2Writer()
    
    # Set metadata
    v1_meta = v1_data.get('metadata', {})
    writer.set_metadata({
        'title': v1_meta.get('source_file', 'Untitled'),
        'created': v1_meta.get('created_at'),
        'source_hash': v1_meta.get('content_hash'),
        'migrated_from': f'v1 ({version})',
        'original_chunk_count': v1_meta.get('chunk_count', 0)
    })
    
    # Set original content if present
    if 'original_raw' in v1_data:
        raw = v1_data['original_raw']
        if isinstance(raw, str):
            raw = raw.encode('utf-8')
        writer.set_original_raw(raw)
    
    # Add chunks
    for chunk in v1_data.get('chunks', []):
        content = chunk.get('content', '')
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        chunk_type = chunk.get('type', 'text').upper()
        if chunk_type not in ['TEXT', 'TABLE', 'IMAGE', 'AUDIO', 'VIDEO', 'CODE']:
            chunk_type = 'TEXT'
        
        writer.add_chunk(chunk_type, content, {
            'v1_id': chunk.get('id'),
            'v1_type': chunk.get('type')
        })
    
    # Build and write v2 file
    v2_data = writer.build()
    with open(v2_path, 'wb') as f:
        f.write(v2_data)
    
    # Report
    v1_size = Path(v1_path).stat().st_size
    v2_size = Path(v2_path).stat().st_size
    reduction = (1 - v2_size / v1_size) * 100 if v1_size > 0 else 0
    
    print(f"Migrated: {v1_path} -> {v2_path}")
    print(f"  v1 size: {v1_size:,} bytes")
    print(f"  v2 size: {v2_size:,} bytes")
    print(f"  Reduction: {reduction:.1f}%")


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 migrate_v1_to_v2.py <input.aif-bin> <output.aif-bin>")
        sys.exit(1)
    
    v1_path = sys.argv[1]
    v2_path = sys.argv[2]
    
    if not Path(v1_path).exists():
        print(f"Error: File not found: {v1_path}")
        sys.exit(1)
    
    migrate_v1_to_v2(v1_path, v2_path)


if __name__ == '__main__':
    main()
