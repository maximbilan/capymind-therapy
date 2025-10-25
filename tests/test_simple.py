import unittest
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSimple(unittest.TestCase):
    """Simple tests that don't require external dependencies."""
    
    def test_project_structure(self):
        """Test that the project has the expected structure."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Check that main files exist
        self.assertTrue(os.path.exists(os.path.join(project_root, 'main.py')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'requirements.txt')))
        self.assertTrue(os.path.exists(os.path.join(project_root, 'README.md')))
        
        # Check that agent directory exists
        agent_dir = os.path.join(project_root, 'capymind_agent')
        self.assertTrue(os.path.exists(agent_dir))
        
        # Check that agent files exist
        self.assertTrue(os.path.exists(os.path.join(agent_dir, 'agent.py')))
        self.assertTrue(os.path.exists(os.path.join(agent_dir, 'prompt.py')))
        self.assertTrue(os.path.exists(os.path.join(agent_dir, '__init__.py')))
        
        # Check that tools directory exists
        tools_dir = os.path.join(agent_dir, 'tools')
        self.assertTrue(os.path.exists(tools_dir))
        self.assertTrue(os.path.exists(os.path.join(tools_dir, 'firestore_data.py')))
        self.assertTrue(os.path.exists(os.path.join(tools_dir, 'format_data.py')))
        
        # Check that sub-agents exist
        sug_agents_dir = os.path.join(agent_dir, 'sug_agents')
        self.assertTrue(os.path.exists(sug_agents_dir))
        self.assertTrue(os.path.exists(os.path.join(sug_agents_dir, 'data_fetcher')))
        self.assertTrue(os.path.exists(os.path.join(sug_agents_dir, 'crysis_line')))
    
    def test_main_py_content(self):
        """Test that main.py has expected content."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_py_path = os.path.join(project_root, 'main.py')
        
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Check for key imports
        self.assertIn('import os', content)
        self.assertIn('import uvicorn', content)
        self.assertIn('from fastapi import FastAPI', content)
        self.assertIn('from google.adk.cli.fast_api import get_fast_api_app', content)
        
        # Check for key constants
        self.assertIn('AGENT_DIR', content)
        self.assertIn('SESSION_SERVICE_URI', content)
        self.assertIn('ALLOWED_ORIGINS', content)
        self.assertIn('SERVE_WEB_INTERFACE', content)
        
        # Check for main execution block
        self.assertIn('if __name__ == "__main__":', content)
        self.assertIn('uvicorn.run', content)
    
    def test_requirements_txt_content(self):
        """Test that requirements.txt has expected content."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        requirements_path = os.path.join(project_root, 'requirements.txt')
        
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        # Check for key dependencies
        self.assertIn('google-adk', content)
        self.assertIn('google-cloud-firestore', content)
    
    def test_prompt_file_exists(self):
        """Test that prompt.py exists and has content."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(project_root, 'capymind_agent', 'prompt.py')
        
        self.assertTrue(os.path.exists(prompt_path))
        
        with open(prompt_path, 'r') as f:
            content = f.read()
        
        # Check for key prompt elements
        self.assertIn('CAPYMIND_AGENT_PROMPT', content)
        self.assertIn('prompt =', content)
        self.assertIn('therapist', content.lower())
        self.assertIn('crisis', content.lower())
    
    def test_tools_files_exist(self):
        """Test that tool files exist and have expected content."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Test firestore_data.py
        firestore_path = os.path.join(project_root, 'capymind_agent', 'tools', 'firestore_data.py')
        self.assertTrue(os.path.exists(firestore_path))
        
        with open(firestore_path, 'r') as f:
            firestore_content = f.read()
        
        self.assertIn('def capy_firestore_data', firestore_content)
        self.assertIn('def _to_jsonable', firestore_content)
        self.assertIn('def _get_firestore_client', firestore_content)
        
        # Test format_data.py
        format_path = os.path.join(project_root, 'capymind_agent', 'tools', 'format_data.py')
        self.assertTrue(os.path.exists(format_path))
        
        with open(format_path, 'r') as f:
            format_content = f.read()
        
        self.assertIn('def format_data', format_content)
        self.assertIn('format_data_tool', format_content)
    
    def test_sub_agent_files_exist(self):
        """Test that sub-agent files exist."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Test data_fetcher
        data_fetcher_dir = os.path.join(project_root, 'capymind_agent', 'sug_agents', 'data_fetcher')
        self.assertTrue(os.path.exists(os.path.join(data_fetcher_dir, 'agent.py')))
        self.assertTrue(os.path.exists(os.path.join(data_fetcher_dir, 'prompt.py')))
        self.assertTrue(os.path.exists(os.path.join(data_fetcher_dir, '__init__.py')))
        
        # Test crisis_line
        crisis_line_dir = os.path.join(project_root, 'capymind_agent', 'sug_agents', 'crysis_line')
        self.assertTrue(os.path.exists(os.path.join(crisis_line_dir, 'agent.py')))
        self.assertTrue(os.path.exists(os.path.join(crisis_line_dir, 'prompt.py')))
        self.assertTrue(os.path.exists(os.path.join(crisis_line_dir, '__init__.py')))
    
    def test_scripts_directory(self):
        """Test that scripts directory exists with expected files."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts_dir = os.path.join(project_root, 'scripts')
        
        self.assertTrue(os.path.exists(scripts_dir))
        self.assertTrue(os.path.exists(os.path.join(scripts_dir, 'deploy_adk_cloud_run.sh')))
        self.assertTrue(os.path.exists(os.path.join(scripts_dir, 'deployment_account_perms.sh')))
        self.assertTrue(os.path.exists(os.path.join(scripts_dir, 'setup_dev_env.sh')))
    
    def test_readme_exists(self):
        """Test that README.md exists and has content."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        readme_path = os.path.join(project_root, 'README.md')
        
        self.assertTrue(os.path.exists(readme_path))
        
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Check for key sections
        self.assertIn('# CapyMind Session', content)
        self.assertIn('Features', content)  # Check for "Features" anywhere in the content
        self.assertIn('Quick Start', content)
        self.assertIn('Architecture', content)


if __name__ == '__main__':
    unittest.main()