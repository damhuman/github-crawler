import unittest
from src.validators import validate_input_data
from src.enums import SearchType

class TestValidators(unittest.TestCase):
    def test_validate_input_data_success(self):
        """Test successful validation"""
        input_data = {
            'keywords': ['python', 'web scraping'],
            'proxies': ['http://proxy1.com', 'http://proxy2.com'],
            'type': 'repositories'
        }
        
        # Validate the input data
        result = validate_input_data(input_data)
        
        # Verify the result
        self.assertTrue(result)
    
    def test_validate_input_data_missing_fields(self):
        """Test validation with missing fields"""
        input_data = {
            'keywords': ['python', 'web scraping'],
            'proxies': ['http://proxy1.com']
            # Missing 'type'
        }
        
        # Validate the input data
        with self.assertRaises(ValueError) as context:
            validate_input_data(input_data)
        
        self.assertIn('Missing required field(s): type', str(context.exception))
    
    def test_validate_input_data_invalid_keywords(self):
        """Test validation with invalid keywords"""
        input_data = {
            'keywords': [],  # Empty list
            'proxies': ['http://proxy1.com'],
            'type': 'repositories'
        }
        
        # Validate the input data
        with self.assertRaises(ValueError) as context:
            validate_input_data(input_data)
        
        self.assertIn('Keywords must be a non-empty list', str(context.exception))
    
    def test_validate_input_data_invalid_proxies(self):
        """Test validation with invalid proxies"""
        input_data = {
            'keywords': ['python', 'web scraping'],
            'proxies': 'http://proxy1.com',  # Not a list
            'type': 'repositories'
        }
        
        # Validate the input data
        with self.assertRaises(ValueError) as context:
            validate_input_data(input_data)
        
        self.assertIn('Proxies must be a list', str(context.exception))
    
    def test_validate_input_data_invalid_type(self):
        """Test validation with invalid search type"""
        input_data = {
            'keywords': ['python', 'web scraping'],
            'proxies': ['http://proxy1.com'],
            'type': 'invalid_type'  # Invalid type
        }
        
        # Validate the input data
        with self.assertRaises(ValueError) as context:
            validate_input_data(input_data)
        
        valid_types = [t.value for t in SearchType]
        self.assertIn(f'Invalid search type: invalid_type. Must be one of: {", ".join(valid_types)}', str(context.exception)) 