import argparse
import json
import logging
from src.github_crawler import GitHubCrawler
from src.validators import validate_input_data


def parse_arguments():
    parser = argparse.ArgumentParser(description='GitHub Crawler')
    parser.add_argument('input_file', help='JSON input file path')
    parser.add_argument('--output_file', help='Output file path', default='data/results.json')
    parser.add_argument('--extra_info', help='Include extra info', action='store_true')
    return parser.parse_args()


class GitHubCrawlerApp:
    def __init__(self):
        self.args = parse_arguments()
        self.logger = logging.getLogger(__name__)
        
    def load_input_data(self):
        with open(self.args.input_file, 'r') as f:
            input_data = json.load(f)
        validate_input_data(input_data)
        self.logger.info(f'Input data: {input_data}')
        return input_data
        
    def save_output(self, results):
        with open(self.args.output_file, 'w') as f:
            json.dump(results, f, indent=2)
        self.logger.info(f'Results: {json.dumps(results, indent=2)}')
        
    def run(self):
        try:
            input_data = self.load_input_data()
            crawler = GitHubCrawler(
                proxies=input_data['proxies'], 
                search_type=input_data['type'], 
                keywords=input_data['keywords'],
                include_extra_info=self.args.extra_info,
            )
            results = crawler.execute_search()
            self.save_output(results)
        except Exception as e:
            self.logger.error(f'Error: {str(e)}')


def main():
    logging.basicConfig(level=logging.INFO)
    app = GitHubCrawlerApp()
    app.run()


if __name__ == '__main__':
    main()