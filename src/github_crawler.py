import concurrent.futures
import logging
from typing import Any, Dict, List

from src.enums import SearchType
from src.github_client import GitHubClient
from src.exceptions import GitHubCrawlerException
from src.parser import ResultParser


class GitHubCrawler:
    """Coordinates the crawling process"""
    
    def __init__(self, 
                 proxies: List[str], 
                 keywords: List[str], 
                 search_type: SearchType, 
                 include_extra_info: bool = False):
        self.logger = logging.getLogger(__name__)
        self.search_type = SearchType(search_type.lower())
        self.keywords = keywords
        self.include_extra_info = include_extra_info
        
        self.client = GitHubClient(proxies)
        self.parser = ResultParser()
        
        self.logger.info(f'Initializing GitHubCrawler with {self.search_type.value} search type')
        self.logger.info(f'Keywords: {self.keywords}')
        self.logger.info(f'Include extra info: {self.include_extra_info}')

    def execute_search(self) -> List[Dict[str, Any]]:
        try:
            results = self._search(self.keywords)
        except GitHubCrawlerException as e:
            self.logger.error(f'Error during search: {str(e)}')
            return []
        
        return results
    
    def _search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search GitHub and return results"""
        response = self.client.search(keywords, self.search_type)
        results = self.parser.parse_search_results(response.text, self.search_type)
        
        if self.search_type == SearchType.REPOSITORIES and self.include_extra_info:
            results = self._include_extra_info(results)
        return results
    
    def _include_extra_info(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(self._get_repository_extra_info, result['url']): result 
                for result in results
            }
            for future in concurrent.futures.as_completed(future_to_url):
                result = future_to_url[future]
                try:
                    extra_info = future.result()
                    if extra_info:
                        result['extra'] = extra_info
                except Exception as exc:
                    self.logger.error(f'Error processing {result["url"]}: {exc}')
        return results
    
    def _get_repository_extra_info(self, repo_url: str) -> Dict[str, Any]:
        self.logger.info(f'Getting extra info for {repo_url}')
        response = self.client.get_repository(repo_url)
        return self.parser.parse_repository_info(response.text, repo_url)