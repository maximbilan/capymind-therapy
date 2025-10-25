# CapyMind Session Tests

This directory contains unit tests for the CapyMind Session application.

## Test Structure

- `test_format_data.py` - Tests for the data formatting utility functions
- `test_firestore_utils.py` - Tests for Firestore utility functions
- `test_main.py` - Tests for the main application setup
- `test_prompts.py` - Tests for prompt constants and content
- `test_config.py` - Tests for agent configuration
- `run_tests.py` - Test runner script

## Running Tests

### Run all tests:
```bash
cd /path/to/capymind-session
python tests/run_tests.py
```

### Run specific test file:
```bash
cd /path/to/capymind-session
python -m unittest tests.test_format_data
python -m unittest tests.test_firestore_utils
python -m unittest tests.test_main
python -m unittest tests.test_prompts
python -m unittest tests.test_config
```

### Run with verbose output:
```bash
cd /path/to/capymind-session
python -m unittest tests -v
```

## Test Coverage

The tests cover:

1. **Data Formatting** (`test_format_data.py`):
   - Formatting of notes, settings, and user data
   - Handling of timestamps and edge cases
   - Error handling for invalid data

2. **Firestore Utilities** (`test_firestore_utils.py`):
   - JSON serialization of Firestore data types
   - Firestore client creation with different credential scenarios
   - Error handling for missing credentials

3. **Main Application** (`test_main.py`):
   - Application constants and configuration
   - FastAPI app initialization
   - Environment variable handling

4. **Prompts** (`test_prompts.py`):
   - Prompt content validation
   - Presence of key therapeutic elements
   - Crisis line numbers and safety information

5. **Agent Configuration** (`test_config.py`):
   - Agent setup and attributes
   - Model and tool configuration
   - Agent relationships

## Dependencies

The tests use Python's built-in `unittest` framework and `unittest.mock` for mocking external dependencies. No additional test dependencies are required beyond the main application requirements.

## Notes

- Tests are designed to run without external dependencies (Firestore, etc.)
- Mocking is used extensively to isolate units under test
- Tests focus on the most testable parts of the codebase
- Some integration aspects are skipped due to complexity with Google ADK framework