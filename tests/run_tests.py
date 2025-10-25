#!/usr/bin/env python3
"""
Test runner for CapyMind Session tests.
Run this script to execute all unit tests.
"""

import unittest
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_tests():
    """Run all unit tests."""
    # For now, only run simple tests that don't require external dependencies
    # The other tests require Google ADK which may not be installed
    
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Only run test_simple.py for now
    suite = loader.loadTestsFromName('test_simple')
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)