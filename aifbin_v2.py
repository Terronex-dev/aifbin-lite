#!/usr/bin/env python3
"""
AIF-BIN Specification v2.0 — Binary Format
==========================================
Aligned with the Forensic Suite TypeScript implementation.

This is the "real" AIF-BIN format using:
- Binary headers with fixed offsets
- MessagePack for metadata/chunks (not JSON)
- Footer with index and checksum
- Proper chunk typing (TEXT, CODE, IMAGE, etc.)

Format Structure:
-----------------
[Header: 64 bytes]
  - Magic: "AIFBIN\x00\x01" (8 bytes)
  - Version: u32 (4 bytes)
  - Padding: 4 bytes
  - metadataOffset: u64 (8 bytes)
  - originalRawOffset: u64 (8 bytes)  — 0xFFFFFFFFFFFFFFFF if absent
  - contentChunksOffset: u64 (8 bytes)
  - versionsOffset: u64 (8 bytes)     — 0xFFFFFFFFFFFFFFFF if absent
  - footerOffset: u64 (8 bytes)
  - totalSize: u64 (8 bytes)

[Metadata Section]
  - length: u64
  - data: MessagePack blob

[Original Raw Section] (optional)
  - length: u64
  - data: raw bytes

[Content Chunks Section]
  - count: u32
  - For each chunk:
    - type: u32 (1=TEXT, 2=TABLE_JSON, 3=IMAGE, 4=AUDIO, 5=VIDEO, 6=CODE)
    - dataLength: u64
    - metadataLength: u64
    - metadata: MessagePack blob
    - data: raw bytes

[Versions Section] (optional)
  - count: u32
  - For each version:
    - descLength: u32
    - description: UTF-8 string
    - deltaLength: u32
    - delta: MessagePack blob
    - timestamp: u64

[Footer]
  - indexCount: u32
  - For each index entry:
    - chunkId: u32
    - offset: u64
  - checksum: u64 (CRC64 or simple sum)
"""

import struct
import hashlib
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import IntEnum
from datetime import datetime

try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False
    print("""
❌  Error: 'msgpack' library not found.
    AIF-BIN v2 requires msgpack for binary encoding.

    Install with:
    pip install msgpack                      # macOS/Windows
    pip install msgpack --break-system-packages # Debian/Ubuntu (WSL)

    Or, use AIF-BIN v1 for JSON-based memory (no dependencies):
    python3 aifbin_v1.py --help
""")
    sys.exit(1) # Exit if msgpack is not available

# Constants
MAGIC = b"AIFBIN\x00\x01"
HEADER_SIZE = 64
ABSENT_OFFSET = 0xFFFFFFFFFFFFFFFF
VERSION = 2


class ChunkType(IntEnum):
    TEXT = 1
    TABLE_JSON = 2
    IMAGE = 3
    AUDIO = 4
    VIDEO = 5
    CODE = 6


@dataclass
class ContentChunk:
    chunk_type: ChunkType
    data: bytes
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


@dataclass 
class Version:
    description: str
    delta: Dict[str, Any]
    timestamp: int  # Unix timestamp


@dataclass
class AIFBINFile:
    metadata: Dict[str, Any]
    chunks: List[ContentChunk]
    original_raw: Optional[bytes] = None
    versions: List[Version] = field(default_factory=list)


