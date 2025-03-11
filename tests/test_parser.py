import unittest
from unittest.mock import MagicMock, patch
from src.parser import ResultParser
from src.enums import SearchType

class TestResultParser(unittest.TestCase):
    def setUp(self):
        self.parser = ResultParser()
    
    def test_parse_search_results(self):
        """Test parsing search results"""
        # Create a mock HTML with search results
        html = """
        <div class="search-title"><a href="/user1/repo1">Repo 1</a></div>
        <div class="search-title"><a href="/user2/repo2">Repo 2</a></div>
        <div class="search-title"><a href="https://github.com/user3/repo3">Repo 3</a></div>
        """
        
        # Parse the results
        results = self.parser.parse_search_results(html, SearchType.REPOSITORIES)
        
        # Verify the results
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['url'], 'https://github.com/user1/repo1')
        self.assertEqual(results[1]['url'], 'https://github.com/user2/repo2')
        self.assertEqual(results[2]['url'], 'https://github.com/user3/repo3')
    
    def test_parse_repository_info_success(self):
        """Test parsing repository info successfully"""
        # Create a mock HTML with repository info
        html = """
        <div class="Layout-sidebar">
            <li class="d-inline">
                <span>Python</span>
                <span>80%</span>
            </li>
            <li class="d-inline">
                <span>JavaScript</span>
                <span>20%</span>
            </li>
        </div>
        """
        
        repo_url = 'https://github.com/user/repo'
        
        # Parse the info
        info = self.parser.parse_repository_info(html, repo_url)
        
        # Verify the info
        self.assertEqual(info['owner'], 'user')
        self.assertEqual(info['language_stats']['Python'], 80.0)
        self.assertEqual(info['language_stats']['JavaScript'], 20.0)
    
    def test_parse_repository_info_error(self):
        """Test parsing repository info with an error"""
        # Create an invalid HTML
        html = '<div>Invalid HTML</div>'
        
        repo_url = 'https://github.com/user/repo'
        
        # Parse the info
        info = self.parser.parse_repository_info(html, repo_url)
        
        # Verify the info
        self.assertEqual(info['owner'], 'user')
        self.assertEqual(info['language_stats'], {}) 