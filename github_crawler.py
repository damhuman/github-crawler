import random
import requests
import logging
import json
from bs4 import BeautifulSoup
from typing import List, Dict
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
    
    def __init__(self, proxies: List[str], keywords: List[str], search_type: str):
        self.proxies = proxies
        self.search_type = SearchType(search_type.lower())
        self.session = requests.Session()
        self.keywords = keywords

    def execute_search(self, output_file_path: str = "results.json") -> List[Dict[str, str]]:
        """
        Execute search with keywords and save results to output file
        """
        results = self._search(self.keywords)
        
        response = {
            "keywords": self.keywords,
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
    
    def _make_request(self, url: str, params: Dict[str, str]) -> requests.Response:
        """
        Make a request to the GitHub API
        """
        proxy = self._get_random_proxy()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
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
    
    def _search(self, keywords: List[str]) -> List[Dict[str, str]]:
        """
        Search GitHub and return results
        """
        params = {
            "q": " ".join(keywords),
            "type": self.search_type.value
        }
        try:
            response = self._make_request(self.SEARCH_URL, params)
            return self._parse_results(response.text)
        except requests.RequestException as e:
            logger.error(f"Error during request: {str(e)}")
            raise GitHubCrawlerException(f"Error during request: {str(e)}")
        
    def _parse_results(self, html: str) -> List[Dict[str, str]]:
        logger.info(f"Parsing results of {self.search_type.value} search")
        
        soup = BeautifulSoup(html, 'html.parser')
        divs = soup.find_all('div', class_="search-title")
        urls = [div.find('a').get('href') for div in divs]
        
        logger.info(f"Found {len(urls)} results")
        
        results = []
        for url in urls:
            results.append({
                "url": url,
            })
        return results