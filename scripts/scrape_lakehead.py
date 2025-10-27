#!/usr/bin/env python3
"""Comprehensive web crawler for Lakehead University websites.
    
This script recursively crawls and scrapes all pages from Lakehead University
domains (lakeheadu.ca and csdc.lakeheadu.ca), discovering links and extracting
content-rich pages while filtering out low-value pages.
"""

import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class LakeheadScraper:
    """Scraper for Lakehead University website."""
    
    BASE_URL = "https://www.lakeheadu.ca"
    CATALOG_URL = "https://csdc.lakeheadu.ca"
    OUTPUT_DIR = Path(__file__).parent.parent / "data" / "lakehead_scraped"
    
    # Sitemap URLs to discover more pages
    SITEMAPS = [
        "https://www.lakeheadu.ca/sitemap.xml",
        "https://www.lakeheadu.ca/robots.txt",
        "https://csdc.lakeheadu.ca/sitemap.xml"
    ]
    
    # Sections to scrape - Comprehensive list of official Lakehead University websites
    SECTIONS = {
        # Main Website Pages
        "home": {
            "url": "https://www.lakeheadu.ca",
            "description": "Lakehead University homepage"
        },
        "about": {
            "url": "https://www.lakeheadu.ca/about",
            "description": "About Lakehead University"
        },
        
        # Future Students
        "future_students": {
            "url": "https://www.lakeheadu.ca/future-students",
            "description": "Information for prospective students"
        },
        "programs": {
            "url": "https://www.lakeheadu.ca/future-students/programs",
            "description": "Academic programs offered at Lakehead University"
        },
        "admissions": {
            "url": "https://www.lakeheadu.ca/future-students/admissions",
            "description": "Admissions information for prospective students"
        },
        "application_process": {
            "url": "https://www.lakeheadu.ca/future-students/how-to-apply",
            "description": "How to apply to Lakehead University"
        },
        "scholarships": {
            "url": "https://www.lakeheadu.ca/future-students/scholarships-and-awards",
            "description": "Scholarships and financial awards"
        },
        "international_students": {
            "url": "https://www.lakeheadu.ca/future-students/international",
            "description": "International student information"
        },
        "transfer_credits": {
            "url": "https://www.lakeheadu.ca/future-students/transfer-credits",
            "description": "Transfer credit information"
        },
        
        # Tuition and Fees
        "tuition_fees": {
            "url": "https://www.lakeheadu.ca/future-students/tuition-and-fees",
            "description": "Tuition and fees information"
        },
        
        # Academic Information
        "academics": {
            "url": "https://www.lakeheadu.ca/academics",
            "description": "Academic programs and departments"
        },
        "faculties": {
            "url": "https://www.lakeheadu.ca/faculties",
            "description": "Faculties and departments"
        },
        
        # Academic Calendar (CSDC)
        "academic_calendar": {
            "url": "https://csdc.lakeheadu.ca/Catalog/ViewCatalog.aspx",
            "description": "Official academic calendar and course catalog"
        },
        
        # Campuses
        "thunder_bay": {
            "url": "https://www.lakeheadu.ca/about/our-campus/thunder-bay",
            "description": "Thunder Bay campus information"
        },
        "orillia": {
            "url": "https://www.lakeheadu.ca/about/our-campus/orillia",
            "description": "Orillia campus information"
        },
        
        # Student Services
        "current_students": {
            "url": "https://www.lakeheadu.ca/student-central",
            "description": "Current student services and information"
        },
        "registration": {
            "url": "https://www.lakeheadu.ca/studentcentral/registration",
            "description": "Registration information for students"
        },
        "student_services": {
            "url": "https://www.lakeheadu.ca/student-life",
            "description": "Student services and support"
        },
        "library": {
            "url": "https://library.lakeheadu.ca",
            "description": "Lakehead University library"
        },
        
        # Financial Information
        "financial_aid": {
            "url": "https://www.lakeheadu.ca/studentcentral/fees-and-finances",
            "description": "Financial aid and payment information"
        },
        
        # Student Life
        "campus_life": {
            "url": "https://www.lakeheadu.ca/student-life/campus-life",
            "description": "Campus life and activities"
        },
        "housing": {
            "url": "https://www.lakeheadu.ca/student-life/housing",
            "description": "Housing and residence information"
        },
        "athletics": {
            "url": "https://www.lakeheadu.ca/student-life/athletics",
            "description": "Athletics and recreation"
        },
        
        # Research
        "research": {
            "url": "https://www.lakeheadu.ca/research",
            "description": "Research activities and opportunities"
        },
        "research_centers": {
            "url": "https://www.lakeheadu.ca/research/research-centres-and-institutes",
            "description": "Research centres and institutes"
        },
        
        # Alumni and Giving
        "alumni": {
            "url": "https://www.lakeheadu.ca/alumni",
            "description": "Alumni information and services"
        },
        "giving": {
            "url": "https://www.lakeheadu.ca/giving",
            "description": "Supporting Lakehead University"
        },
        
        # News and Events
        "news": {
            "url": "https://www.lakeheadu.ca/news",
            "description": "University news and announcements"
        },
        "events": {
            "url": "https://www.lakeheadu.ca/events",
            "description": "University events and activities"
        }
    }
    
    def __init__(self, delay: float = 1.0, resume: bool = False):
        """Initialize the scraper.
        
        Args:
            delay: Delay between requests in seconds (for rate limiting)
            resume: Whether to resume from previous crawl state
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Lakehead Chatbot Scraper 1.0'
        })
        
        # Create output directory
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Crawler state tracking
        self.visited_urls: Set[str] = set()
        self.discovered_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.content_hashes: Set[str] = set()
        self.url_queue = deque()
        self.statistics = {
            'pages_scraped': 0,
            'pages_skipped': 0,
            'pages_failed': 0,
            'links_discovered': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Load previous state if resuming
        if resume:
            self.load_crawler_state()
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for crawling.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL should be crawled
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Must be Lakehead domain
            if not (domain.endswith('lakeheadu.ca') or 'csdc.lakeheadu.ca' in domain):
                return False
            
            # Exclude file downloads
            exclude_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', 
                                '.rar', '.tar', '.gz', '.mp3', '.mp4', '.avi', 
                                '.jpg', '.jpeg', '.png', '.gif']
            if any(url.lower().endswith(ext) for ext in exclude_extensions):
                return False
            
            # Exclude mailto, tel, javascript links
            if any(url.startswith(prefix) for prefix in ['mailto:', 'tel:', 'javascript:', '#']):
                return False
            
            # Exclude login/logout pages
            if any(term in url.lower() for term in ['/login', '/logout', '/signin', '/signout']):
                return False
            
            return True
            
        except Exception:
            return False
    
    def calculate_content_quality(self, soup: BeautifulSoup) -> Dict:
        """Calculate quality metrics for page content.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with quality metrics
        """
        # Extract text
        text_content = soup.get_text()
        word_count = len(text_content.split())
        
        # Count headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        # Count links
        links = soup.find_all('a', href=True)
        
        # Calculate quality score
        quality_score = word_count * 0.5 + len(headings) * 10 + min(len(links), 50)
        
        return {
            'word_count': word_count,
            'heading_count': len(headings),
            'link_count': len(links),
            'quality_score': quality_score
        }
    
    def should_scrape_page(self, soup: BeautifulSoup, _url: str) -> bool:
        """Determine if page should be scraped based on content.
        
        Args:
            soup: BeautifulSoup object
            _url: URL of the page (unused but kept for signature)
            
        Returns:
            True if page should be scraped
        """
        quality = self.calculate_content_quality(soup)
        
        # Skip pages with too little content
        if quality['word_count'] < 50:
            return False
        
        # Skip if too many links relative to content (navigation page)
        if quality['link_count'] > 0 and quality['word_count'] / quality['link_count'] < 3:
            return False
        
        return True
    
    def is_duplicate_content(self, content_hash: str) -> bool:
        """Check if content is duplicate.
        
        Args:
            content_hash: Hash of content
            
        Returns:
            True if content is duplicate
        """
        if content_hash in self.content_hashes:
            return True
        
        self.content_hashes.add(content_hash)
        return False
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if request fails
        """
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def extract_content(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract main content from a webpage.
        
        Args:
            soup: BeautifulSoup object
            url: Source URL
            
        Returns:
            Dictionary with extracted content
        """
        content = {
            'url': url,
            'title': '',
            'main_content': '',
            'headings': [],
            'links': []
        }
        
        # Extract title
        if soup.title:
            content['title'] = soup.title.string.strip() if soup.title.string else ''
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if main_content:
            content['main_content'] = self.clean_text(main_content.get_text())
        
        # Extract headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            heading_text = self.clean_text(heading.get_text())
            if heading_text:
                content['headings'].append(heading_text)
        
        # Extract important links
        for link in soup.find_all('a', href=True):
            link_url = link.get('href', '')
            link_text = self.clean_text(link.get_text())
            if link_text and link_url.startswith('http'):
                content['links'].append({
                    'text': link_text,
                    'url': link_url
                })
        
        return content
    
    def discover_urls_from_sitemap(self, sitemap_url: str) -> List[str]:
        """Discover URLs from a sitemap.
        
        Args:
            sitemap_url: URL of the sitemap
            
        Returns:
            List of discovered URLs
        """
        discovered_urls = []
        
        try:
            print(f"Checking sitemap: {sitemap_url}")
            response = self.session.get(sitemap_url, timeout=10)
            response.raise_for_status()
            
            # Check if it's a robots.txt file
            if 'robots.txt' in sitemap_url:
                # Parse robots.txt to find sitemap references
                for line in response.text.split('\n'):
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        discovered_urls.extend(self.discover_urls_from_sitemap(sitemap_url))
            else:
                # Parse XML sitemap
                root = ET.fromstring(response.content)
                for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        discovered_urls.append(loc.text)
                        
        except Exception as e:
            print(f"Error parsing sitemap {sitemap_url}: {e}")
        
        return discovered_urls
    
    def discover_catalog_pages(self, base_url: str) -> List[dict]:
        """Discover all pages in the academic catalog.
        
        Args:
            base_url: Base URL of the catalog
            
        Returns:
            List of page configurations
        """
        pages = []
        
        try:
            soup = self.fetch_page(base_url)
            if not soup:
                return pages
            
            # Find all navigation links and important pages
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # Check if it's a catalog page
                if '/Catalog/' in href or 'ViewCatalog' in href:
                    url = urljoin(base_url, href)
                    
                    # Avoid duplicates
                    if url not in [p['url'] for p in pages] and text:
                        pages.append({
                            'url': url,
                            'description': f"Academic catalog page: {text}",
                            'title': text
                        })
                        
        except Exception as e:
            print(f"Error discovering catalog pages: {e}")
        
        return pages
    
    def scrape_section(self, section_name: str, section_config: dict) -> str:
        """Scrape a specific section of the website.
        
        Args:
            section_name: Name of the section
            section_config: Configuration for the section
            
        Returns:
            Path to the created markdown file
        """
        url = section_config['url']
        description = section_config['description']
        
        soup = self.fetch_page(url)
        if not soup:
            print(f"Failed to fetch {section_name}")
            return None
        
        # Wait between requests
        time.sleep(self.delay)
        
        # Extract content
        content = self.extract_content(soup, url)
        
        # Generate markdown
        markdown_content = self.generate_markdown(section_name, description, content)
        
        # Save to file
        output_file = self.OUTPUT_DIR / f"{section_name}.md"
        output_file.write_text(markdown_content, encoding='utf-8')
        
        print(f"✓ Saved: {output_file}")
        return str(output_file)
    
    def generate_markdown(self, section_name: str, description: str, content: dict) -> str:
        """Generate markdown content from scraped data.
        
        Args:
            section_name: Name of the section
            description: Description of the section
            content: Extracted content dictionary
            
        Returns:
            Markdown formatted string
        """
        md_lines = []
        
        # Header
        md_lines.append(f"# {content['title'] or section_name.replace('_', ' ').title()}")
        md_lines.append("")
        md_lines.append(f"**Source**: {content['url']}")
        md_lines.append(f"**Description**: {description}")
        md_lines.append(f"**Scraped**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # Headings
        if content['headings']:
            md_lines.append("## Table of Contents")
            md_lines.append("")
            for i, heading in enumerate(content['headings'][:50], 1):  # Limit to first 50
                clean_heading = heading.strip('#').strip()
                md_lines.append(f"{i}. {clean_heading}")
            md_lines.append("")
        
        # Main content
        if content['main_content']:
            # Limit content length (increased to capture more information)
            main_text = content['main_content'][:20000]  # First 20000 characters
            if len(content['main_content']) > 20000:
                main_text += "\n\n*(Content truncated for brevity)*"
            
            md_lines.append("## Content")
            md_lines.append("")
            md_lines.append(main_text)
            md_lines.append("")
        
        # Important links
        if content['links']:
            md_lines.append("## Related Links")
            md_lines.append("")
            for link in content['links'][:30]:  # Limit to first 30
                md_lines.append(f"- [{link['text']}]({link['url']})")
            md_lines.append("")
        
        return '\n'.join(md_lines)
    
    def scrape_all(self, discover_pages: bool = True) -> List[str]:
        """Scrape all configured sections.
        
        Args:
            discover_pages: Whether to discover additional pages from catalogs
        
        Returns:
            List of created file paths
        """
        print("Starting comprehensive scrape of Lakehead University website...")
        print(f"Output directory: {self.OUTPUT_DIR}")
        print(f"Total sections to scrape: {len(self.SECTIONS)}")
        print()
        
        created_files = []
        
        # First, scrape all configured sections
        total = len(self.SECTIONS)
        for idx, (section_name, section_config) in enumerate(self.SECTIONS.items(), 1):
            try:
                print(f"[{idx}/{total}] Scraping {section_name}...")
                file_path = self.scrape_section(section_name, section_config)
                if file_path:
                    created_files.append(file_path)
                time.sleep(self.delay)
            except Exception as e:
                print(f"Error scraping {section_name}: {e}")
        
        # Discover and scrape additional pages
        if discover_pages:
            print()
            print("Discovering additional pages...")
            
            # Discover catalog pages
            print("Scanning academic catalog...")
            catalog_pages = self.discover_catalog_pages(self.CATALOG_URL + "/Catalog/ViewCatalog.aspx")
            
            if catalog_pages:
                print(f"Found {len(catalog_pages)} catalog pages to scrape")
                for page_config in catalog_pages[:20]:  # Limit to first 20 to avoid overwhelming
                    try:
                        page_name = page_config.get('title', 'catalog_page').lower().replace(' ', '_')
                        section_config = {
                            'url': page_config['url'],
                            'description': page_config['description']
                        }
                        file_path = self.scrape_section(f"catalog_{page_name}", section_config)
                        if file_path:
                            created_files.append(file_path)
                        time.sleep(self.delay)
                    except Exception as e:
                        print(f"Error scraping catalog page: {e}")
        
        return created_files
    
    def discover_links_from_page(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Discover all links from a page.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of discovered and valid URLs
        """
        discovered = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if not href:
                continue
            
            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)
            
            # Validate URL
            if self.is_valid_url(absolute_url) and absolute_url not in self.visited_urls:
                discovered.append(absolute_url)
                self.statistics['links_discovered'] += 1
        
        return discovered
    
    def save_crawler_state(self):
        """Save crawler state to disk."""
        state = {
            'visited_urls': list(self.visited_urls),
            'failed_urls': list(self.failed_urls),
            'content_hashes': list(self.content_hashes),
            'statistics': self.statistics,
            'save_time': datetime.now().isoformat()
        }
        
        state_file = self.OUTPUT_DIR / 'crawler_state.json'
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        
        print(f"Crawler state saved to {state_file}")
    
    def load_crawler_state(self):
        """Load crawler state from disk."""
        state_file = self.OUTPUT_DIR / 'crawler_state.json'
        
        if not state_file.exists():
            return
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.visited_urls = set(state.get('visited_urls', []))
            self.failed_urls = set(state.get('failed_urls', []))
            self.content_hashes = set(state.get('content_hashes', []))
            self.statistics = state.get('statistics', self.statistics)
            
            print(f"Loaded crawler state: {len(self.visited_urls)} pages already crawled")
        except Exception as e:
            print(f"Error loading crawler state: {e}")
    
    def generate_filename_from_url(self, url: str) -> str:
        """Generate a safe filename from URL.
        
        Args:
            url: URL to convert
            
        Returns:
            Safe filename
        """
        # Remove protocol and domain
        path = urlparse(url).path
        
        # Replace slashes and special characters
        filename = re.sub(r'[^\w\-_.]', '_', path)
        filename = filename.strip('_')
        
        # Handle empty filename
        if not filename:
            filename = 'index'
        
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename
    
    def scrape_page_recursive(self, url: str) -> Optional[str]:
        """Scrape a single page and discover links (recursive).
        
        Args:
            url: URL to scrape
            
        Returns:
            Path to saved file if successful, None otherwise
        """
        # Check if already visited
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        
        # Fetch page
        soup = self.fetch_page(url)
        if not soup:
            self.failed_urls.add(url)
            self.statistics['pages_failed'] += 1
            return None
        
        time.sleep(self.delay)
        
        # Check content quality
        if not self.should_scrape_page(soup, url):
            self.statistics['pages_skipped'] += 1
            return None
        
        # Check for duplicate content
        content_hash = hashlib.md5(str(soup).encode()).hexdigest()
        if self.is_duplicate_content(content_hash):
            self.statistics['pages_skipped'] += 1
            return None
        
        # Extract and save content
        description = "Discovered from Lakehead University website"
        section_name = self.generate_filename_from_url(url)
        
        content = self.extract_content(soup, url)
        markdown_content = self.generate_markdown(section_name, description, content)
        
        output_file = self.OUTPUT_DIR / f"{section_name}.md"
        output_file.write_text(markdown_content, encoding='utf-8')
        
        self.statistics['pages_scraped'] += 1
        print(f"✓ [{self.statistics['pages_scraped']}] Saved: {output_file}")
        
        # Discover links
        new_links = self.discover_links_from_page(soup, url)
        for link in new_links:
            if link not in self.visited_urls and link not in self.failed_urls:
                self.url_queue.append(link)
        
        return str(output_file)
    
    def crawl_comprehensive(self, seed_urls: List[str], max_pages: Optional[int] = None) -> List[str]:
        """Perform comprehensive recursive crawl.
        
        Args:
            seed_urls: Starting URLs for crawling
            max_pages: Maximum number of pages to crawl (None for unlimited)
            
        Returns:
            List of created file paths
        """
        self.statistics['start_time'] = datetime.now().isoformat()
        
        # Add seed URLs to queue
        for url in seed_urls:
            if self.is_valid_url(url):
                self.url_queue.append(url)
        
        created_files = []
        
        print("Starting comprehensive crawl of Lakehead University websites...")
        print(f"Seed URLs: {len(seed_urls)}")
        print(f"Max pages: {max_pages or 'unlimited'}")
        print()
        
        # Process queue
        while self.url_queue:
            if max_pages and self.statistics['pages_scraped'] >= max_pages:
                print(f"\nReached maximum page limit ({max_pages})")
                break
            
            url = self.url_queue.popleft()
            
            try:
                file_path = self.scrape_page_recursive(url)
                if file_path:
                    created_files.append(file_path)
                
                # Save state periodically
                if self.statistics['pages_scraped'] % 10 == 0:
                    self.save_crawler_state()
                    print(f"Progress: {self.statistics['pages_scraped']} pages scraped, "
                          f"{len(self.url_queue)} in queue, "
                          f"{self.statistics['pages_skipped']} skipped")
            
            except Exception as e:
                print(f"Error processing {url}: {e}")
                self.failed_urls.add(url)
                self.statistics['pages_failed'] += 1
        
        self.statistics['end_time'] = datetime.now().isoformat()
        self.save_crawler_state()
        
        return created_files


