import logging
import random
from typing import Dict, List, Optional

import requests

from src.enums import SearchType
from src.exceptions import GitHubCrawlerException


class GitHubClient:
    """Responsible for making HTTP requests to GitHub"""

    BASE_URL = 'https://github.com'
    
    def __init__(self, proxies: List[str], logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.proxy = self._select_random_proxy(proxies)
        self.logger.info(f'Selected proxy: {self.proxy}')
    
    def _select_random_proxy(self, proxies: List[str]) -> Dict[str, str]:
        if not proxies:
            return {}
        proxy = random.choice(proxies)
        return {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
    
    def make_request(self, url: str, params: Optional[Dict[str, str]] = None) -> requests.Response:
        """Make a request to the GitHub API"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        try:
            response = self.session.get(
                url, 
                params=params,
                proxies=self.proxy,
                headers=headers, 
                timeout=10
            )
            self.logger.info(f'Response status: {response.status_code}')
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f'Error during request: {str(e)}')
            raise GitHubCrawlerException(f'Error during request: {str(e)}')

    def get_repository(self, repo_url: str) -> requests.Response:
        """Get extra information for a repository"""
        self.logger.info(f'Getting info for {repo_url}')
        response = self.make_request(repo_url)
        return response
    
    def search(self, keywords: List[str], search_type: SearchType) -> requests.Response:
        """Search for repositories, issues, or discussions"""
        self.logger.info(f'Searching for {search_type.value} with keywords: {keywords}')
        params = {
            'q': ' '.join(keywords),
            'type': search_type.value
        }
        url = f'{self.BASE_URL}/search'
        response = self.make_request(url, params)
        return response
