from google.adk.agents import Agent
from google.adk.tools import FunctionTool, ToolContext
from typing import Any, Dict, List
import json
from datetime import datetime

DATA_FETCHER_PROMPT = (
    "You are a focused data fetcher for CapyMind. "
    "Your sole job is to retrieve user profile, notes, and settings from Firestore "
    "via provided tools and format them into human-readable responses. "
    "When returning data, use the format_data tool to convert JSON responses into "
    "readable format before presenting to the user. "
    "Do not offer therapy guidance; only fetch and format data."
)

from capymind_agent.tools.firestore_data import capy_firestore_data_tool


def format_data(
    data_type: str,
    data: List[Dict[str, Any]],
    tool_context: ToolContext,
) -> str:
    """
    Format JSON data into human-readable format.
    - data_type: 'notes', 'settings', or 'user'
    - data: List of dictionaries containing the data to format
    """
    if not data:
        return f"No {data_type} found."
    
    # Handle case where data might be a single dict instead of list
    if isinstance(data, dict):
        data = [data]
    
    if data_type == "notes":
        formatted_notes = []
        for note in data:
            # Parse timestamp for better formatting
            timestamp_str = note.get("timestamp", "")
            try:
                if timestamp_str:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
                else:
                    formatted_time = "Unknown date"
            except:
                formatted_time = timestamp_str
            
            formatted_notes.append(
                f"📝 **Note from {formatted_time}**\n"
                f"{note.get('text', 'No content')}\n"
            )
        return "\n".join(formatted_notes)
    
    elif data_type == "settings":
        if not data:
            return "No settings found."
        
        settings_doc = data[0]  # Settings should be a single document
        
        # Handle nested settings structure
        if "settings" in settings_doc:
            settings = settings_doc["settings"]
        else:
            settings = settings_doc
            
        formatted_settings = ["⚙️ **Your Settings:**\n"]
        
        # Format specific settings with better labels
        setting_labels = {
            "EveningReminderOffset": "Evening Reminder Time (hours from midnight)",
            "HasEveningReminder": "Evening Reminder Enabled",
            "HasMorningReminder": "Morning Reminder Enabled", 
            "Location": "Location",
            "MorningReminderOffset": "Morning Reminder Time (hours from midnight)",
            "SecondsFromUTC": "Timezone Offset (seconds from UTC)"
        }
        
        for key, value in settings.items():
            if key == "id":
                continue
                
            # Use custom label if available, otherwise format the key
            if key in setting_labels:
                label = setting_labels[key]
            else:
                label = key.replace("_", " ").title()
            
            # Format boolean values
            if isinstance(value, bool):
                value_str = "Yes" if value else "No"
            else:
                value_str = str(value)
                
            formatted_settings.append(f"• **{label}**: {value_str}")
        
        return "\n".join(formatted_settings)
    
    elif data_type == "user":
        if not data:
            return "No user profile found."
        
        user_doc = data[0]  # User should be a single document
        
        # Handle nested user_data structure
        if "user_data" in user_doc:
            user = user_doc["user_data"]
        else:
            user = user_doc
            
        formatted_user = ["👤 **Your Profile:**\n"]
        
        # Format specific user fields with better labels
        user_labels = {
            "ChatID": "Chat ID",
            "FirstName": "First Name",
            "ID": "User ID",
            "IsDeleted": "Account Status",
            "IsOnboarded": "Onboarding Complete",
            "IsTyping": "Currently Typing",
            "LastCommand": "Last Command Used",
            "LastName": "Last Name",
            "Locale": "Language/Locale",
            "Role": "User Role",
            "SecondsFromUTC": "Timezone Offset (seconds from UTC)",
            "TherapySessionEndAt": "Therapy Session Ends At",
            "TherapySessionId": "Current Therapy Session ID",
            "Timestamp": "Last Updated",
            "UserName": "Username"
        }
        
        for key, value in user.items():
            if key == "id":
                continue
                
            # Use custom label if available, otherwise format the key
            if key in user_labels:
                label = user_labels[key]
            else:
                label = key.replace("_", " ").title()
            
            # Format specific value types
            if isinstance(value, bool):
                if key == "IsDeleted":
                    value_str = "Deleted" if value else "Active"
                else:
                    value_str = "Yes" if value else "No"
            elif key in ["TherapySessionEndAt", "Timestamp"] and value:
                # Format timestamps
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    value_str = dt.strftime("%B %d, %Y at %I:%M %p")
                except:
                    value_str = str(value)
            else:
                value_str = str(value)
                
            formatted_user.append(f"• **{label}**: {value_str}")
        
        return "\n".join(formatted_user)
    
    else:
        return f"Unknown data type: {data_type}"


# Create the formatting tool
format_data_tool = FunctionTool(format_data)


data_fetcher_agent = Agent(
    model="gemini-2.5-flash",
    name="data_fetcher",
    description="Fetches Firestore data (user, notes, settings) for a given user_id and formats it into human-readable responses",
    instruction=DATA_FETCHER_PROMPT,
    tools=[capy_firestore_data_tool, format_data_tool],
)
