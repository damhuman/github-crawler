from src.enums import SearchType


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
    # Check if all required fields are present
    required_fields = {'keywords', 'proxies', 'type'}
    missing_fields = required_fields - input_data.keys()
    
    if missing_fields:
        raise ValueError(f'Missing required field(s): {", ".join(missing_fields)}')
    
    # Validate data types and content
    if not isinstance(input_data['keywords'], list) or not input_data['keywords']:
        raise ValueError('Keywords must be a non-empty list')
    
    if not isinstance(input_data['proxies'], list):
        raise ValueError('Proxies must be a list')
    
    valid_types = [t.value for t in SearchType]
    if input_data['type'] not in valid_types:
        raise ValueError(f'Invalid search type: {input_data["type"]}. Must be one of: {", ".join(valid_types)}')
    
    return True