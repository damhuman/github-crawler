import json
import logging
import argparse
from github_crawler import GitHubCrawler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='GitHub Crawler')
    parser.add_argument('input_file', help='JSON input file path')
    parser.add_argument('--output_file', help='Output file path', default="data/results.json")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as f:
            input_data = json.load(f)
        logger.info(f"Input data: {input_data}")
        crawler = GitHubCrawler(proxies=input_data['proxies'], 
                                search_type=input_data['type'], 
                                keywords=input_data['keywords'])
        results = crawler.execute_search(args.output_file)

        print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 