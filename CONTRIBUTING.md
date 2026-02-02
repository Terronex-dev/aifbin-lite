# Contributing to AIF-BIN Lite

Thank you for your interest in contributing to AIF-BIN Lite!

## Ways to Contribute

### 🐛 Reporting Bugs

1. Check [existing issues](https://github.com/terronexdev/aifbin-lite/issues) first
2. Create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS
   - Sample file (if applicable)

### 💡 Suggesting Features

1. Check if the feature already exists in [AIF-BIN Pro](https://github.com/terronexdev/aifbin-pro)
2. Open an issue with:
   - Clear description of the feature
   - Use case / why it's valuable
   - Proposed implementation (optional)

### 🔧 Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Test thoroughly (see below)
5. Commit with clear messages
6. Push and open a PR

## Code Guidelines

### Style

- Python 3.8+ compatible
- Type hints encouraged
- Clear docstrings for public functions
- Follow existing code patterns

### Dependencies

| Version | Dependencies |
|---------|--------------|
| v1 (`aifbin_v1.py`) | **None** — Keep it dependency-free! |
| v2 (`aifbin_v2.py`) | `msgpack` only |

**Do not add new dependencies to v1.** The zero-dependency design is intentional.

### Testing

Before submitting a PR:

```bash
# Test v1
python3 aifbin_v1.py migrate sample.md
python3 aifbin_v1.py info sample.aimf
python3 aifbin_v1.py extract sample.aimf

# Test v2
python3 aifbin_v2.py migrate sample.md
python3 aifbin_v2.py info sample.aif-bin
python3 aifbin_v2.py upgrade sample.aimf
```

## Project Structure

```
aifbin-lite/
├── aifbin_v1.py      # v1 JSON format (no dependencies)
├── aifbin_v2.py      # v2 binary format (requires msgpack)
├── sample.md         # Test file for quick testing
├── examples/         # Usage examples
├── docs/             # Documentation
└── legal/            # Legal documents
```

## Contributor License Agreement

By submitting a pull request, you agree that:

1. Your contributions are your original work
2. You have the right to submit them under the MIT License
3. Your contributions will be licensed under the MIT License
4. You grant Terronex.dev the right to use your contributions in both open-source and commercial products (including AIF-BIN Pro)

This is a lightweight CLA — no separate signing required. Submitting a PR implies agreement.

## What Happens Next

1. A maintainer will review your PR
2. We may request changes or ask questions
3. Once approved, we'll merge it
4. You'll be credited in the commit history

## Questions?

- **GitHub Issues** — For bugs and feature requests
- **support@terronex.dev** — For other questions

---

Thank you for helping make AIF-BIN better! 🎉
