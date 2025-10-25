import unittest
import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capymind_agent.prompt import CAPYMIND_AGENT_PROMPT, prompt
from capymind_agent.sug_agents.data_fetcher.prompt import DATA_FETCHER_PROMPT
from capymind_agent.sug_agents.crysis_line.prompt import CRISIS_LINE_PROMPT


class TestPrompts(unittest.TestCase):
    """Test cases for prompt constants."""
    
    def test_capymind_agent_prompt_is_defined(self):
        """Test that CAPYMIND_AGENT_PROMPT is defined and not empty."""
        self.assertIsNotNone(CAPYMIND_AGENT_PROMPT)
        self.assertIsInstance(CAPYMIND_AGENT_PROMPT, str)
        self.assertGreater(len(CAPYMIND_AGENT_PROMPT), 100)  # Should be substantial
    
    def test_capymind_agent_prompt_alias(self):
        """Test that prompt is an alias for CAPYMIND_AGENT_PROMPT."""
        self.assertEqual(prompt, CAPYMIND_AGENT_PROMPT)
    
    def test_capymind_agent_prompt_contains_key_elements(self):
        """Test that the main prompt contains key therapeutic elements."""
        prompt_text = CAPYMIND_AGENT_PROMPT.lower()
        
        # Check for key therapeutic approaches
        self.assertIn("cbt", prompt_text)
        self.assertIn("dbt", prompt_text)
        self.assertIn("act", prompt_text)
        self.assertIn("mindfulness", prompt_text)
        
        # Check for safety elements
        self.assertIn("crisis", prompt_text)
        self.assertIn("safety", prompt_text)
        self.assertIn("emergency", prompt_text)
        
        # Check for core instructions
        self.assertIn("brief", prompt_text)
        self.assertIn("therapist", prompt_text)
        self.assertIn("compassionate", prompt_text)
    
    def test_capymind_agent_prompt_contains_crisis_numbers(self):
        """Test that the main prompt contains crisis line numbers."""
        prompt_text = CAPYMIND_AGENT_PROMPT
        
        # Check for key crisis numbers
        self.assertIn("988", prompt_text)  # US Suicide & Crisis Lifeline
        self.assertIn("911", prompt_text)  # Emergency
        self.assertIn("741741", prompt_text)  # Crisis Text Line
    
    def test_data_fetcher_prompt_is_defined(self):
        """Test that DATA_FETCHER_PROMPT is defined and not empty."""
        self.assertIsNotNone(DATA_FETCHER_PROMPT)
        self.assertIsInstance(DATA_FETCHER_PROMPT, str)
        self.assertGreater(len(DATA_FETCHER_PROMPT), 10)
    
    def test_data_fetcher_prompt_contains_key_elements(self):
        """Test that the data fetcher prompt contains key elements."""
        prompt_text = DATA_FETCHER_PROMPT.lower()
        
        self.assertIn("data fetcher", prompt_text)
        self.assertIn("firestore", prompt_text)
        self.assertIn("format", prompt_text)
        self.assertIn("brief", prompt_text)
    
    def test_crisis_line_prompt_is_defined(self):
        """Test that CRISIS_LINE_PROMPT is defined and not empty."""
        self.assertIsNotNone(CRISIS_LINE_PROMPT)
        self.assertIsInstance(CRISIS_LINE_PROMPT, str)
        self.assertGreater(len(CRISIS_LINE_PROMPT), 10)
    
    def test_crisis_line_prompt_contains_key_elements(self):
        """Test that the crisis line prompt contains key elements."""
        prompt_text = CRISIS_LINE_PROMPT.lower()
        
        self.assertIn("crisis line", prompt_text)
        self.assertIn("phone", prompt_text)
        self.assertIn("location", prompt_text)
        self.assertIn("brief", prompt_text)
    
    def test_crisis_line_prompt_contains_crisis_numbers(self):
        """Test that the crisis line prompt contains crisis numbers."""
        prompt_text = CRISIS_LINE_PROMPT
        
        self.assertIn("988", prompt_text)  # US Suicide & Crisis Lifeline
        self.assertIn("911", prompt_text)  # Emergency
        self.assertIn("741741", prompt_text)  # Crisis Text Line
    
    def test_prompts_are_strings(self):
        """Test that all prompts are strings."""
        self.assertIsInstance(CAPYMIND_AGENT_PROMPT, str)
        self.assertIsInstance(prompt, str)
        self.assertIsInstance(DATA_FETCHER_PROMPT, str)
        self.assertIsInstance(CRISIS_LINE_PROMPT, str)
    
    def test_prompts_have_reasonable_length(self):
        """Test that prompts have reasonable lengths (not too short or too long)."""
        # Main prompt should be substantial
        self.assertGreater(len(CAPYMIND_AGENT_PROMPT), 1000)
        self.assertLess(len(CAPYMIND_AGENT_PROMPT), 10000)
        
        # Sub-agent prompts should be shorter but not empty
        self.assertGreater(len(DATA_FETCHER_PROMPT), 20)
        self.assertLess(len(DATA_FETCHER_PROMPT), 1000)
        
        self.assertGreater(len(CRISIS_LINE_PROMPT), 20)
        self.assertLess(len(CRISIS_LINE_PROMPT), 1000)
    
    def test_prompts_do_not_contain_placeholders(self):
        """Test that prompts don't contain obvious placeholder text."""
        all_prompts = [CAPYMIND_AGENT_PROMPT, DATA_FETCHER_PROMPT, CRISIS_LINE_PROMPT]
        
        for prompt_text in all_prompts:
            # Check for common placeholder patterns
            self.assertNotIn("TODO", prompt_text.upper())
            self.assertNotIn("FIXME", prompt_text.upper())
            self.assertNotIn("PLACEHOLDER", prompt_text.upper())
            self.assertNotIn("XXX", prompt_text.upper())


if __name__ == '__main__':
    unittest.main()