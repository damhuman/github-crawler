import unittest
from unittest.mock import MagicMock, patch
from src.github_crawler import GitHubCrawler
from src.enums import SearchType
from src.exceptions import GitHubCrawlerException

class TestGitHubCrawler(unittest.TestCase):
    def setUp(self):
        self.proxies = ['http://proxy1.com', 'http://proxy2.com']
        self.keywords = ['python', 'web scraping']
        self.search_type = SearchType.REPOSITORIES.value
        
        # Create the crawler with mocked dependencies
        with patch('src.github_crawler.GitHubClient'), patch('src.github_crawler.ResultParser'):
            self.crawler = GitHubCrawler(
                proxies=self.proxies,
                keywords=self.keywords,
                search_type=self.search_type,
                include_extra_info=False
            )
            self.crawler.client = MagicMock()
            self.crawler.parser = MagicMock()
    
    def test_init(self):
        """Test the initialization of GitHubCrawler"""
        self.assertEqual(self.crawler.keywords, self.keywords)
        self.assertEqual(self.crawler.search_type, SearchType.REPOSITORIES)
        self.assertEqual(self.crawler.include_extra_info, False)
    
    def test_execute_search_success(self):
        """Test successful search execution"""
        # Mock the _search method
        expected_results = [{'url': 'https://github.com/user/repo'}]
        self.crawler._search = MagicMock(return_value=expected_results)
        
        # Execute the search
        results = self.crawler.execute_search()
        
        # Verify the results
        self.assertEqual(results, expected_results)
        self.crawler._search.assert_called_once_with(self.keywords)
    
    def test_execute_search_failure(self):
        """Test search execution with an exception"""
        # Mock the _search method to raise an exception
        self.crawler._search = MagicMock(side_effect=GitHubCrawlerException('Search failed'))
        
        # Execute the search
        results = self.crawler.execute_search()
        
        # Verify the results
        self.assertEqual(results, [])
        self.crawler._search.assert_called_once_with(self.keywords)
    
    def test_search(self):
        """Test the _search method"""
        # Mock the dependencies
        mock_response = MagicMock()
        self.crawler.client.search.return_value = mock_response
        
        expected_results = [{'url': 'https://github.com/user/repo'}]
        self.crawler.parser.parse_search_results.return_value = expected_results
        
        # Execute the search
        results = self.crawler._search(self.keywords)
        
        # Verify the results
        self.assertEqual(results, expected_results)
        self.crawler.client.search.assert_called_once_with(self.keywords, SearchType(self.search_type))
        self.crawler.parser.parse_search_results.assert_called_once_with(mock_response.text, SearchType(self.search_type))
    
    def test_search_with_extra_info(self):
        """Test the _search method with extra info"""
        # Set up the crawler to include extra info
        self.crawler.include_extra_info = True
        
        # Mock the dependencies
        mock_response = MagicMock()
        self.crawler.client.search.return_value = mock_response
        
        initial_results = [{'url': 'https://github.com/user/repo'}]
        self.crawler.parser.parse_search_results.return_value = initial_results
        
        expected_results = [{'url': 'https://github.com/user/repo', 'extra': {'owner': 'user'}}]
        self.crawler._include_extra_info = MagicMock(return_value=expected_results)
        
        # Execute the search
        results = self.crawler._search(self.keywords)
        
        # Verify the results
        self.assertEqual(results, expected_results)
        self.crawler._include_extra_info.assert_called_once_with(initial_results)
    
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_include_extra_info(self, mock_executor):
        """Test the _include_extra_info method"""
        # Set up the mock executor
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Set up the mock futures
        mock_future = MagicMock()
        mock_future.result.return_value = {'owner': 'user', 'language_stats': {'Python': 100.0}}
        mock_executor_instance.submit.return_value = mock_future
        
        # Set up the concurrent.futures.as_completed mock
        with patch('concurrent.futures.as_completed', return_value=[mock_future]):
            # Execute the method
            results = [{'url': 'https://github.com/user/repo'}]
            updated_results = self.crawler._include_extra_info(results)
            
            # Verify the results
            self.assertEqual(updated_results[0]['extra'], {'owner': 'user', 'language_stats': {'Python': 100.0}})
    
    def test_get_repository_extra_info(self):
        """Test the _get_repository_extra_info method"""
        # Mock the dependencies
        repo_url = 'https://github.com/user/repo'
        mock_response = MagicMock()
        mock_response.text = '<html>Mock HTML</html>'
        self.crawler.client.get_repository.return_value = mock_response
        
        expected_info = {'owner': 'user', 'language_stats': {'Python': 100.0}}
        self.crawler.parser.parse_repository_info.return_value = expected_info
        
        # Execute the method
        info = self.crawler._get_repository_extra_info(repo_url)
        
        # Verify the results
        self.assertEqual(info, expected_info)
        self.crawler.client.get_repository.assert_called_once_with(repo_url)
        self.crawler.parser.parse_repository_info.assert_called_once_with(mock_response.text, repo_url) 