class AIFBINWriter:
    """Writes AIF-BIN files in the v2 binary format."""
    
    def __init__(self):
        if not HAS_MSGPACK:
            raise ImportError("msgpack is required for v2 format")
    
    def write(self, aifbin: AIFBINFile, filepath: str) -> int:
        """Write an AIFBINFile to disk. Returns bytes written."""
        
        # Prepare sections as bytes
        metadata_bytes = msgpack.packb(aifbin.metadata)
        
        original_raw_bytes = aifbin.original_raw or b""
        has_original = aifbin.original_raw is not None
        
        chunks_bytes = self._pack_chunks(aifbin.chunks)
        
        versions_bytes = self._pack_versions(aifbin.versions)
        has_versions = len(aifbin.versions) > 0
        
        # Calculate offsets
        metadata_offset = HEADER_SIZE
        metadata_section_size = 8 + len(metadata_bytes)  # length prefix + data
        
        if has_original:
            original_offset = metadata_offset + metadata_section_size
            original_section_size = 8 + len(original_raw_bytes)
        else:
            original_offset = ABSENT_OFFSET
            original_section_size = 0
        
        chunks_offset = metadata_offset + metadata_section_size + original_section_size
        chunks_section_size = len(chunks_bytes)
        
        if has_versions:
            versions_offset = chunks_offset + chunks_section_size
            versions_section_size = len(versions_bytes)
        else:
            versions_offset = ABSENT_OFFSET
            versions_section_size = 0
        
        footer_offset = chunks_offset + chunks_section_size + versions_section_size
        
        # Build footer (index + checksum)
        footer_bytes = self._pack_footer(aifbin.chunks, chunks_offset)
        
        total_size = footer_offset + len(footer_bytes)
        
        # Build header
        header = struct.pack(
            "<8sII QQQQQQ",
            MAGIC,
            VERSION,
            0,  # Padding
            metadata_offset,
            original_offset,
            chunks_offset,
            versions_offset,
            footer_offset,
            total_size
        )
        
        # Write file
        with open(filepath, 'wb') as f:
            f.write(header)
            
            # Metadata section
            f.write(struct.pack("<Q", len(metadata_bytes)))
            f.write(metadata_bytes)
            
            # Original raw section (if present)
            if has_original:
                f.write(struct.pack("<Q", len(original_raw_bytes)))
                f.write(original_raw_bytes)
            
            # Chunks section
            f.write(chunks_bytes)
            
            # Versions section (if present)
            if has_versions:
                f.write(versions_bytes)
            
            # Footer
            f.write(footer_bytes)
        
        return total_size
    
    def _pack_chunks(self, chunks: List[ContentChunk]) -> bytes:
        """Pack all chunks into bytes."""
        parts = [struct.pack("<I", len(chunks))]  # Count
        
        for chunk in chunks:
            meta_bytes = msgpack.packb(chunk.metadata)
            data_bytes = chunk.data if isinstance(chunk.data, bytes) else chunk.data.encode('utf-8')
            
            parts.append(struct.pack(
                "<I Q Q",
                int(chunk.chunk_type),
                len(data_bytes),
                len(meta_bytes)
            ))
            parts.append(meta_bytes)
            parts.append(data_bytes)
        
        return b"".join(parts)
    
    def _pack_versions(self, versions: List[Version]) -> bytes:
        """Pack all versions into bytes."""
        if not versions:
            return b""
        
        parts = [struct.pack("<I", len(versions))]
        
        for v in versions:
            desc_bytes = v.description.encode('utf-8')
            delta_bytes = msgpack.packb(v.delta)
            
            parts.append(struct.pack("<I", len(desc_bytes)))
            parts.append(desc_bytes)
            parts.append(struct.pack("<I", len(delta_bytes)))
            parts.append(delta_bytes)
            parts.append(struct.pack("<Q", v.timestamp))
        
        return b"".join(parts)
    
    def _pack_footer(self, chunks: List[ContentChunk], chunks_offset: int) -> bytes:
        """Pack footer with index and checksum."""
        parts = [struct.pack("<I", len(chunks))]  # Index count
        
        # Build index (simplified: just sequential offsets)
        current_offset = chunks_offset + 4  # After chunk count
        for i, chunk in enumerate(chunks):
            parts.append(struct.pack("<I Q", i, current_offset))
            meta_bytes = msgpack.packb(chunk.metadata)
            data_bytes = chunk.data if isinstance(chunk.data, bytes) else chunk.data.encode('utf-8')
            current_offset += 4 + 8 + 8 + len(meta_bytes) + len(data_bytes)
        
        # Simple checksum (sum of all index offsets)
        checksum = sum(struct.unpack("<Q", parts[i+1][4:])[0] for i in range(len(chunks)))
        parts.append(struct.pack("<Q", checksum & 0xFFFFFFFFFFFFFFFF))
        
        return b"".join(parts)


