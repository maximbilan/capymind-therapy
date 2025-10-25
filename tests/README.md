# CapyMind Session Tests

This directory contains unit tests for the CapyMind Session application.

## Test Structure

- `test_simple.py` - Structural validation tests (no external dependencies)
- `run_tests.py` - Test runner script

**Note**: Complex tests requiring Google ADK dependencies have been removed to simplify CI/CD and focus on essential structural validation.

## Running Tests

### Run all tests:
```bash
cd /path/to/capymind-session
python tests/run_tests.py
```

### Run specific test file:
```bash
cd /path/to/capymind-session
python -m unittest tests.test_simple
```

### Run with verbose output:
```bash
cd /path/to/capymind-session
python -m unittest tests -v
```

## Test Coverage

The tests cover:

1. **Structural Validation** (`test_simple.py`):
   - Project file structure and organization
   - Required files and directories exist
   - Basic content validation for key files
   - Scripts and configuration files
   - Agent and tool file structure

## Dependencies

The tests use Python's built-in `unittest` framework. No external dependencies are required - tests focus on structural validation only.

## Notes

- Tests are designed to run without any external dependencies
- Focus on essential structural validation rather than complex functionality testing
- Simplified for reliable CI/CD execution
- Complex tests requiring Google ADK have been removed for maintainability