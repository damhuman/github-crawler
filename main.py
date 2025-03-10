import json
import logging
import argparse
from github_crawler import GitHubCrawler, SearchType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def validate_input_data(input_data):
    """
    Validates the input data for the GitHub crawler
    
    Args:
        input_data (dict): The input data to validate
        
    Raises:
        ValueError: If any validation fails
        
    Returns:
        bool: True if validation passes
    """
    required_fields = ['keywords', 'proxies', 'type']
    missing_fields = [field for field in required_fields if field not in input_data]
    
    if missing_fields:
        raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}")
    
    # Validate data types and content
    if not isinstance(input_data['keywords'], list) or not input_data['keywords']:
        raise ValueError("Keywords must be a non-empty list")
    
    if not isinstance(input_data['proxies'], list):
        raise ValueError("Proxies must be a list")
    
    valid_types = [t.value for t in SearchType]
    if input_data['type'] not in valid_types:
        raise ValueError(f"Invalid search type: {input_data['type']}. Must be one of: {', '.join(valid_types)}")
    
    logger.info("Input data validation passed")
    return True

def main():
    parser = argparse.ArgumentParser(description='GitHub Crawler')
    parser.add_argument('input_file', help='JSON input file path')
    parser.add_argument('--output_file', help='Output file path', default="data/results.json")
    parser.add_argument('--extra_info', help='Include extra info', action='store_true')
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as f:
            input_data = json.load(f)
        validate_input_data(input_data)
        logger.info(f"Input data: {input_data}")
        crawler = GitHubCrawler(proxies=input_data['proxies'], 
                                search_type=input_data['type'], 
                                keywords=input_data['keywords'],
                                include_extra_info=args.extra_info)
        results = crawler.execute_search(args.output_file)

        print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 