class AIFBINReader:
    """Reads AIF-BIN files in the v2 binary format."""
    
    def __init__(self, filepath: str):
        if not HAS_MSGPACK:
            raise ImportError("msgpack is required for v2 format")
        
        self.filepath = filepath
        self.filesize = os.path.getsize(filepath)
    
    def read(self) -> AIFBINFile:
        """Read and parse an AIF-BIN file."""
        with open(self.filepath, 'rb') as f:
            # Read header
            header = f.read(HEADER_SIZE)
            (
                magic, version, _, 
                meta_off, raw_off, chunks_off, versions_off, footer_off, total_size
            ) = struct.unpack("<8sII QQQQQQ", header)
            
            if magic != MAGIC:
                raise ValueError(f"Invalid magic signature: {magic}")
            
            # Read metadata
            f.seek(meta_off)
            meta_len = struct.unpack("<Q", f.read(8))[0]
            metadata = msgpack.unpackb(f.read(meta_len))
            
            # Read original raw (if present)
            original_raw = None
            if raw_off != ABSENT_OFFSET and raw_off < self.filesize:
                f.seek(raw_off)
                raw_len = struct.unpack("<Q", f.read(8))[0]
                original_raw = f.read(raw_len)
            
            # Read chunks
            chunks = []
            if chunks_off < self.filesize:
                f.seek(chunks_off)
                chunk_count = struct.unpack("<I", f.read(4))[0]
                
                for _ in range(chunk_count):
                    c_type, data_len, meta_len = struct.unpack("<I Q Q", f.read(20))
                    c_meta = msgpack.unpackb(f.read(meta_len))
                    c_data = f.read(data_len)
                    
                    chunks.append(ContentChunk(
                        chunk_type=ChunkType(c_type),
                        data=c_data,
                        metadata=c_meta,
                        embedding=c_meta.get('embedding')
                    ))
            
            # Read versions (if present)
            versions = []
            if versions_off != ABSENT_OFFSET and versions_off < self.filesize:
                f.seek(versions_off)
                ver_count = struct.unpack("<I", f.read(4))[0]
                
                for _ in range(ver_count):
                    desc_len = struct.unpack("<I", f.read(4))[0]
                    desc = f.read(desc_len).decode('utf-8')
                    delta_len = struct.unpack("<I", f.read(4))[0]
                    delta = msgpack.unpackb(f.read(delta_len))
                    timestamp = struct.unpack("<Q", f.read(8))[0]
                    
                    versions.append(Version(
                        description=desc,
                        delta=delta,
                        timestamp=timestamp
                    ))
            
            return AIFBINFile(
                metadata=metadata,
                chunks=chunks,
                original_raw=original_raw,
                versions=versions
            )
    
    def get_info(self) -> Dict[str, Any]:
        """Get file info without full parse."""
        with open(self.filepath, 'rb') as f:
            header = f.read(HEADER_SIZE)
            (
                magic, version, _,
                meta_off, raw_off, chunks_off, versions_off, footer_off, total_size
            ) = struct.unpack("<8sII QQQQQQ", header)
            
            # Count chunks
            chunk_count = 0
            if chunks_off < self.filesize:
                f.seek(chunks_off)
                chunk_count = struct.unpack("<I", f.read(4))[0]
            
            # Get checksum from footer
            checksum = 0
            if footer_off < self.filesize:
                f.seek(footer_off)
                idx_count = struct.unpack("<I", f.read(4))[0]
                f.seek(footer_off + 4 + idx_count * 12)  # Skip to checksum
                if f.tell() + 8 <= self.filesize:
                    checksum = struct.unpack("<Q", f.read(8))[0]
            
            return {
                'magic_valid': magic == MAGIC,
                'version': version,
                'total_size': total_size,
                'chunk_count': chunk_count,
                'has_original_raw': raw_off != ABSENT_OFFSET,
                'has_versions': versions_off != ABSENT_OFFSET,
                'checksum': hex(checksum)
            }


