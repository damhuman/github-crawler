import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from src.enums import SearchType


class ResultParser:
    """Responsible for parsing HTML responses"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_search_results(self, html: str, search_type: SearchType) -> List[Dict[str, Any]]:
        self.logger.info(f'Parsing results of {search_type.value} search')
        
        soup = BeautifulSoup(html, 'html.parser')
        divs = soup.find_all('div', class_='search-title')
        urls = [div.find('a').get('href') for div in divs]
        
        self.logger.info(f'Found {len(urls)} results')
        
        results = []
        for url in urls:
            if not url.startswith('http'):
                url = urljoin('https://github.com', url)
                
            results.append({
                'url': url,
            })
        return results
    
    def parse_repository_info(self, html: str, repo_url: str) -> Dict[str, Any]:
        try:
            owner = repo_url.split('/')[-2]
            soup = BeautifulSoup(html, 'html.parser')
            language_stats = {}
            layout_sidebar = soup.find('div', class_='Layout-sidebar')
            languages = layout_sidebar.find_all('li', class_='d-inline')
            for language in languages:
                spans = language.find_all('span')
                lang, percentage = spans[-2].text, spans[-1].text
                language_stats[lang] = float(percentage.strip('%'))
            
            return {
                'owner': owner,
                'language_stats': language_stats
            }
        except Exception as e:
            self.logger.error(f'Error parsing info for {repo_url}: {str(e)}')
            return {
                'owner': owner,
                'language_stats': {}
            }
