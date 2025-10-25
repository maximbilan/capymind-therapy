import unittest
from unittest.mock import Mock, patch, MagicMock
from capymind_agent.tools.firestore_data import _to_jsonable, _get_firestore_client


class TestFirestoreUtils(unittest.TestCase):
    """Test cases for Firestore utility functions."""
    
    def test_to_jsonable_simple_types(self):
        """Test conversion of simple types to JSON-serializable format."""
        # Test basic types
        self.assertEqual(_to_jsonable("string"), "string")
        self.assertEqual(_to_jsonable(123), 123)
        self.assertEqual(_to_jsonable(True), True)
        self.assertEqual(_to_jsonable(None), None)
        self.assertEqual(_to_jsonable(3.14), 3.14)
    
    def test_to_jsonable_dict(self):
        """Test conversion of dictionary to JSON-serializable format."""
        data = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "nested": {
                "inner": "value"
            }
        }
        result = _to_jsonable(data)
        self.assertEqual(result, data)
    
    def test_to_jsonable_list(self):
        """Test conversion of list to JSON-serializable format."""
        data = ["item1", "item2", {"nested": "value"}]
        result = _to_jsonable(data)
        self.assertEqual(result, data)
    
    def test_to_jsonable_with_isoformat(self):
        """Test conversion of objects with isoformat method."""
        class MockTimestamp:
            def isoformat(self):
                return "2024-01-15T10:30:00Z"
        
        timestamp = MockTimestamp()
        result = _to_jsonable(timestamp)
        self.assertEqual(result, "2024-01-15T10:30:00Z")
    
    def test_to_jsonable_with_isoformat_exception(self):
        """Test conversion of objects with isoformat method that raises exception."""
        class MockTimestamp:
            def isoformat(self):
                raise ValueError("Invalid timestamp")
        
        timestamp = MockTimestamp()
        result = _to_jsonable(timestamp)
        self.assertEqual(result, timestamp)  # Should return original object
    
    def test_to_jsonable_document_reference(self):
        """Test conversion of Firestore DocumentReference."""
        # Mock DocumentReference
        class MockDocumentReference:
            def __init__(self, path):
                self.path = path
        
        doc_ref = MockDocumentReference("users/user123")
        result = _to_jsonable(doc_ref)
        self.assertEqual(result, "users/user123")
    
    def test_to_jsonable_nested_structures(self):
        """Test conversion of nested structures with mixed types."""
        class MockTimestamp:
            def isoformat(self):
                return "2024-01-15T10:30:00Z"
        
        class MockDocRef:
            def __init__(self, path):
                self.path = path
        
        data = {
            "user": MockDocRef("users/user123"),
            "timestamp": MockTimestamp(),
            "simple": "value",
            "nested": {
                "inner_timestamp": MockTimestamp(),
                "inner_ref": MockDocRef("notes/note456")
            },
            "list_with_refs": [MockDocRef("settings/set123"), "string_item"]
        }
        
        result = _to_jsonable(data)
        expected = {
            "user": "users/user123",
            "timestamp": "2024-01-15T10:30:00Z",
            "simple": "value",
            "nested": {
                "inner_timestamp": "2024-01-15T10:30:00Z",
                "inner_ref": "notes/note456"
            },
            "list_with_refs": ["settings/set123", "string_item"]
        }
        
        self.assertEqual(result, expected)
    
    @patch('capymind_agent.tools.firestore_data.os.getenv')
    @patch('capymind_agent.tools.firestore_data.default')
    @patch('capymind_agent.tools.firestore_data.FirestoreClient')
    def test_get_firestore_client_with_credentials(self, mock_client, mock_default, mock_getenv):
        """Test getting Firestore client with default credentials."""
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'GOOGLE_CLOUD_PROJECT': 'test-project',
            'GOOGLE_CLOUD_DATABASE': 'test-db'
        }.get(key, default)
        
        # Mock credentials
        mock_credentials = Mock()
        mock_default.return_value = (mock_credentials, 'test-project')
        
        # Mock client
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        result = _get_firestore_client()
        
        # Verify client was created with correct parameters
        mock_client.assert_called_once_with(
            project='test-project',
            credentials=mock_credentials,
            database='test-db'
        )
        self.assertEqual(result, mock_client_instance)
    
    @patch('capymind_agent.tools.firestore_data.os.getenv')
    @patch('capymind_agent.tools.firestore_data.default')
    @patch('capymind_agent.tools.firestore_data.AnonymousCredentials')
    @patch('capymind_agent.tools.firestore_data.FirestoreClient')
    def test_get_firestore_client_no_credentials(self, mock_client, mock_anon_creds, mock_default, mock_getenv):
        """Test getting Firestore client with no credentials (fallback to anonymous)."""
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'GOOGLE_CLOUD_PROJECT': 'test-project'
        }.get(key, default)
        
        # Mock credentials error
        from google.auth.exceptions import DefaultCredentialsError
        mock_default.side_effect = DefaultCredentialsError("No credentials")
        
        # Mock anonymous credentials
        mock_anon_creds_instance = Mock()
        mock_anon_creds.return_value = mock_anon_creds_instance
        
        # Mock client
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        result = _get_firestore_client()
        
        # Verify client was created with anonymous credentials
        mock_client.assert_called_once_with(
            project='test-project',
            credentials=mock_anon_creds_instance
        )
        self.assertEqual(result, mock_client_instance)
    
    @patch('capymind_agent.tools.firestore_data.os.getenv')
    @patch('capymind_agent.tools.firestore_data.default')
    @patch('capymind_agent.tools.firestore_data.AnonymousCredentials')
    @patch('capymind_agent.tools.firestore_data.FirestoreClient')
    def test_get_firestore_client_with_override_project(self, mock_client, mock_anon_creds, mock_default, mock_getenv):
        """Test getting Firestore client with override project ID."""
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'GOOGLE_CLOUD_PROJECT': 'env-project'
        }.get(key, default)
        
        # Mock credentials error
        from google.auth.exceptions import DefaultCredentialsError
        mock_default.side_effect = DefaultCredentialsError("No credentials")
        
        # Mock anonymous credentials
        mock_anon_creds_instance = Mock()
        mock_anon_creds.return_value = mock_anon_creds_instance
        
        # Mock client
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        result = _get_firestore_client(override_project_id="override-project")
        
        # Verify client was created with override project
        mock_client.assert_called_once_with(
            project='override-project',
            credentials=mock_anon_creds_instance
        )
        self.assertEqual(result, mock_client_instance)
    
    @patch('capymind_agent.tools.firestore_data.os.getenv')
    @patch('capymind_agent.tools.firestore_data.default')
    @patch('capymind_agent.tools.firestore_data.AnonymousCredentials')
    @patch('capymind_agent.tools.firestore_data.FirestoreClient')
    def test_get_firestore_client_database_not_supported(self, mock_client, mock_anon_creds, mock_default, mock_getenv):
        """Test getting Firestore client when database parameter is not supported."""
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'GOOGLE_CLOUD_PROJECT': 'test-project'
        }.get(key, default)
        
        # Mock credentials error
        from google.auth.exceptions import DefaultCredentialsError
        mock_default.side_effect = DefaultCredentialsError("No credentials")
        
        # Mock anonymous credentials
        mock_anon_creds_instance = Mock()
        mock_anon_creds.return_value = mock_anon_creds_instance
        
        # Mock client to raise TypeError for database parameter
        mock_client.side_effect = TypeError("Database parameter not supported")
        
        # This should not raise an exception, should fall back to client without database
        with patch.object(mock_client, 'side_effect', None):
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            
            result = _get_firestore_client(override_database="test-db")
            
            # Verify client was created without database parameter
            mock_client.assert_called_with(
                project='test-project',
                credentials=mock_anon_creds_instance
            )


if __name__ == '__main__':
    unittest.main()