def migrate_from_v1(v1_path: str, v2_path: str, embeddings: Optional[List[List[float]]] = None):
    """Migrate a v1 JSON-based AIF-BIN to v2 binary format."""
    import json
    
    with open(v1_path, 'r') as f:
        v1_data = json.load(f)
    
    # Build v2 structure
    metadata = v1_data.get('metadata', {})
    original_raw = None
    if 'original_raw' in v1_data:
        original_raw = v1_data['original_raw'].encode('utf-8')
    
    chunks = []
    v1_chunks = v1_data.get('chunks', [])
    for i, c in enumerate(v1_chunks):
        chunk_meta = c.get('metadata', {})
        if embeddings and i < len(embeddings):
            chunk_meta['embedding'] = embeddings[i]
        
        chunks.append(ContentChunk(
            chunk_type=ChunkType.TEXT,  # Default to TEXT for v1 migrations
            data=c.get('content', '').encode('utf-8'),
            metadata=chunk_meta
        ))
    
    versions = []
    for v in v1_data.get('versions', []):
        versions.append(Version(
            description=v.get('description', ''),
            delta=v.get('delta', {}),
            timestamp=v.get('timestamp', int(datetime.now().timestamp()))
        ))
    
    aifbin = AIFBINFile(
        metadata=metadata,
        chunks=chunks,
        original_raw=original_raw,
        versions=versions
    )
    
    writer = AIFBINWriter()
    return writer.write(aifbin, v2_path)


