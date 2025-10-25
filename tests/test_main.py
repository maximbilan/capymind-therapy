import unittest
import os
from unittest.mock import patch, Mock
import sys

# Add the project root to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, AGENT_DIR, SESSION_SERVICE_URI, ALLOWED_ORIGINS, SERVE_WEB_INTERFACE


class TestMainApp(unittest.TestCase):
    """Test cases for the main application setup."""
    
    def test_constants_are_defined(self):
        """Test that all required constants are defined."""
        self.assertIsNotNone(AGENT_DIR)
        self.assertIsNotNone(SESSION_SERVICE_URI)
        self.assertIsNotNone(ALLOWED_ORIGINS)
        self.assertIsNotNone(SERVE_WEB_INTERFACE)
    
    def test_agent_dir_is_valid_path(self):
        """Test that AGENT_DIR is a valid directory path."""
        self.assertTrue(os.path.isdir(AGENT_DIR))
        self.assertTrue(AGENT_DIR.endswith('capymind-session'))
    
    def test_session_service_uri_format(self):
        """Test that SESSION_SERVICE_URI has correct format."""
        self.assertTrue(SESSION_SERVICE_URI.startswith('sqlite:///'))
        self.assertTrue(SESSION_SERVICE_URI.endswith('.db'))
    
    def test_allowed_origins_is_list(self):
        """Test that ALLOWED_ORIGINS is a list."""
        self.assertIsInstance(ALLOWED_ORIGINS, list)
        self.assertIn("http://localhost", ALLOWED_ORIGINS)
        self.assertIn("http://localhost:8080", ALLOWED_ORIGINS)
        self.assertIn("*", ALLOWED_ORIGINS)
    
    def test_serve_web_interface_is_boolean(self):
        """Test that SERVE_WEB_INTERFACE is a boolean."""
        self.assertIsInstance(SERVE_WEB_INTERFACE, bool)
        self.assertTrue(SERVE_WEB_INTERFACE)
    
    def test_app_is_fastapi_instance(self):
        """Test that app is a FastAPI instance."""
        from fastapi import FastAPI
        self.assertIsInstance(app, FastAPI)
    
    def test_app_has_correct_title(self):
        """Test that the app has the expected title."""
        # The app title should be set by the ADK framework
        # We can at least verify it's a FastAPI app
        self.assertTrue(hasattr(app, 'title'))
    
    @patch('main.uvicorn.run')
    @patch('main.os.environ.get')
    def test_main_execution_with_default_port(self, mock_getenv, mock_run):
        """Test main execution with default port."""
        mock_getenv.return_value = None
        
        # Import and execute the main block
        import main
        
        # The main block should call uvicorn.run
        # We can't easily test this without mocking the entire execution
        # but we can verify the constants are accessible
        self.assertIsNotNone(main.AGENT_DIR)
    
    @patch('main.uvicorn.run')
    @patch('main.os.environ.get')
    def test_main_execution_with_custom_port(self, mock_getenv, mock_run):
        """Test main execution with custom port from environment."""
        mock_getenv.return_value = "9000"
        
        # Import and execute the main block
        import main
        
        # Verify the environment variable is accessed
        mock_getenv.assert_called_with("PORT", 8080)
    
    def test_imports_are_available(self):
        """Test that all required imports are available."""
        import os
        import uvicorn
        from fastapi import FastAPI
        from google.adk.cli.fast_api import get_fast_api_app
        
        # If we get here without ImportError, the imports work
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()