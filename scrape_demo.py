#!/usr/bin/env python3

from webpage_harvester import WebPageHarvester

def main():
    # Initialize the scraper with quotes.toscrape.com
    scraper = WebPageHarvester(
        base_url="http://quotes.toscrape.com",
        output_dir="downloaded_quotes",
        delay=1.0,  # 1 second delay between requests
        preserve_structure=True
    )
    
    # Start scraping
    scraper.start_scraping()

if __name__ == "__main__":
    main()
