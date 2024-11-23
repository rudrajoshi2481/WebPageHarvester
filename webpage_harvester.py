#!/usr/bin/env python3

import os
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date
from typing_extensions import TypedDict

class PageMetadata(TypedDict):
    original_url: str
    local_path: str
    downloaded_at: str
    status_code: int
    content_type: str

class WebPageHarvester:
    """A comprehensive web scraping tool that preserves directory structure."""
    
    DEFAULT_USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]

    def __init__(
        self,
        base_url: str,
        output_dir: str = "downloaded_pages",
        delay: float = 1.0,
        preserve_structure: bool = True,
        user_agents: Optional[List[str]] = None
    ):
        """Initialize the WebPageHarvester.

        Args:
            base_url: The starting URL to begin scraping
            output_dir: Directory to store scraped content
            delay: Time delay between requests in seconds
            preserve_structure: Whether to maintain original URL directory structure
            user_agents: List of user agents to rotate through
        """
        self.base_url = base_url.rstrip('/')
        self.base_domain = urlparse(self.base_url).netloc
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.preserve_structure = preserve_structure
        self.user_agents = user_agents or self.DEFAULT_USER_AGENTS
        
        self.visited_urls: Set[str] = set()
        self.failed_urls: Dict[str, str] = {}
        self.metadata: Dict[str, PageMetadata] = {}
        
        # Create output directory and setup logging
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging to both file and console."""
        log_file = self.output_dir / 'scraper.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def _get_headers(self) -> Dict[str, str]:
        """Generate request headers with a random user agent."""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def _get_local_path(self, url: str) -> Path:
        """Generate a local file path for a given URL while preserving structure."""
        parsed = urlparse(url)
        if self.preserve_structure:
            # Remove base URL path from the URL path to get relative path
            base_path = urlparse(self.base_url).path
            relative_path = parsed.path[len(base_path):] if parsed.path.startswith(base_path) else parsed.path
            
            # Create path that mirrors URL structure
            path_parts = relative_path.strip('/').split('/')
            if not path_parts[-1]:  # URL ends with /
                path_parts.append('index.html')
            elif '.' not in path_parts[-1]:  # URL doesn't end with file extension
                path_parts[-1] += '.html'
                
            return self.output_dir.joinpath(*path_parts)
        else:
            # Simple hash-based approach for flat structure
            filename = f"{hash(url)}.html"
            return self.output_dir / filename

    def _save_metadata(self) -> None:
        """Save metadata about downloaded pages to a JSON file."""
        metadata_file = self.output_dir / 'metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)

    def _download_page(self, url: str) -> Tuple[Optional[str], Optional[requests.Response]]:
        """Download a single page and return its content and response object."""
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return response.text, response
        except Exception as e:
            logging.error(f"Failed to download {url}: {str(e)}")
            self.failed_urls[url] = str(e)
            return None, None

    def _extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all valid internal links from the page."""
        links = []
        for tag, attr in [('a', 'href'), ('link', 'href')]:
            for element in soup.find_all(tag):
                if attr in element.attrs:
                    url = element[attr]
                    absolute_url = urljoin(current_url, url)
                    parsed = urlparse(absolute_url)
                    
                    # Only include internal links with http(s) scheme
                    if (parsed.netloc == self.base_domain and 
                        parsed.scheme in ('http', 'https') and
                        '#' not in url):  # Exclude anchor links
                        links.append(absolute_url)
        return links

    def _process_page(self, url: str) -> None:
        """Process a single page: download and save."""
        if url in self.visited_urls:
            return

        self.visited_urls.add(url)
        logging.info(f"Processing: {url}")
        
        # Download the page
        content, response = self._download_page(url)
        if not content or not response:
            return

        # Parse the content
        soup = BeautifulSoup(content, 'lxml')
        
        # Get the local path for this URL
        local_path = self._get_local_path(url)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Store metadata
        self.metadata[url] = {
            'original_url': url,
            'local_path': str(local_path),
            'downloaded_at': datetime.now().isoformat(),
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type', '')
        }
        
        # Save the content
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        # Process delay
        time.sleep(self.delay)
        
        # Recursively process all internal links
        for link in self._extract_links(soup, url):
            if link not in self.visited_urls:
                self._process_page(link)

    def start_scraping(self) -> None:
        """Start the scraping process from the base URL."""
        try:
            logging.info(f"Starting scraping from: {self.base_url}")
            self._process_page(self.base_url)
            
            # Save metadata
            self._save_metadata()
            
            # Log summary
            logging.info(f"Scraping completed. Downloaded {len(self.visited_urls)} pages.")
            if self.failed_urls:
                logging.warning(f"Failed to download {len(self.failed_urls)} pages.")
                for url, error in self.failed_urls.items():
                    logging.warning(f"  {url}: {error}")
                    
        except Exception as e:
            logging.error(f"Scraping failed: {str(e)}")
            raise

if __name__ == '__main__':
    # Example usage
    scraper = WebPageHarvester(
        base_url="https://example.com/blog/",
        output_dir="downloaded_pages",
        delay=1.0,
        preserve_structure=True
    )
    scraper.start_scraping()
