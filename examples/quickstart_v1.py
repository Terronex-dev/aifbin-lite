#!/usr/bin/env python3
"""
AIF-BIN v1 Quickstart
=====================

Basic example of creating and reading v1 JSON format.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from aifbin_v1 import create_aifbin_lite, load_aifbin


def main():
    # Create a sample markdown file
    sample_md = "sample.md"
    with open(sample_md, 'w') as f:
        f.write("""# My Notes

This is a sample document for AIF-BIN.

## Section 1

Some important information here.

## Section 2

More content to demonstrate chunking.
""")
    
    # Convert to AIF-BIN v1
    output = "sample.aif-bin"
    result = create_aifbin_lite(sample_md, output)
    print(f"Created: {output}")
    print(f"Chunks: {len(result.get('chunks', []))}")
    
    # Read it back
    data = load_aifbin(output)
    print(f"\nMetadata: {data['metadata']}")
    print(f"\nFirst chunk: {data['chunks'][0]['content'][:100]}...")
    
    # Clean up
    Path(sample_md).unlink()
    Path(output).unlink()
    print("\nCleaned up test files.")


if __name__ == '__main__':
    main()
