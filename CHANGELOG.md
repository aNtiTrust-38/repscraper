# Changelog

## [Unreleased]
### Added
- Flair filtering for Reddit posts: Only posts with allowed flairs (e.g., 'QC', 'Haul', 'Review') are processed.
- Unit test for flair filtering in `test_processors.py`.
- End-to-end integration test for flair filtering in `test_end_to_end.py`.

### Changed
- All flair filtering logic is implemented in `filter_by_flair` (TDD approach).
- Allowed flairs are configurable in the test and can be made configurable in production.

- Reddit API integration milestone: RedditScraper.fetch_batch implemented, TDD integration tests passing, error handling and config support per instructions.md.
