import unittest
from unittest.mock import MagicMock, patch
import requests
from src.github_client import GitHubClient
from src.enums import SearchType
from src.exceptions import GitHubCrawlerException

class TestGitHubClient(unittest.TestCase):
    def setUp(self):
        self.proxies = ['127.0.0.1:8080', '127.0.0.1:8020']
        self.client = GitHubClient(self.proxies)
    
    def test_init(self):
        """Test initialization of GitHubClient"""
        proxy = self.client.proxy['http'].split('//')[1]
        self.assertIn(proxy, self.proxies)
        self.assertIsNotNone(self.client.session)
        self.assertIsInstance(self.client.session, requests.Session)
    
    @patch('src.github_client.GitHubClient.make_request')
    def test_search(self, mock_make_request):
        """Test search method"""
        # Set up mock
        mock_response = MagicMock()
        mock_make_request.return_value = mock_response
        
        # Call search
        keywords = ['python', 'web scraping']
        search_type = SearchType.REPOSITORIES
        response = self.client.search(keywords, search_type)
        
        # Verify
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(
            'https://github.com/search',
            {'q': 'python web scraping', 'type': 'repositories'}
        )
    
    @patch('src.github_client.GitHubClient.make_request')
    def test_get_repository(self, mock_make_request):
        """Test get_repository method"""
        # Set up mock
        mock_response = MagicMock()
        mock_make_request.return_value = mock_response
        
        # Call get_repository
        repo_url = 'https://github.com/user/repo'
        response = self.client.get_repository(repo_url)
        
        # Verify
        self.assertEqual(response, mock_response)
        mock_make_request.assert_called_once_with(repo_url) 