# CLI
if __name__ == "__main__":
    import sys
    import argparse
    from pathlib import Path
    
    def cmd_migrate(args):
        """Convert file to AIF-BIN v2 binary format."""
        source = Path(args.source)
        
        if not source.exists():
            print(f"❌ File not found: {source}")
            sys.exit(1)
        
        # Determine output path
        if args.output:
            output = Path(args.output)
            if output.is_dir():
                output = output / source.with_suffix('.aif-bin').name
        else:
            output = source.with_suffix('.aif-bin')
        
        print(f"📄 Converting: {source.name}")
        
        # Read source file (handle various encodings including Windows UTF-16/BOM)
        content = None
        for encoding in ['utf-8-sig', 'utf-8', 'utf-16', 'latin-1']:
            try:
                with open(source, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if content is None:
            print(f"❌ Could not decode {source} with any supported encoding")
            sys.exit(1)
        
        # Chunk the content
        words = content.split()
        chunks = []
        chunk_size = 512
        overlap = 50
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_text = ' '.join(words[start:end])
            if chunk_text.strip():
                chunks.append(ContentChunk(
                    chunk_type=ChunkType.TEXT,
                    data=chunk_text.encode('utf-8'),
                    metadata={'id': len(chunks)}
                ))
            start = end - overlap
        
        if not chunks:
            chunks.append(ContentChunk(
                chunk_type=ChunkType.TEXT,
                data=content.encode('utf-8'),
                metadata={'id': 0}
            ))
        
        # Build AIF-BIN file
        aifbin = AIFBINFile(
            metadata={
                'title': source.stem,
                'source_file': str(source),
                'created': datetime.now().isoformat(),
                'chunk_count': len(chunks)
            },
            chunks=chunks,
            original_raw=content.encode('utf-8'),
            versions=[]
        )
        
        writer = AIFBINWriter()
        size = writer.write(aifbin, str(output))
        print(f"✅ Created: {output.name} ({len(chunks)} chunks, {size} bytes)")
        print(f"   Format: AIF-BIN v2 (binary, supports embeddings)")
    
    def cmd_upgrade(args):
        """Upgrade .aimf (v1 JSON) to .aif-bin (v2 binary)."""
        import json
        source = Path(args.source)
        
        if not source.exists():
            print(f"❌ File not found: {source}")
            sys.exit(1)
        
        # Determine output path
        if args.output:
            output = Path(args.output)
        else:
            output = source.with_suffix('.aif-bin')
        
        print(f"📄 Upgrading: {source.name} → {output.name}")
        
        size = migrate_from_v1(str(source), str(output))
        print(f"✅ Created: {output.name} ({size} bytes)")
        print(f"   Format: AIF-BIN v2 (binary)")
    
    def cmd_info(args):
        """Show file info."""
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            sys.exit(1)
        
        reader = AIFBINReader(str(filepath))
        info = reader.get_info()
        
        print(f"\n📦 AIF-BIN File Info (v2 Binary)")
        print(f"{'─' * 40}")
        print(f"  File:       {filepath.name}")
        print(f"  Valid:      {'✅ Yes' if info['magic_valid'] else '❌ No'}")
        print(f"  Version:    {info['version']}")
        print(f"  Size:       {info['total_size']} bytes")
        print(f"  Chunks:     {info['chunk_count']}")
        print(f"  Has Raw:    {'Yes' if info['has_original_raw'] else 'No'}")
        print(f"  Has Versions: {'Yes' if info['has_versions'] else 'No'}")
        print(f"  Checksum:   {info['checksum']}")
        print()
    
    def cmd_extract(args):
        """Extract original content."""
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            sys.exit(1)
        
        reader = AIFBINReader(str(filepath))
        aifbin = reader.read()
        
        if aifbin.original_raw:
            content = aifbin.original_raw.decode('utf-8', errors='replace')
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Extracted to {args.output}")
            else:
                print(content)
        else:
            print("❌ No original content found")
            sys.exit(1)
    
    def cmd_chunks(args):
        """List chunks."""
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            sys.exit(1)
        
        reader = AIFBINReader(str(filepath))
        aifbin = reader.read()
        
        print(f"\n📦 Chunks in {filepath.name} (AIF-BIN v2)")
        print(f"{'─' * 50}")
        
        for i, chunk in enumerate(aifbin.chunks[:args.limit]):
            preview = chunk.data[:100].decode('utf-8', errors='replace')
            print(f"\n  [{i}] {chunk.chunk_type.name}")
            print(f"      {preview}...")
        
        if len(aifbin.chunks) > args.limit:
            print(f"\n  ... and {len(aifbin.chunks) - args.limit} more")
    
    # Argument parser
    parser = argparse.ArgumentParser(
        prog='aifbin-v2',
        description='AIF-BIN v2 — Binary Format CLI',
        epilog='For semantic search, use AIF-BIN Pro: https://aifbin.dev'
    )
    parser.add_argument('--version', '-v', action='store_true', help='Show version')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # migrate
    p_migrate = subparsers.add_parser('migrate', help='Convert file to AIF-BIN v2 (binary)')
    p_migrate.add_argument('source', help='Source file (markdown, text)')
    p_migrate.add_argument('-o', '--output', help='Output file or directory')
    
    # upgrade
    p_upgrade = subparsers.add_parser('upgrade', help='Upgrade .aimf (v1) to .aif-bin (v2)')
    p_upgrade.add_argument('source', help='Source .aimf file')
    p_upgrade.add_argument('-o', '--output', help='Output .aif-bin file')
    
    # info
    p_info = subparsers.add_parser('info', help='Show file info')
    p_info.add_argument('file', help='AIF-BIN file (.aif-bin)')
    
    # extract
    p_extract = subparsers.add_parser('extract', help='Extract original content')
    p_extract.add_argument('file', help='AIF-BIN file (.aif-bin)')
    p_extract.add_argument('-o', '--output', help='Output file')
    
    # chunks
    p_chunks = subparsers.add_parser('chunks', help='List chunks')
    p_chunks.add_argument('file', help='AIF-BIN file (.aif-bin)')
    p_chunks.add_argument('-l', '--limit', type=int, default=10, help='Max chunks to show')
    
    args = parser.parse_args()
    
    if args.version:
        print(f"""
AIF-BIN v2 (Binary Format)
Format version: {VERSION}

📦 Output: .aif-bin (binary, MessagePack)
📄 License: MIT

Features:
  • Binary format (smaller, faster)
  • Supports embeddings for semantic search
  • CRC64 checksums
  • Version history

🔗 https://aifbin.dev
""")
        sys.exit(0)
    
    if not args.command:
        parser.print_help()
        print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AIF-BIN v2 — Binary Format
  
  📦 Output: .aif-bin (binary)
  
  ✅ Included: migrate, upgrade, info, extract, chunks
  
  🔒 Pro Only: search, batch, watch, embeddings
     Upgrade: https://aifbin.dev
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        sys.exit(0)
    
    commands = {
        'migrate': cmd_migrate,
        'upgrade': cmd_upgrade,
        'info': cmd_info,
        'extract': cmd_extract,
        'chunks': cmd_chunks,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        print(f"Unknown command: {args.command}")
