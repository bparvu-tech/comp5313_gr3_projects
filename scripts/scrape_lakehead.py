#!/usr/bin/env python3
"""Comprehensive recursive web scraper for ALL Lakehead University pages.

This scraper recursively crawls and discovers all pages across Lakehead University
domains, with improved FAQ extraction and comprehensive content capture.
"""

import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from heapq import heappush, heappop
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


class ComprehensiveLakeheadScraper:
    """Comprehensive scraper with recursive crawling and improved FAQ extraction."""

    BASE_URL = "https://www.lakeheadu.ca"
    CATALOG_URL = "https://csdc.lakeheadu.ca"
    LUSU_URL = "https://lusu.ca"
    OUTPUT_DIR = Path(__file__).parent.parent / "data" / "lakehead_scraped"

    # Sitemaps for URL discovery
    SITEMAPS = [
        "https://www.lakeheadu.ca/sitemap.xml",
        "https://www.lakeheadu.ca/robots.txt",
        "https://csdc.lakeheadu.ca/sitemap.xml",
        "https://lusu.ca/sitemap.xml",
    ]

    # Seed URLs to start crawling
    SEED_URLS = [
        "https://www.lakeheadu.ca",
        "https://www.lakeheadu.ca/programs",
        "https://www.lakeheadu.ca/programs/departments/computer-science",
        "https://www.lakeheadu.ca/future-students",
        "https://www.lakeheadu.ca/student-life",
        "https://www.lakeheadu.ca/studentcentral",
        "https://csdc.lakeheadu.ca/Catalog/ViewCatalog.aspx",
        "https://lusu.ca",
    ]

    def __init__(self, delay: float = 1.0, resume: bool = False):
        """Initialize the comprehensive scraper.

        Args:
            delay: Delay between requests in seconds
            resume: Whether to resume from previous crawl state
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })

        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Crawler state
        self.visited_urls: Set[str] = set()
        self.discovered_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.content_hashes: Set[str] = set()
        self.url_queue = []  # Priority queue: (priority, url)

        self.statistics = {
            'pages_scraped': 0,
            'pages_skipped': 0,
            'pages_failed': 0,
            'faq_items_found': 0,
            'links_discovered': 0,
            'start_time': None,
            'end_time': None,
            'by_priority': {1: 0, 2: 0, 3: 0}
        }

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

            # Must be Lakehead or LUSU domain
            if not (domain.endswith('lakeheadu.ca') or domain == 'lusu.ca' or
                   domain.endswith('.lusu.ca')):
                return False

            # Exclude file downloads
            exclude_ext = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip',
                                '.rar', '.tar', '.gz', '.mp3', '.mp4', '.avi',
                          '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico']
            if any(url.lower().endswith(ext) for ext in exclude_ext):
                return False

            # Exclude special links
            if any(url.startswith(prefix) for prefix in
                  ['mailto:', 'tel:', 'javascript:', '#', 'data:']):
                return False

            # Exclude login/admin pages
            if any(term in url.lower() for term in
                  ['/login', '/logout', '/signin', '/signout', '/admin', '/user/password']):
                return False

            return True

        except Exception:
            return False

    def prioritize_url(self, url: str) -> int:
        """Assign priority to URL (lower = higher priority).

        Args:
            url: URL to prioritize

        Returns:
            Priority level (1 = highest, 3 = lowest)
        """
        url_lower = url.lower()

        # Tier 1: High-value content
        if any(term in url_lower for term in
              ['/faq', '/frequently-asked', 'important-dates', 'calendar']):
            return 1
        if '/programs/' in url_lower or '/departments/' in url_lower:
            return 1
        if any(term in url_lower for term in
              ['admissions', 'tuition', 'fees', 'scholarships']):
            return 1
        if any(term in url_lower for term in
              ['housing', 'residence', 'dining', 'meal']):
            return 1
        if 'lusu.ca' in url_lower:
            return 1

        # Tier 2: Medium-value content
        if any(term in url_lower for term in
              ['student', 'service', 'career', 'health', 'wellness']):
            return 2
        if '/Catalog/' in url_lower:
            return 2
        if any(term in url_lower for term in
              ['accessibility', 'international', 'policy', 'polic']):
            return 2

        # Tier 3: General content
        return 3

    def clean_text(self, text: str) -> str:
        """Clean and normalize text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines).strip()

    def extract_faq_content(self, soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """Extract FAQ questions and answers.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of (question, answer) tuples
        """
        faq_items = []

        # Find main content area
        main_container = (
            soup.find('div', class_=re.compile(r'field-name-body', re.I)) or
            soup.find('article') or
            soup.find('div', class_=re.compile(r'l-main|main-content', re.I)) or
            soup.find('main') or
            soup.find('div', {'role': 'main'}) or
            soup.find('body')
        )

        if not main_container:
            return faq_items

        # Remove navigation, sidebars, footers
        for unwanted in main_container.find_all(['nav', 'aside', 'footer', 'header']):
            unwanted.decompose()
        for unwanted in main_container.find_all('div',
                class_=re.compile(r'sidebar|navigation|menu|footer', re.I)):
            unwanted.decompose()

        # Strategy 1: <p><strong>Number. Question</strong></p> pattern
        paragraphs = main_container.find_all('p')

        for p in paragraphs:
            strong = p.find('strong')
            if strong:
                strong_text = self.clean_text(strong.get_text())
                match = re.match(r'^(\d+)\.\s+(.+)$', strong_text)

                if match:
                    question_text = match.group(2)
                    answer_parts = []
                    current = p.find_next_sibling()

                    # Collect answer until next question
                    while current:
                        if current.name == 'p':
                            next_strong = current.find('strong')
                            if next_strong:
                                next_text = self.clean_text(next_strong.get_text())
                                if re.match(r'^\d+\.\s+', next_text):
                                    break

                            text = self.clean_text(current.get_text())
                            if text and len(text) > 5:
                                answer_parts.append(text)

                        elif current.name in ['ul', 'ol']:
                            items = current.find_all('li', recursive=False)
                            for item in items:
                                item_text = self.clean_text(item.get_text())
                                if item_text:
                                    answer_parts.append(f"• {item_text}")

                        elif current.name in ['div', 'section']:
                            div_strong = current.find('strong')
                            if div_strong and re.match(r'^\d+\.\s+',
                                    self.clean_text(div_strong.get_text())):
                                break

                            text = self.clean_text(current.get_text())
                            if text and len(text) > 10:
                                answer_parts.append(text)

                        current = current.find_next_sibling()

                    if answer_parts:
                        answer = '\n\n'.join(answer_parts)
                        if len(answer) > 20:
                            faq_items.append((question_text, answer))

        # Strategy 2: Heading-based FAQs
        if not faq_items:
            headings = main_container.find_all(['h2', 'h3', 'h4'])
            for heading in headings:
                h_text = self.clean_text(heading.get_text())

                if not h_text or len(h_text) < 5:
                    continue
                if any(skip in h_text.lower() for skip in
                      ['contact', 'navigation', 'menu', 'search', 'hours:', 'address:']):
                    continue

                content_parts = []
                for sibling in heading.find_next_siblings():
                    if sibling.name in ['h1', 'h2', 'h3']:
                        break

                    text = self.clean_text(sibling.get_text())
                    if text and len(text) > 10:
                        if sibling.name in ['ul', 'ol']:
                            items = sibling.find_all('li')
                            for item in items:
                                item_text = self.clean_text(item.get_text())
                                if item_text:
                                    content_parts.append(f"• {item_text}")
                        else:
                            content_parts.append(text)

                if content_parts:
                    answer = '\n\n'.join(content_parts)
                    if len(answer) > 50:
                        faq_items.append((h_text, answer))

        return faq_items

    def extract_structured_content(self, soup: BeautifulSoup) -> Dict:
        """Extract comprehensive structured content.

        Args:
            soup: BeautifulSoup object

        Returns:
            Dictionary with structured content
        """
        content = {
            'sections': [],
            'lists': [],
            'tables': [],
            'links': [],
            'contact_info': {}
        }

        main = (
            soup.find('div', class_=re.compile(r'field-name-body', re.I)) or
            soup.find('main') or
            soup.find('article') or
            soup.find('div', {'role': 'main'}) or
            soup.find('div', class_=re.compile(r'main|content', re.I))
        )

        if not main:
            return content

        # Remove unwanted elements
        for unwanted in main.find_all(['script', 'style', 'nav', 'footer']):
            unwanted.decompose()

        # Extract sections with headings
        for heading in main.find_all(['h1', 'h2', 'h3', 'h4']):
            h_text = self.clean_text(heading.get_text())
            if not h_text or len(h_text) < 3:
                continue

            section_content = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h1', 'h2', 'h3', 'h4']:
                    break
                text = self.clean_text(sibling.get_text())
                if text and len(text) > 10:
                    section_content.append(text)

            if section_content:
                content['sections'].append({
                    'heading': h_text,
                    'level': heading.name,
                    'content': '\n\n'.join(section_content)
                })

        # Extract lists
        for ul in main.find_all(['ul', 'ol']):
            items = []
            for li in ul.find_all('li', recursive=False):
                text = self.clean_text(li.get_text())
                if text:
                    items.append(text)
            if items and len(items) >= 2:
                content['lists'].append({'type': ul.name, 'items': items})

        # Extract tables
        for table in main.find_all('table'):
            table_data = {'headers': [], 'rows': []}

            headers = table.find_all('th')
            if headers:
                table_data['headers'] = [self.clean_text(h.get_text()) for h in headers]

            for row in table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_data = [self.clean_text(cell.get_text()) for cell in cells]
                    if any(row_data):
                        table_data['rows'].append(row_data)

            if table_data['rows']:
                content['tables'].append(table_data)

        # Extract links
        for link in main.find_all('a', href=True):
            href = link.get('href')
            text = self.clean_text(link.get_text())
            if text and href and not href.startswith('#'):
                absolute_url = urljoin(self.BASE_URL, href)
                if len(content['links']) < 50:
                    content['links'].append({'text': text, 'url': absolute_url})

        # Extract contact information
        text_content = main.get_text()

        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                           text_content)
        if emails:
            content['contact_info']['emails'] = list(set(emails))[:5]

        phones = re.findall(r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',
                           text_content)
        if phones:
            content['contact_info']['phones'] = [
                f"({p[0]}) {p[1]}-{p[2]}" for p in phones[:5]
            ]

        return content

    def generate_markdown(self, url: str, title: str, faq_items: List[Tuple[str, str]],
                         content: Dict) -> str:
        """Generate comprehensive markdown.

        Args:
            url: Source URL
            title: Page title
            faq_items: List of (question, answer) tuples
            content: Structured content dictionary

        Returns:
            Markdown string
        """
        md_lines = []

        # Header
        md_lines.append(f"# {title}")
        md_lines.append("")
        md_lines.append(f"**URL:** {url}")
        md_lines.append(f"**Scraped:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

        # FAQ section
        if faq_items:
            md_lines.append("## Frequently Asked Questions")
            md_lines.append("")
            for i, (question, answer) in enumerate(faq_items, 1):
                md_lines.append(f"### {i}. {question}")
                md_lines.append("")
                md_lines.append(answer)
                md_lines.append("")

        # Content sections
        if content.get('sections'):
            if faq_items:
                md_lines.append("## Additional Content")
            else:
                md_lines.append("## Content")
            md_lines.append("")

            for section in content['sections'][:30]:
                level = int(section['level'][1])
                prefix = '#' * (level + 1)
                md_lines.append(f"{prefix} {section['heading']}")
                md_lines.append("")
                md_lines.append(section['content'][:2000])
                md_lines.append("")

        # Lists
        if content.get('lists'):
            md_lines.append("## Key Information")
            md_lines.append("")
            for list_data in content['lists'][:10]:
                for item in list_data['items'][:20]:
                    md_lines.append(f"- {item}")
                md_lines.append("")

        # Tables
        if content.get('tables'):
            md_lines.append("## Tables")
            md_lines.append("")
            for table in content['tables'][:5]:
                if table['headers']:
                    md_lines.append("| " + " | ".join(table['headers']) + " |")
                    md_lines.append("| " + " | ".join(['---'] * len(table['headers'])) + " |")

                for row in table['rows'][:20]:
                    md_lines.append("| " + " | ".join(row) + " |")
                md_lines.append("")

        # Contact info
        if content.get('contact_info'):
            contact = content['contact_info']
            if contact.get('phones') or contact.get('emails'):
                md_lines.append("## Contact Information")
                md_lines.append("")

                if contact.get('phones'):
                    md_lines.append("**Phone:**")
                    for phone in contact['phones']:
                        md_lines.append(f"- {phone}")
                    md_lines.append("")

                if contact.get('emails'):
                    md_lines.append("**Email:**")
                    for email in contact['emails']:
                        md_lines.append(f"- {email}")
                    md_lines.append("")

        # Related links
        if content.get('links'):
            md_lines.append("## Related Links")
            md_lines.append("")
            for link in content['links'][:30]:
                md_lines.append(f"- [{link['text']}]({link['url']})")
            md_lines.append("")

        return '\n'.join(md_lines)

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage.

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None
        """
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def discover_links_from_page(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Discover all valid links from a page.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links

        Returns:
            List of discovered URLs
        """
        discovered = []

        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if not href:
                continue

            absolute_url = urljoin(base_url, href)

            if (self.is_valid_url(absolute_url) and
                absolute_url not in self.visited_urls and
                absolute_url not in self.discovered_urls):
                discovered.append(absolute_url)
                self.statistics['links_discovered'] += 1

        return discovered

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

            if 'robots.txt' in sitemap_url:
                for line in response.text.split('\n'):
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        discovered_urls.extend(self.discover_urls_from_sitemap(sitemap_url))
            else:
                root = ET.fromstring(response.content)
                for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and self.is_valid_url(loc.text):
                        discovered_urls.append(loc.text)

        except Exception as e:
            print(f"Error parsing sitemap {sitemap_url}: {e}")

        return discovered_urls

    def is_duplicate_content(self, content_hash: str) -> bool:
        """Check if content is duplicate.

        Args:
            content_hash: Hash of content

        Returns:
            True if duplicate
        """
        if content_hash in self.content_hashes:
            return True
        self.content_hashes.add(content_hash)
        return False

    def should_scrape_page(self, soup: BeautifulSoup) -> bool:
        """Determine if page should be scraped.

        Args:
            soup: BeautifulSoup object

        Returns:
            True if page should be scraped
        """
        text = soup.get_text()
        word_count = len(text.split())

        if word_count < 50:
            return False

        # Check for actual content
        main = soup.find(['main', 'article']) or soup.find('div',
                class_=re.compile(r'content|main', re.I))
        if main:
            main_text = main.get_text()
            if len(main_text.split()) < 30:
                return False

        return True

    def generate_filename(self, url: str) -> str:
        """Generate safe filename from URL.

        Args:
            url: URL

        Returns:
            Filename
        """
        parsed = urlparse(url)
        path = parsed.path.strip('/')

        filename = re.sub(r'[^\w\-/]', '_', path)
        filename = filename.replace('/', '_')

        if not filename:
            filename = 'index'

        if len(filename) > 100:
            filename = filename[:100]

        return f"{filename}.md"

    def scrape_page(self, url: str) -> Optional[str]:
        """Scrape a single page.

        Args:
            url: URL to scrape

        Returns:
            Path to saved file or None
        """
        if url in self.visited_urls:
            return None

        self.visited_urls.add(url)

        soup = self.fetch_page(url)
        if not soup:
            self.failed_urls.add(url)
            self.statistics['pages_failed'] += 1
            return None

        time.sleep(self.delay)

        # Check quality
        if not self.should_scrape_page(soup):
            self.statistics['pages_skipped'] += 1
            return None

        # Check for duplicates
        content_hash = hashlib.md5(str(soup).encode()).hexdigest()
        if self.is_duplicate_content(content_hash):
            self.statistics['pages_skipped'] += 1
            return None

        # Extract title
        title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled"

        # Extract content
        faq_items = self.extract_faq_content(soup)
        if faq_items:
            self.statistics['faq_items_found'] += len(faq_items)

        content = self.extract_structured_content(soup)

        # Generate markdown
        markdown = self.generate_markdown(url, title, faq_items, content)

        # Save
        filename = self.generate_filename(url)
        output_path = self.OUTPUT_DIR / filename
        output_path.write_text(markdown, encoding='utf-8')

        self.statistics['pages_scraped'] += 1
        print(f"✓ [{self.statistics['pages_scraped']}] {filename}")

        # Discover new links
        new_links = self.discover_links_from_page(soup, url)
        for link in new_links:
            if link not in self.visited_urls and link not in self.failed_urls:
                priority = self.prioritize_url(link)
                heappush(self.url_queue, (priority, link))
                self.discovered_urls.add(link)

        return str(output_path)

    def save_crawler_state(self):
        """Save crawler state to JSON."""
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

            print(f"Loaded state: {len(self.visited_urls)} pages already crawled")
        except Exception as e:
            print(f"Error loading state: {e}")

    def crawl_comprehensive(self, max_pages: Optional[int] = None) -> List[str]:
        """Perform comprehensive recursive crawl of ALL Lakehead pages.

        Args:
            max_pages: Maximum number of pages to crawl (None for unlimited)

        Returns:
            List of created file paths
        """
        self.statistics['start_time'] = datetime.now().isoformat()

        print("=" * 80)
        print("COMPREHENSIVE LAKEHEAD UNIVERSITY WEB SCRAPER")
        print("=" * 80)
        print(f"Max pages: {max_pages or 'UNLIMITED - All discoverable pages'}")
        print(f"Output directory: {self.OUTPUT_DIR}")
        print()

        # Discover URLs from sitemaps
        print("Discovering URLs from sitemaps...")
        for sitemap in self.SITEMAPS:
            urls = self.discover_urls_from_sitemap(sitemap)
            for url in urls:
                if self.is_valid_url(url):
                    priority = self.prioritize_url(url)
                    heappush(self.url_queue, (priority, url))
                    self.discovered_urls.add(url)

        # Add seed URLs
        print(f"Adding {len(self.SEED_URLS)} seed URLs...")
        for url in self.SEED_URLS:
            if self.is_valid_url(url):
                priority = self.prioritize_url(url)
                heappush(self.url_queue, (priority, url))
                self.discovered_urls.add(url)

        print(f"Starting crawl with {len(self.url_queue)} URLs in queue")
        print()

        created_files = []

        # Process priority queue
        while self.url_queue:
            if max_pages and self.statistics['pages_scraped'] >= max_pages:
                print(f"\nReached maximum page limit ({max_pages})")
                break

            priority, url = heappop(self.url_queue)

            try:
                file_path = self.scrape_page(url)
                if file_path:
                    created_files.append(file_path)
                    self.statistics['by_priority'][priority] = \
                        self.statistics['by_priority'].get(priority, 0) + 1

                # Save state periodically
                if self.statistics['pages_scraped'] % 50 == 0 and self.statistics['pages_scraped'] > 0:
                    self.save_crawler_state()
                    print(f"\nProgress: {self.statistics['pages_scraped']} scraped, "
                          f"{len(self.url_queue)} in queue, "
                          f"{self.statistics['pages_skipped']} skipped, "
                          f"{self.statistics['faq_items_found']} FAQ items")
                    print(f"Priority distribution - T1: {self.statistics['by_priority'][1]}, "
                          f"T2: {self.statistics['by_priority'][2]}, "
                          f"T3: {self.statistics['by_priority'][3]}")

            except Exception as e:
                print(f"Error processing {url}: {e}")
                self.failed_urls.add(url)
                self.statistics['pages_failed'] += 1

        self.statistics['end_time'] = datetime.now().isoformat()
        self.save_crawler_state()

        print()
        print("=" * 80)
        print("CRAWLING COMPLETE!")
        print("=" * 80)
        print(f"Pages scraped: {self.statistics['pages_scraped']}")
        print(f"Pages skipped: {self.statistics['pages_skipped']}")
        print(f"Pages failed: {self.statistics['pages_failed']}")
        print(f"FAQ items found: {self.statistics['faq_items_found']}")
        print(f"Links discovered: {self.statistics['links_discovered']}")
        print(f"Files created: {len(created_files)}")
        print()

        return created_files


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Comprehensive recursive scraper for ALL Lakehead University pages'
    )
    parser.add_argument('--max-pages', type=int,
                       help='Maximum number of pages to crawl (default: unlimited)')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from previous crawl state')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between requests in seconds (default: 1.0)')
    args = parser.parse_args()

    scraper = ComprehensiveLakeheadScraper(delay=args.delay, resume=args.resume)
    scraper.crawl_comprehensive(max_pages=args.max_pages)


if __name__ == "__main__":
    main()
