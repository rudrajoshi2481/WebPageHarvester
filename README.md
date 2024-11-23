# WebPageHarvester

A robust and polite web scraping tool designed to recursively download all pages under a specified URL path. Built with Python, this tool maintains the original directory structure and updates internal links to work locally, allowing you to browse the downloaded content just like the original website.

## Features

- 🌐 Recursive webpage crawling
- 📁 Preserves original directory structure
- 🔗 Updates internal links to work locally
- 📊 Detailed metadata tracking
- 🔄 Duplicate prevention
- ⚡ Efficient error handling
- 🤝 Respectful scraping with rate limiting
- 🔍 URL validation and sanitization
- 📝 Comprehensive logging
- 📑 Creates an index page for easy navigation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rudrajoshi2481/WebPageHarvester
cd WebPageHarvester
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Basic usage with directory structure preservation:
```python
from webpage_harvester import WebPageHarvester

# Initialize the scraper with structure preservation
scraper = WebPageHarvester(
    base_url="https://example.com/blog/",
    preserve_structure=True  # This will maintain the original URL structure
)

# Start scraping
scraper.start_scraping()
```

2. Custom configuration:
```python
scraper = WebPageHarvester(
    base_url="https://example.com/blog/",
    output_dir="custom_output",
    delay=2.0,  # Custom delay between requests in seconds
    preserve_structure=True
)
```

## Output Structure

The scraper creates an organized output directory that mirrors the original website structure:

```
downloaded_pages/
├── index.html              # Main index page with links to all downloaded content
├── blog/
│   ├── index.html         # Main blog page
│   ├── post1/
│   │   └── index.html     # First blog post
│   └── post2/
│       └── index.html     # Second blog post
├── metadata.json          # Detailed information about downloaded pages
└── scraper.log           # Logging information
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| base_url | Required | The starting URL to begin scraping |
| output_dir | "downloaded_pages" | Directory to store scraped content |
| delay | 1.0 | Time delay between requests (seconds) |
| preserve_structure | True | Maintain original URL directory structure |
| user_agents | [list of agents] | List of user agents to rotate through |

## Features in Detail

### Directory Structure Preservation
- Maintains the same directory structure as the original website
- Creates appropriate subdirectories for nested content
- Generates index.html files for directory listings

### Link Updates
- Updates all internal links to work with the local file structure
- Handles relative and absolute URLs
- Updates links in:
  - Anchor tags (<a href="">)
  - Stylesheets (<link href="">)
  - Scripts (<script src="">)
  - Images (<img src="">)

### Navigation
- Creates an index.html file listing all downloaded pages
- Preserves the original website's navigation structure
- Allows browsing the downloaded content like the original site

## Best Practices

1. Always check the website's robots.txt file before scraping
2. Set appropriate delays between requests
3. Include proper user agent identification
4. Handle rate limiting and errors gracefully
5. Respect the website's terms of service

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Beautiful Soup documentation
- Python Requests library
- Web scraping best practices community

## Disclaimer

This tool is for educational purposes only. Always ensure you have permission to scrape websites and comply with their terms of service and robots.txt directives.
