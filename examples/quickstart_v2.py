#!/usr/bin/env python3
"""
AIF-BIN v2 Quickstart
=====================

Basic example of creating and reading v2 binary format.
Requires: pip install msgpack
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from aifbin_v2 import AifBinV2Writer, AifBinV2Reader


def main():
    # Create a v2 AIF-BIN file
    writer = AifBinV2Writer()
    
    # Set metadata
    writer.set_metadata({
        'title': 'My Notes',
        'author': 'Example User',
        'tags': ['demo', 'quickstart']
    })
    
    # Set original content
    original = """# My Notes

This is a sample document for AIF-BIN v2.

## Features

- Binary format (smaller)
- CRC64 checksums
- Typed chunks
"""
    writer.set_original_raw(original.encode('utf-8'))
    
    # Add content chunks
    writer.add_chunk('TEXT', b'This is a sample document for AIF-BIN v2.', {
        'section': 'intro'
    })
    writer.add_chunk('TEXT', b'Binary format, CRC64 checksums, typed chunks.', {
        'section': 'features'
    })
    
    # Build and save
    output = "sample_v2.aif-bin"
    data = writer.build()
    with open(output, 'wb') as f:
        f.write(data)
    print(f"Created: {output} ({len(data):,} bytes)")
    
    # Read it back
    reader = AifBinV2Reader(output)
    info = reader.get_info()
    
    print(f"\nVersion: {info['version']}")
    print(f"Title: {info['metadata'].get('title')}")
    print(f"Chunks: {info['chunk_count']}")
    print(f"Checksum valid: {info['checksum_valid']}")
    
    # Extract original
    original_back = reader.get_original_raw()
    if original_back:
        print(f"\nOriginal content ({len(original_back)} bytes):")
        print(original_back.decode('utf-8')[:200])
    
    # Clean up
    Path(output).unlink()
    print("\nCleaned up test file.")


if __name__ == '__main__':
    main()
