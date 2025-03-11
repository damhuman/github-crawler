# GitHub Crawler

Tool for crawling GitHub repositories, issues, and discussions based on keywords.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/damhuman/github-crawler.git
   cd github-crawler
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the crawler with an input JSON file:

```bash
python main.py data/input.json
```

### Options

The crawler supports the following options:

- `--output_file`: Specify the output file path (default: "data/results.json")
- `--extra_info`: Include extra information in the output (default: False)

```bash
python main.py data/input.json --output_file data/results.json --extra_info
```

Example input JSON file:

```json
{
  "keywords": ["python", "data science"],
  "proxies": ["127.0.0.1:8080"],
  "type": "repositories"
}
```

### Output

The crawler will save the results in the specified output file. The output format is as follows:

```json
{
  "keywords": ["python", "data science"],
  "search_type": "repositories",
  "results": [
    {
      "url": "https://github.com/user/repo",
      "extra": {
        "owner": "user",
        "language_stats": {
          "Python": 50,
          "JavaScript": 30,
          "HTML": 20
        }
      }
    }
  ]
}
```

## Testing

To run the tests:

```bash
coverage coverage run -m unittest discover tests
coverage report -m
```

## Coverage

To view the coverage report:

```bash
coverage html
```
