#!/usr/bin/env python3
"""FAQ scraper for Lakehead University Student Central FAQ page.

This script extracts Q&A pairs from the structured FAQ page at
https://www.lakeheadu.ca/studentcentral/faq
"""

import json
import re
from pathlib import Path
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class FAQScraper:
    """Scraper for FAQ pages."""

    FAQ_URL = "https://www.lakeheadu.ca/studentcentral/faq"
    OUTPUT_DIR = Path(__file__).parent.parent / "data" / "lakehead_scraped"

    def __init__(self):
        """Initialize FAQ scraper."""
        self.output_dir = self.OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a webpage.

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching {url}: {e}")
            return None

    def clean_text(self, text: str) -> str:
        """Clean and normalize text.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove newlines
        text = text.replace('\n', ' ').replace('\r', ' ')
        return text.strip()

    def extract_faq_qa_pairs(self, soup: BeautifulSoup, base_url: str) -> List[dict]:
        """Extract Q&A pairs from FAQ page structure.

        Args:
            soup: BeautifulSoup object of the FAQ page
            base_url: Base URL for resolving relative links

        Returns:
            List of Q&A dictionaries
        """
        qa_pairs = []

        # Find all accordion sections or FAQ sections
        # The FAQ page uses expandable sections with categories
        # Look for common FAQ structures

        # Method 1: Look for sections with category headings
        # The page likely has sections like "Undergraduate Admissions", "Personal Information", etc.

        # Find all sections that might contain FAQs
        # Look for common patterns: accordion items, FAQ sections, etc.

        # Try to find FAQ categories first
        category_sections = soup.find_all(['section', 'div'], class_=re.compile(r'(faq|accordion|category|section)', re.I))

        if not category_sections:
            # If no specific sections found, look for headings followed by content
            category_sections = soup.find_all(['h2', 'h3', 'h4'])

        current_category = None
        current_subcategory = None

        # Look for tables with Q&A structure
        # FAQ page uses tables where each Q&A pair is in separate rows
        # Row 1: Question (single cell)
        # Row 2: Answer (single cell)
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')

            # Try to find category heading before this table
            heading = table.find_previous(['h2', 'h3', 'h4'])
            if heading:
                heading_text = self.clean_text(heading.get_text())
                if heading_text and len(heading_text) > 3:
                    # Determine if this is a main category (h2) or subcategory (h3)
                    if heading.name == 'h2':
                        current_category = heading_text
                        current_subcategory = None
                    elif heading.name == 'h3':
                        current_subcategory = heading_text

            # Process rows in pairs (question, answer)
            i = 0
            while i < len(rows):
                # Get question from current row
                question_cells = rows[i].find_all(['td', 'th'])
                if question_cells:
                    question_text = self.clean_text(question_cells[0].get_text())

                    # Next row should be the answer
                    if i + 1 < len(rows):
                        answer_cells = rows[i + 1].find_all(['td', 'th'])
                        if answer_cells:
                            answer_text = self.clean_text(answer_cells[0].get_text())

                            # Only add if both question and answer are meaningful
                            if question_text and answer_text and len(question_text) > 10 and len(answer_text) > 20:
                                # Extract links from answer cell
                                links = []
                                for link in answer_cells[0].find_all('a', href=True):
                                    href = link.get('href', '')
                                    link_text = self.clean_text(link.get_text())
                                    if href.startswith('http'):
                                        links.append({'text': link_text, 'url': href})
                                    else:
                                        full_url = urljoin(base_url, href)
                                        links.append({'text': link_text, 'url': full_url})

                                qa_pairs.append({
                                    'category': current_category or 'General',
                                    'subcategory': current_subcategory,
                                    'question': question_text,
                                    'answer': answer_text,
                                    'related_links': links,
                                    'source_url': base_url,
                                    'keywords': self.extract_keywords(question_text, answer_text)
                                })

                                # Skip next row since we already processed it
                                i += 2
                                continue

                i += 1

        # Alternative method: Look for structured FAQ format
        # Some FAQ pages use definition lists (dl, dt, dd)
        definition_lists = soup.find_all('dl')
        for dl in definition_lists:
            questions = dl.find_all('dt')
            answers = dl.find_all('dd')

            for q, a in zip(questions, answers):
                question_text = self.clean_text(q.get_text())
                answer_text = self.clean_text(a.get_text())

                if question_text and answer_text:
                    links = []
                    for link in a.find_all('a', href=True):
                        href = link.get('href', '')
                        link_text = self.clean_text(link.get_text())
                        if href.startswith('http'):
                            links.append({'text': link_text, 'url': href})
                        else:
                            full_url = urljoin(base_url, href)
                            links.append({'text': link_text, 'url': full_url})

                    qa_pairs.append({
                        'category': current_category or 'General',
                        'subcategory': current_subcategory,
                        'question': question_text,
                        'answer': answer_text,
                        'related_links': links,
                        'source_url': base_url,
                        'keywords': self.extract_keywords(question_text, answer_text)
                    })

        # Method 3: Look for questions as headings followed by answer paragraphs
        # This is common in FAQ pages
        headings = soup.find_all(['h3', 'h4', 'h5', 'strong'])

        for heading in headings:
            heading_text = self.clean_text(heading.get_text())

            # Check if this looks like a question
            if '?' in heading_text and len(heading_text) > 10:
                # Find the answer (next sibling elements)
                answer_parts = []
                current = heading.next_sibling

                while current:
                    if hasattr(current, 'name'):
                        if current.name in ['p', 'div', 'ul', 'ol']:
                            text = self.clean_text(current.get_text())
                            if text:
                                answer_parts.append(text)
                        elif current.name in ['h3', 'h4', 'h5', 'h6']:
                            # Stop at next heading
                            break
                    elif isinstance(current, str):
                        text = self.clean_text(current)
                        if text:
                            answer_parts.append(text)

                    current = current.next_sibling

                if answer_parts:
                    answer_text = ' '.join(answer_parts)

                    # Extract links
                    links = []
                    answer_elem = heading.find_next(['p', 'div'])
                    if answer_elem:
                        for link in answer_elem.find_all('a', href=True):
                            href = link.get('href', '')
                            link_text = self.clean_text(link.get_text())
                            if href.startswith('http'):
                                links.append({'text': link_text, 'url': href})
                            else:
                                full_url = urljoin(base_url, href)
                                links.append({'text': link_text, 'url': full_url})

                    # Don't add if we already have this from table extraction
                    if not any(qa['question'].lower() == heading_text.lower() for qa in qa_pairs):
                        qa_pairs.append({
                            'category': current_category or 'General',
                            'subcategory': current_subcategory,
                            'question': heading_text,
                            'answer': answer_text,
                            'related_links': links,
                            'source_url': base_url,
                            'keywords': self.extract_keywords(heading_text, answer_text)
                        })

        # Try to identify categories from page structure
        # Update categories if we found them
        for i, qa in enumerate(qa_pairs):
            # Try to find which section this Q&A belongs to
            # This is a heuristic - may need refinement based on actual page structure
            question_lower = qa['question'].lower()
            answer_lower = qa['answer'].lower()

            if any(word in question_lower or word in answer_lower for word in ['admission', 'apply', 'application', 'offer', 'deadline']):
                qa['category'] = 'Undergraduate Admissions'
            elif any(word in question_lower or word in answer_lower for word in ['osap', 'financial', 'aid', 'scholarship', 'loan', 'grant']):
                qa['category'] = 'Financing, Scholarships & Awards and Government Aid'
            elif any(word in question_lower or word in answer_lower for word in ['grade', 'course', 'registration', 'academic', 'exam']):
                qa['category'] = 'Academics'
            elif any(word in question_lower or word in answer_lower for word in ['graduation', 'convocation', 'degree', 'diploma']):
                qa['category'] = 'Graduation & Convocation'
            elif any(word in question_lower or word in answer_lower for word in ['date', 'deadline', 'calendar', 'semester', 'term']):
                qa['category'] = 'Important Dates'
            elif any(word in question_lower or word in answer_lower for word in ['name', 'address', 'contact', 'personal', 'update']):
                qa['category'] = 'Personal Information'

        return qa_pairs

    def extract_keywords(self, question: str, answer: str) -> List[str]:
        """Extract keywords from question and answer.

        Args:
            question: Question text
            answer: Answer text

        Returns:
            List of keywords
        """
        # Common stopwords to exclude
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'when', 'where', 'why', 'how'}

        # Extract words
        text = (question + ' ' + answer).lower()
        words = re.findall(r'\b[a-z]{3,}\b', text)

        # Filter stopwords and get unique keywords
        keywords = list(set([w for w in words if w not in stopwords]))

        # Return top 10 keywords
        return keywords[:10]

    def scrape_faq(self) -> List[dict]:
        """Scrape FAQ page and extract Q&A pairs.

        Returns:
            List of Q&A dictionaries
        """
        print("Fetching FAQ page...")
        soup = self.fetch_page(self.FAQ_URL)

        if not soup:
            print("Failed to fetch FAQ page")
            return []

        print("Extracting Q&A pairs...")
        qa_pairs = self.extract_faq_qa_pairs(soup, self.FAQ_URL)

        print(f"Extracted {len(qa_pairs)} Q&A pairs")

        return qa_pairs

    def save_results(self, qa_pairs: List[dict], output_format: str = 'both'):
        """Save Q&A pairs to file.

        Args:
            qa_pairs: List of Q&A dictionaries
            output_format: 'json', 'csv', or 'both'
        """
        # Save as JSON
        if output_format in ['json', 'both']:
            json_file = self.output_dir / 'faq_qa.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
            print(f"Saved JSON to: {json_file}")

        # Save as CSV
        if output_format in ['csv', 'both']:
            csv_file = self.output_dir / 'faq_qa.csv'
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('Category,Subcategory,Question,Answer,Source_URL,Keywords\n')
                for qa in qa_pairs:
                    category = (qa.get('category') or '').replace('"', '""')
                    subcategory = (qa.get('subcategory') or '').replace('"', '""')
                    question = qa['question'].replace('"', '""')
                    answer = qa['answer'].replace('"', '""')
                    source_url = (qa.get('source_url') or '').replace('"', '""')
                    keywords = ', '.join(qa.get('keywords', []))

                    f.write(f'"{category}","{subcategory}","{question}","{answer}","{source_url}","{keywords}"\n')
            print(f"Saved CSV to: {csv_file}")


def main():
    """Main entry point."""
    print("=" * 80)
    print("Lakehead University FAQ Scraper")
    print("=" * 80)
    print()

    scraper = FAQScraper()
    qa_pairs = scraper.scrape_faq()

    if qa_pairs:
        scraper.save_results(qa_pairs, output_format='both')
        print()
        print("=" * 80)
        print("FAQ Scraping Complete!")
        print("=" * 80)
        print(f"Total Q&A pairs extracted: {len(qa_pairs)}")
        print()

        # Show categories
        categories = {}
        for qa in qa_pairs:
            cat = qa.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1

        print("Categories found:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"  - {cat}: {count} Q&A pairs")
    else:
        print("No Q&A pairs extracted. Check the FAQ page structure.")


if __name__ == "__main__":
    main()

