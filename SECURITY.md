# Security Policy

**Last Updated:** February 2, 2026

## Supported Versions

| Version | Supported |
|---------|-----------|
| v1.x (AIMF) | ✅ Yes |
| v2.x (AIF-BIN) | ✅ Yes |

## Security Model

AIF-BIN Lite is designed with a minimal attack surface:

- **No network communication** — The tool never connects to the internet
- **No external dependencies** (v1) — Pure Python standard library
- **One dependency** (v2) — Only `msgpack` for binary serialization
- **Local processing only** — Files are read and written locally
- **No code execution** — The tool does not execute content from files

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

### How to Report

**Email:** security@terronex.dev

**Include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Any suggested fixes (optional)

### What to Expect

| Stage | Timeline |
|-------|----------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 1 week |
| Fix timeline communicated | Within 2 weeks |
| Public disclosure (coordinated) | After fix is released |

### What We Ask

- **Do not** publicly disclose the vulnerability before we've had a chance to address it
- **Do not** exploit the vulnerability beyond what's necessary to demonstrate it
- **Do** provide sufficient detail for us to reproduce and fix the issue

## Security Best Practices

When using AIF-BIN Lite:

1. **Verify downloads** — Only download from official sources (GitHub, terronex.dev)
2. **Check file integrity** — v2 files include CRC64 checksums for verification
3. **Review before processing** — Don't process untrusted files without inspection

## Contact

- **Security issues:** security@terronex.dev
- **General support:** support@terronex.dev

---

© 2026 Terronex.dev. All rights reserved.
