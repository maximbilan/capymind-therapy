import unittest
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capymind_agent.agent import root_agent
from capymind_agent.sug_agents.data_fetcher.agent import data_fetcher_agent
from capymind_agent.sug_agents.crysis_line.agent import crisis_line_agent


class TestAgentConfiguration(unittest.TestCase):
    """Test cases for agent configuration and setup."""
    
    def test_root_agent_is_defined(self):
        """Test that root_agent is defined."""
        self.assertIsNotNone(root_agent)
    
    def test_root_agent_has_required_attributes(self):
        """Test that root_agent has required attributes."""
        self.assertTrue(hasattr(root_agent, 'model'))
        self.assertTrue(hasattr(root_agent, 'name'))
        self.assertTrue(hasattr(root_agent, 'description'))
        self.assertTrue(hasattr(root_agent, 'instruction'))
        self.assertTrue(hasattr(root_agent, 'sub_agents'))
    
    def test_root_agent_model(self):
        """Test that root_agent uses the correct model."""
        self.assertEqual(root_agent.model, 'gemini-2.5-flash')
    
    def test_root_agent_name(self):
        """Test that root_agent has the correct name."""
        self.assertEqual(root_agent.name, 'capymind_agent')
    
    def test_root_agent_has_sub_agents(self):
        """Test that root_agent has sub-agents configured."""
        self.assertIsNotNone(root_agent.sub_agents)
        self.assertIsInstance(root_agent.sub_agents, list)
        self.assertEqual(len(root_agent.sub_agents), 2)
    
    def test_data_fetcher_agent_is_defined(self):
        """Test that data_fetcher_agent is defined."""
        self.assertIsNotNone(data_fetcher_agent)
    
    def test_data_fetcher_agent_has_required_attributes(self):
        """Test that data_fetcher_agent has required attributes."""
        self.assertTrue(hasattr(data_fetcher_agent, 'model'))
        self.assertTrue(hasattr(data_fetcher_agent, 'name'))
        self.assertTrue(hasattr(data_fetcher_agent, 'description'))
        self.assertTrue(hasattr(data_fetcher_agent, 'instruction'))
        self.assertTrue(hasattr(data_fetcher_agent, 'tools'))
    
    def test_data_fetcher_agent_model(self):
        """Test that data_fetcher_agent uses the correct model."""
        self.assertEqual(data_fetcher_agent.model, 'gemini-2.5-flash')
    
    def test_data_fetcher_agent_name(self):
        """Test that data_fetcher_agent has the correct name."""
        self.assertEqual(data_fetcher_agent.name, 'data_fetcher')
    
    def test_data_fetcher_agent_has_tools(self):
        """Test that data_fetcher_agent has tools configured."""
        self.assertIsNotNone(data_fetcher_agent.tools)
        self.assertIsInstance(data_fetcher_agent.tools, list)
        self.assertEqual(len(data_fetcher_agent.tools), 2)
    
    def test_crisis_line_agent_is_defined(self):
        """Test that crisis_line_agent is defined."""
        self.assertIsNotNone(crisis_line_agent)
    
    def test_crisis_line_agent_has_required_attributes(self):
        """Test that crisis_line_agent has required attributes."""
        self.assertTrue(hasattr(crisis_line_agent, 'model'))
        self.assertTrue(hasattr(crisis_line_agent, 'name'))
        self.assertTrue(hasattr(crisis_line_agent, 'description'))
        self.assertTrue(hasattr(crisis_line_agent, 'instruction'))
        self.assertTrue(hasattr(crisis_line_agent, 'tools'))
    
    def test_crisis_line_agent_model(self):
        """Test that crisis_line_agent uses the correct model."""
        self.assertEqual(crisis_line_agent.model, 'gemini-2.5-flash')
    
    def test_crisis_line_agent_name(self):
        """Test that crisis_line_agent has the correct name."""
        self.assertEqual(crisis_line_agent.name, 'crisis_line')
    
    def test_crisis_line_agent_has_tools(self):
        """Test that crisis_line_agent has tools configured."""
        self.assertIsNotNone(crisis_line_agent.tools)
        self.assertIsInstance(crisis_line_agent.tools, list)
        self.assertEqual(len(crisis_line_agent.tools), 2)
    
    def test_agents_are_different_instances(self):
        """Test that all agents are different instances."""
        agents = [root_agent, data_fetcher_agent, crisis_line_agent]
        
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents):
                if i != j:
                    self.assertIsNot(agent1, agent2)
    
    def test_agent_names_are_unique(self):
        """Test that all agent names are unique."""
        agent_names = [
            root_agent.name,
            data_fetcher_agent.name,
            crisis_line_agent.name
        ]
        
        self.assertEqual(len(agent_names), len(set(agent_names)))


if __name__ == '__main__':
    unittest.main()