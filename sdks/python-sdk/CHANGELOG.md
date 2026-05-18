# Changelog

All notable changes to the Aletheia AI Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Aletheia AI Python SDK
- Synchronous and asynchronous client support
- Agent lifecycle management (register, update, list, delete)
- Audit event logging with cryptographic signatures
- Evidence package download (.aep format)
- Policy management API
- Delegation chain support
- Compliance reporting (PDF, JSON, CSV)
- ROI calculation
- Verification API (signatures, timestamps, chain of custody)
- Type hints throughout
- Comprehensive examples:
  - Basic usage
  - Async client
  - Delegation chains
  - Compliance reporting
- Full test suite with pytest
- Pydantic models for type safety
- httpx for HTTP client (sync + async)
- Environment variable configuration

### Documentation
- Complete README with examples
- API reference in docstrings
- Contributing guidelines
- Examples with detailed comments

## [0.1.0] - 2026-02-12

### Added
- Initial development release
- Core SDK functionality
- Basic documentation

[Unreleased]: https://github.com/aletheia-ai/python-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/aletheia-ai/python-sdk/releases/tag/v0.1.0
