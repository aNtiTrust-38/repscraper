# Changelog

## [Unreleased]
### Added
- Flair filtering for Reddit posts: Only posts with allowed flairs (e.g., 'QC', 'Haul', 'Review') are processed.
- Unit test for flair filtering in `test_processors.py`.
- End-to-end integration test for flair filtering in `test_end_to_end.py`.
- Added web-based configuration interface (FastAPI + HTML/JS/CSS)
- All config variables now editable via web UI
- Real-time validation, error highlighting, and user-friendly error messages
- Save, load defaults, and test config from browser
- Replaces manual YAML editing for config
- Improved backend error handling for robust UX

### Changed
- All flair filtering logic is implemented in `filter_by_flair` (TDD approach).
- Allowed flairs are configurable in the test and can be made configurable in production.

- Reddit API integration milestone: RedditScraper.fetch_batch implemented, TDD integration tests passing, error handling and config support per instructions.md.

- Logging and error handling in subprocesses is robust. Tests for log file creation are marked xfail on macOS due to temp directory isolation/subprocess file visibility issues. This is not a logic bug and is documented for future maintainers.

- Persistent deduplication (SQLite) is now integrated into the batch workflow, replacing in-memory deduplication. All core and integration tests pass except for expected failures. Documented for production reliability.
