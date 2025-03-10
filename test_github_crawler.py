import unittest
from unittest.mock import patch, MagicMock, call
import json
import os
from github_crawler import GitHubCrawler, GitHubCrawlerException, SearchType
import requests

class TestGitHubCrawler(unittest.TestCase):
    def setUp(self):
        self.proxies = ["194.126.37.94:8080", "13.78.125.167:8080"]
        self.keywords = ["python", "django"]
        self.search_type = "Repositories"
        self.crawler = GitHubCrawler(
            proxies=self.proxies,
            keywords=self.keywords,
            search_type=self.search_type,
            include_extra_info=False
        )
        
        # Create a crawler with extra info enabled
        self.crawler_with_extra = GitHubCrawler(
            proxies=self.proxies,
            keywords=self.keywords,
            search_type=self.search_type,
            include_extra_info=True
        )

    def test_initialization(self):
        """Test crawler initialization with different parameters"""
        # Test with repositories
        crawler = GitHubCrawler(
            proxies=self.proxies,
            keywords=self.keywords,
            search_type="Repositories",
            include_extra_info=True
        )
        self.assertEqual(crawler.search_type, SearchType.REPOSITORIES)
        self.assertTrue(crawler.include_extra_info)
        
        # Test with issues
        crawler = GitHubCrawler(
            proxies=self.proxies,
            keywords=self.keywords,
            search_type="Issues",
            include_extra_info=False
        )
        self.assertEqual(crawler.search_type, SearchType.ISSUES)
        self.assertFalse(crawler.include_extra_info)
        
        # Test with discussions
        crawler = GitHubCrawler(
            proxies=self.proxies,
            keywords=self.keywords,
            search_type="Discussions",
            include_extra_info=False
        )
        self.assertEqual(crawler.search_type, SearchType.DISCUSSIONS)

    def test_get_random_proxy(self):
        """Test random proxy selection"""
        # Test with proxies
        proxy = self.crawler._get_random_proxy()
        self.assertIn(proxy["http"].replace("http://", ""), self.proxies)
        
        # Test with empty proxies
        crawler = GitHubCrawler(
            proxies=[],
            keywords=self.keywords,
            search_type=self.search_type
        )
        proxy = crawler._get_random_proxy()
        self.assertEqual(proxy, {})

    def test_build_search_url_params(self):
        """Test building search URL parameters"""
        params = {
            "q": "python django",
            "type": "repositories"
        }
        self.assertEqual(
            params,
            {"q": " ".join(self.keywords), "type": self.crawler.search_type.value}
        )

    @patch('requests.Session.get')
    def test_make_request(self, mock_get):
        """Test making HTTP requests"""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test successful request
        response = self.crawler._make_request("https://github.com", {"q": "test"})
        self.assertEqual(response, mock_response)
        
        # Test request exception
        mock_get.side_effect = requests.RequestException("Connection error")
        with self.assertRaises(GitHubCrawlerException):
            self.crawler._make_request("https://github.com", {"q": "test"})

    @patch('github_crawler.GitHubCrawler._make_request')
    def test_parse_results(self, mock_make_request):
        """Test parsing search results"""
        # Setup mock response with HTML
        mock_response = MagicMock()
        mock_response.text = """
        <div class="search-title">
            <a href="/user1/repo1">Repo 1</a>
        </div>
        <div class="search-title">
            <a href="/user2/repo2">Repo 2</a>
        </div>
        <div class="search-title">
            <a href="https://github.com/user3/repo3">Repo 3</a>
        </div>
        """
        mock_make_request.return_value = mock_response
        
        # Test parsing
        params = {"q": " ".join(self.keywords), "type": self.crawler.search_type.value}
        response = self.crawler._make_request(self.crawler.SEARCH_URL, params)
        results = self.crawler._parse_results(response.text)
        
        # Verify results
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["url"], "https://github.com/user1/repo1")
        self.assertEqual(results[1]["url"], "https://github.com/user2/repo2")
        self.assertEqual(results[2]["url"], "https://github.com/user3/repo3")

    @patch('github_crawler.GitHubCrawler._make_request')
    def test_get_repository_extra_info(self, mock_make_request):
        """Test getting extra repository information"""
        # Setup mock response with HTML
        mock_response = MagicMock()
        mock_response.text = """
        <div class="Layout-sidebar">
            <li class="d-inline">
                <span>Python</span>
                <span>80.5%</span>
            </li>
            <li class="d-inline">
                <span>JavaScript</span>
                <span>15.3%</span>
            </li>
            <li class="d-inline">
                <span>HTML</span>
                <span>4.2%</span>
            </li>
        </div>
        """
        mock_make_request.return_value = mock_response
        
        # Test getting extra info
        repo_url = "https://github.com/testuser/testrepo"
        extra_info = self.crawler._get_repository_extra_info(repo_url)
        
        # Verify results
        self.assertEqual(extra_info["owner"], "testuser")
        self.assertEqual(len(extra_info["language_stats"]), 3)
        self.assertEqual(extra_info["language_stats"]["Python"], 80.5)
        self.assertEqual(extra_info["language_stats"]["JavaScript"], 15.3)
        self.assertEqual(extra_info["language_stats"]["HTML"], 4.2)
        
        # Test exception handling
        mock_make_request.side_effect = Exception("Error")
        extra_info = self.crawler._get_repository_extra_info(repo_url)
        self.assertEqual(extra_info["owner"], "")
        self.assertEqual(extra_info["language_stats"], {})

    @patch('github_crawler.GitHubCrawler._search')
    def test_execute_search(self, mock_search):
        """Test executing search and saving results"""
        # Setup mock
        mock_results = [{"url": "https://github.com/user/repo"}]
        mock_search.return_value = mock_results
        
        # Test with output file
        output_file = "test_results.json"
        results = self.crawler.execute_search(output_file)
        
        # Verify results
        self.assertEqual(results, mock_results)
        self.assertTrue(os.path.exists(output_file))
        
        # Verify file contents
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data["keywords"], self.keywords)
            self.assertEqual(saved_data["search_type"], self.crawler.search_type.value)
            self.assertEqual(saved_data["results"], mock_results)
        
        # Clean up
        os.remove(output_file)
        
        # Test with exception
        mock_search.side_effect = GitHubCrawlerException("Search error")
        results = self.crawler.execute_search(output_file)
        self.assertEqual(results, [])

    @patch('github_crawler.GitHubCrawler._make_request')
    @patch('github_crawler.GitHubCrawler._get_repository_extra_info')
    def test_search_with_extra_info(self, mock_get_extra, mock_make_request):
        """Test search with extra repository information"""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.text = """
        <div class="search-title">
            <a href="/user1/repo1">Repo 1</a>
        </div>
        <div class="search-title">
            <a href="/user2/repo2">Repo 2</a>
        </div>
        """
        mock_make_request.return_value = mock_response
        
        mock_extra_info = {
            "owner": "testuser",
            "language_stats": {"Python": 100.0}
        }
        mock_get_extra.return_value = mock_extra_info
        
        # Test search with extra info
        results = self.crawler_with_extra._search(self.keywords)
        
        # Verify results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["url"], "https://github.com/user1/repo1")
        self.assertEqual(results[0]["extra"], mock_extra_info)
        self.assertEqual(results[1]["url"], "https://github.com/user2/repo2")
        self.assertEqual(results[1]["extra"], mock_extra_info)
        
        # Verify mock calls
        self.assertEqual(mock_get_extra.call_count, 2)
        mock_get_extra.assert_has_calls([
            call("https://github.com/user1/repo1"),
            call("https://github.com/user2/repo2")
        ])
        
        # Test search without extra info
        mock_get_extra.reset_mock()
        results = self.crawler._search(self.keywords)
        
        # Verify no extra info calls
        mock_get_extra.assert_not_called()

    @patch('github_crawler.GitHubCrawler._make_request')
    def test_search_with_different_types(self, mock_make_request):
        """Test search with different search types"""
        # Setup mock
        mock_response = MagicMock()
        mock_response.text = """
        <div class="search-title">
            <a href="/user1/repo1">Repo 1</a>
        </div>
        """
        mock_make_request.return_value = mock_response
        
        # Test with issues
        crawler = GitHubCrawler(
            proxies=self.proxies,
            keywords=self.keywords,
            search_type="Issues"
        )
        results = crawler._search(self.keywords)
        
        # Verify params
        mock_make_request.assert_called_with(
            crawler.SEARCH_URL,
            {"q": "python django", "type": "issues"}
        )
        
        # Test with discussions
        crawler = GitHubCrawler(
            proxies=self.proxies,
            keywords=self.keywords,
            search_type="Discussions"
        )
        results = crawler._search(self.keywords)
        
        # Verify params
        mock_make_request.assert_called_with(
            crawler.SEARCH_URL,
            {"q": "python django", "type": "discussions"}
        )

if __name__ == '__main__':
    unittest.main() 