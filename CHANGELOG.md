# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added link to the documentation in the cli

### Fixed

- Comparisons against two instances will no longer fail when they are the same

## [1.1.0] - 2022-09-04

### Added

- CLI flag for converting only (`--convert`)

### Changed

- Errors were made easier to read (traceback & technical details were removed, assorted formatting improvements)

### Fixed

- Comparisons against non-instance types will now return false rather than crashing

## [1.0.0] - 2022-08-28

Initial release
