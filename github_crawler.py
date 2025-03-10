import random
import requests
import logging
import json
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin
from enum import Enum

logger = logging.getLogger(__name__)

class SearchType(Enum):
    REPOSITORIES = "repositories"
    ISSUES = "issues"
    DISCUSSIONS = "discussions"

class GitHubCrawlerException(Exception):
    pass

class GitHubCrawler:
    SEARCH_URL = "https://github.com/search"
    
    def __init__(self, 
                 proxies: List[str], 
                 keywords: List[str], 
                 search_type: str, 
                 include_extra_info: bool = False):
        self.proxies = proxies
        self.search_type = SearchType(search_type.lower())
        self.session = requests.Session()
        self.keywords = keywords
        self.include_extra_info = include_extra_info
        logger.info(f"Initializing GitHubCrawler with {self.search_type.value} search type")
        logger.info(f"Keywords: {self.keywords}")
        logger.info(f"Include extra info: {self.include_extra_info}")

    def execute_search(self, output_file_path: str = "results.json") -> List[Dict[str, Any]]:
        """
        Execute search with keywords and save results to output file
        """
        try:
            results = self._search(self.keywords)
        except GitHubCrawlerException as e:
            logger.error(f"Error during search: {str(e)}")
            return []
        
        response = {
            "keywords": self.keywords,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "search_type": self.search_type.value,
            "results": results
        }
        with open(output_file_path, 'w') as f:
            json.dump(response, f, indent=2)
            
        logger.info(f"Results saved to {output_file_path}")
        return results
    
    def _get_random_proxy(self) -> Dict[str, str]:
        if not self.proxies:
            return {}
        proxy = random.choice(self.proxies)
        logger.info(f"Using proxy: {proxy}")
        return {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
    
    def _make_request(self, url: str, params: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Make a request to the GitHub API
        """
        proxy = self._get_random_proxy()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        try:
            response = self.session.get(
            url, 
            params=params,
            proxies=proxy,
            headers=headers, 
                timeout=10
            )
            logger.info(f"Response status: {response.status_code}")
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error during request: {str(e)}")
            raise GitHubCrawlerException(f"Error during request: {str(e)}")
    
    def _search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Search GitHub and return results
        """
        params = {
            "q": " ".join(keywords),
            "type": self.search_type.value
        }
        response = self._make_request(self.SEARCH_URL, params)
        results = self._parse_results(response.text)
        
        if self.search_type == SearchType.REPOSITORIES and self.include_extra_info:
            for result in results:
                extra_info = self._get_repository_extra_info(result["url"])
                if extra_info:
                    result["extra"] = extra_info
        return results
    
        
    def _parse_results(self, html: str) -> List[Dict[str, Any]]:
        logger.info(f"Parsing results of {self.search_type.value} search")
        
        soup = BeautifulSoup(html, 'html.parser')
        divs = soup.find_all('div', class_="search-title")
        urls = [div.find('a').get('href') for div in divs]
        
        logger.info(f"Found {len(urls)} results")
        
        results = []
        for url in urls:
            if not url.startswith('http'):
                url = urljoin("https://github.com", url)
                
            results.append({
                "url": url,
            })
        return results
    
    def _get_repository_extra_info(self, repo_url: str) -> Dict[str, Any]:
        try:
            logger.info(f"Getting extra info for {repo_url}")
            response = self._make_request(repo_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            language_stats = {}
            layout_sidebar = soup.find('div', class_="Layout-sidebar")
            languages = layout_sidebar.find_all('li', class_='d-inline')
            for language in languages:
                spans = language.find_all('span')
                lang, percentage = spans[0].text, spans[1].text
                language_stats[lang] = float(percentage.strip('%'))
            
            return {
                "owner": repo_url.split('/')[-2],
                "language_stats": language_stats
            }
        except Exception as e:
            logger.error(f"Error getting extra info for {repo_url}: {str(e)}")
            return {
                "owner": "",
                "language_stats": {}
            }