def main():
    """Main entry point for the comprehensive crawler."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Crawl Lakehead University websites comprehensively')
    parser.add_argument('--max-pages', type=int, help='Maximum number of pages to crawl')
    parser.add_argument('--resume', action='store_true', help='Resume from previous crawl state')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    args = parser.parse_args()
    
    print("=" * 80)
    print("Lakehead University Comprehensive Website Crawler")
    print("=" * 80)
    print()
    
    scraper = LakeheadScraper(delay=args.delay, resume=args.resume)
    
    # Seed URLs for comprehensive crawling
    seed_urls = [
        "https://www.lakeheadu.ca",
        "https://csdc.lakeheadu.ca/Catalog/ViewCatalog.aspx"
    ]
    
    # Perform comprehensive crawl
    created_files = scraper.crawl_comprehensive(seed_urls, max_pages=args.max_pages)
    
    print()
    print("=" * 80)
    print("Crawling Complete!")
    print("=" * 80)
    print()
    print("Statistics:")
    print(f"  - Pages scraped: {scraper.statistics['pages_scraped']}")
    print(f"  - Pages skipped: {scraper.statistics['pages_skipped']}")
    print(f"  - Pages failed: {scraper.statistics['pages_failed']}")
    print(f"  - Links discovered: {scraper.statistics['links_discovered']}")
    print(f"  - Files created: {len(created_files)}")
    print()
    print(f"Output directory: {scraper.OUTPUT_DIR}")
    print()


if __name__ == "__main__":
    main()
