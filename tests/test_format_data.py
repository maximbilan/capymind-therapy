import unittest
from datetime import datetime
from unittest.mock import Mock
from capymind_agent.tools.format_data import format_data


class TestFormatData(unittest.TestCase):
    """Test cases for the format_data function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_context = Mock()
        self.mock_context._invocation_context = Mock()
        self.mock_context._invocation_context.user_id = "test_user_123"
    
    def test_format_notes_empty_list(self):
        """Test formatting empty notes list."""
        result = format_data("notes", [], self.mock_context)
        self.assertEqual(result, "No notes found.")
    
    def test_format_notes_single_note(self):
        """Test formatting a single note."""
        notes = [{
            "id": "note_1",
            "text": "This is a test note",
            "timestamp": "2024-01-15T10:30:00Z"
        }]
        result = format_data("notes", notes, self.mock_context)
        
        self.assertIn("📝 **Note from January 15, 2024 at 10:30 AM**", result)
        self.assertIn("This is a test note", result)
    
    def test_format_notes_multiple_notes(self):
        """Test formatting multiple notes."""
        notes = [
            {
                "id": "note_1",
                "text": "First note",
                "timestamp": "2024-01-15T10:30:00Z"
            },
            {
                "id": "note_2", 
                "text": "Second note",
                "timestamp": "2024-01-16T14:45:00Z"
            }
        ]
        result = format_data("notes", notes, self.mock_context)
        
        self.assertIn("📝 **Note from January 15, 2024 at 10:30 AM**", result)
        self.assertIn("First note", result)
        self.assertIn("📝 **Note from January 16, 2024 at 02:45 PM**", result)
        self.assertIn("Second note", result)
    
    def test_format_notes_invalid_timestamp(self):
        """Test formatting notes with invalid timestamp."""
        notes = [{
            "id": "note_1",
            "text": "Note with bad timestamp",
            "timestamp": "invalid-timestamp"
        }]
        result = format_data("notes", notes, self.mock_context)
        
        self.assertIn("📝 **Note from invalid-timestamp**", result)
        self.assertIn("Note with bad timestamp", result)
    
    def test_format_notes_missing_timestamp(self):
        """Test formatting notes with missing timestamp."""
        notes = [{
            "id": "note_1",
            "text": "Note without timestamp"
        }]
        result = format_data("notes", notes, self.mock_context)
        
        self.assertIn("📝 **Note from Unknown date**", result)
        self.assertIn("Note without timestamp", result)
    
    def test_format_settings_empty_list(self):
        """Test formatting empty settings list."""
        result = format_data("settings", [], self.mock_context)
        self.assertEqual(result, "No settings found.")
    
    def test_format_settings_single_document(self):
        """Test formatting settings document."""
        settings = [{
            "id": "settings_1",
            "settings": {
                "Location": "New York",
                "HasMorningReminder": True,
                "HasEveningReminder": False,
                "MorningReminderOffset": 7,
                "EveningReminderOffset": 20
            }
        }]
        result = format_data("settings", settings, self.mock_context)
        
        self.assertIn("⚙️ **Your Settings:**", result)
        self.assertIn("• **Location**: New York", result)
        self.assertIn("• **Morning Reminder Enabled**: Yes", result)
        self.assertIn("• **Evening Reminder Enabled**: No", result)
        self.assertIn("• **Morning Reminder Time (hours from midnight)**: 7", result)
        self.assertIn("• **Evening Reminder Time (hours from midnight)**: 20", result)
    
    def test_format_settings_flat_structure(self):
        """Test formatting settings with flat structure (no nested 'settings' key)."""
        settings = [{
            "id": "settings_1",
            "Location": "San Francisco",
            "HasMorningReminder": False
        }]
        result = format_data("settings", settings, self.mock_context)
        
        self.assertIn("⚙️ **Your Settings:**", result)
        self.assertIn("• **Location**: San Francisco", result)
        self.assertIn("• **Morning Reminder Enabled**: No", result)
    
    def test_format_user_empty_list(self):
        """Test formatting empty user list."""
        result = format_data("user", [], self.mock_context)
        self.assertEqual(result, "No user found.")
    
    def test_format_user_single_document(self):
        """Test formatting user document."""
        user = [{
            "id": "user_1",
            "user_data": {
                "FirstName": "John",
                "LastName": "Doe",
                "IsOnboarded": True,
                "IsDeleted": False,
                "Role": "user",
                "Locale": "en-US"
            }
        }]
        result = format_data("user", user, self.mock_context)
        
        self.assertIn("👤 **Your Profile:**", result)
        self.assertIn("• **First Name**: John", result)
        self.assertIn("• **Last Name**: Doe", result)
        self.assertIn("• **Onboarding Complete**: Yes", result)
        self.assertIn("• **Account Status**: Active", result)
        self.assertIn("• **User Role**: user", result)
        self.assertIn("• **Language/Locale**: en-US", result)
    
    def test_format_user_flat_structure(self):
        """Test formatting user with flat structure (no nested 'user_data' key)."""
        user = [{
            "id": "user_1",
            "FirstName": "Jane",
            "LastName": "Smith",
            "IsOnboarded": False
        }]
        result = format_data("user", user, self.mock_context)
        
        self.assertIn("👤 **Your Profile:**", result)
        self.assertIn("• **First Name**: Jane", result)
        self.assertIn("• **Last Name**: Smith", result)
        self.assertIn("• **Onboarding Complete**: No", result)
    
    def test_format_user_with_timestamps(self):
        """Test formatting user with timestamp fields."""
        user = [{
            "id": "user_1",
            "FirstName": "Test",
            "Timestamp": "2024-01-15T10:30:00Z",
            "TherapySessionEndAt": "2024-01-15T11:00:00Z"
        }]
        result = format_data("user", user, self.mock_context)
        
        self.assertIn("• **Last Updated**: January 15, 2024 at 10:30 AM", result)
        self.assertIn("• **Therapy Session Ends At**: January 15, 2024 at 11:00 AM", result)
    
    def test_format_user_invalid_timestamp(self):
        """Test formatting user with invalid timestamp."""
        user = [{
            "id": "user_1",
            "FirstName": "Test",
            "Timestamp": "invalid-timestamp"
        }]
        result = format_data("user", user, self.mock_context)
        
        self.assertIn("• **Last Updated**: invalid-timestamp", result)
    
    def test_format_data_single_dict_instead_of_list(self):
        """Test that single dict is converted to list internally."""
        user = {
            "id": "user_1",
            "FirstName": "Single",
            "LastName": "User"
        }
        result = format_data("user", user, self.mock_context)
        
        self.assertIn("👤 **Your Profile:**", result)
        self.assertIn("• **First Name**: Single", result)
        self.assertIn("• **Last Name**: User", result)
    
    def test_format_unknown_data_type(self):
        """Test formatting unknown data type."""
        result = format_data("unknown_type", [{"some": "data"}], self.mock_context)
        self.assertEqual(result, "Unknown data type: unknown_type")


if __name__ == '__main__':
    unittest.main()