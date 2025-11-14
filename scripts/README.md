# Scripts

This directory contains utility scripts for the Lakehead University Chatbot project.

## Comprehensive Web Scraper

### Overview

The `scrape_lakehead.py` script is a comprehensive recursive web scraper that discovers and scrapes ALL pages across Lakehead University's website. It uses advanced content extraction to capture FAQs, program information, and general content.

### Key Features

- **Recursive Crawling**: Automatically discovers and scrapes all Lakehead University pages
- **Smart URL Discovery**: Discovers URLs from sitemaps and by following links on pages
- **Priority-Based Crawling**: High-value content (FAQs, programs, admissions) scraped first
- **Advanced FAQ Extraction**: Properly extracts numbered Q&A pairs with full formatting
- **Comprehensive Content Capture**: Extracts sections, lists, tables, contact info, and links
- **Resume Capability**: Can resume interrupted crawls from saved state
- **Duplicate Detection**: Skips duplicate content to avoid wasting resources
- **Proper Rate Limiting**: 1-second delay between requests (configurable)
- **Progress Tracking**: Real-time statistics on crawling progress

### Installation

Install required dependencies:

```bash
pip install requests beautifulsoup4
```

Or with conda:

```bash
conda install -c conda-forge requests beautifulsoup4
```

### Usage

#### Scrape All Discoverable Pages (Unlimited)

```bash
# Scrapes ALL Lakehead University pages - can discover thousands of pages
python scripts/scrape_lakehead.py
```

This will:
1. Check sitemaps for URLs
2. Start from seed URLs (homepage, programs, departments, etc.)
3. Recursively discover links on each page
4. Scrape all discovered pages with no limit
5. Save state every 50 pages (can be resumed)

#### Scrape Limited Number of Pages

```bash
# Scrape first 100 pages (useful for testing)
python scripts/scrape_lakehead.py --max-pages 100
```

#### Resume Interrupted Crawl

```bash
# Resume from where you left off
python scripts/scrape_lakehead.py --resume
```

#### Adjust Request Delay

```bash
# Use 2-second delay between requests
python scripts/scrape_lakehead.py --delay 2.0
```

#### Combined Options

```bash
# Resume crawl, max 500 pages, 1.5 second delay
python scripts/scrape_lakehead.py --resume --max-pages 500 --delay 1.5
```

### How It Works

1. **URL Discovery**
   - Checks sitemaps (lakeheadu.ca, csdc.lakeheadu.ca, lusu.ca)
   - Starts with seed URLs (homepage, major sections)
   - Discovers new links on every page scraped

2. **Priority System**
   - **Tier 1 (High Priority)**: FAQs, programs, admissions, tuition, housing, LUSU
   - **Tier 2 (Medium Priority)**: Student services, catalog, policies, international
   - **Tier 3 (Low Priority)**: General pages, news, events

3. **Content Extraction**
   - **FAQ Detection**: Finds numbered questions (e.g., "1. Why Take Computer Science?")
   - **Structured Content**: Extracts headings, sections, lists, tables
   - **Contact Info**: Automatically extracts emails and phone numbers
   - **Links**: Preserves related links for reference

4. **Quality Control**
   - Skips pages with < 50 words
   - Detects and skips duplicate content
   - Filters navigation/sidebar content
   - Validates URLs before crawling

### Output

Scraped content is saved to:
```
data/lakehead_scraped/
├── programs_departments_computer-science_future-students_faq.md  (4.9 KB - 7 FAQ items!)
├── programs_overview.md                                           (15 KB)
├── admissions.md
├── tuition_fees.md
├── [... hundreds/thousands more files ...]
└── crawler_state.json  (for resume capability)
```

Each markdown file includes:
- Page title and source URL
- FAQ questions and answers (if present)
- Structured content with headings
- Lists and tables
- Contact information
- Related links
- Scrape timestamp

### Example Output

**Before (old scraper):** CS FAQ = 500 bytes, no Q&A content
**After (new scraper):** CS FAQ = 4,900 bytes, all 7 Q&A pairs with full answers!

```markdown
# FAQ | Lakehead University

## Frequently Asked Questions

### 1. Why Take Computer Science at Lakehead?

• Faculty are readily available for student consultation.
• We follow a rigorous curriculum regularly brought up-to-date...
• Professional experience through Co-op...
[...12 detailed bullet points...]

### 2. What if I don't have any computing experience?
[Full answer extracted...]

[... all 7 questions with complete answers ...]
```

### Statistics and Monitoring

During crawling, you'll see:
```
Progress: 100 scraped, 450 in queue, 23 skipped, 15 FAQ items
Priority distribution - T1: 45, T2: 35, T3: 20
```

After completion:
- Total pages scraped
- Pages skipped (duplicates/low quality)
- Pages failed (404, timeouts)
- FAQ items found
- Links discovered
- Files created

### Performance

- **Speed**: ~1 page per second (with 1.0 delay)
- **Scale**: Can discover and scrape 500+ pages
- **Efficiency**: Skips duplicates and low-quality pages
- **Memory**: Modest - state is periodically saved to disk

### Advanced Options

#### Customize Seed URLs

Edit `SEED_URLS` in the script to change starting points:
```python
SEED_URLS = [
    "https://www.lakeheadu.ca",
    "https://www.lakeheadu.ca/your/custom/page",
]
```

#### Adjust Priority Levels

Modify `prioritize_url()` to change which pages are scraped first.

#### Change Output Directory

Modify `OUTPUT_DIR` in the script.

### Best Practices

1. **Start with Limited Pages**: Test with `--max-pages 50` first
2. **Use Resume**: For large crawls, use `--resume` if interrupted
3. **Monitor Progress**: Watch statistics to ensure quality extraction
4. **Respect Rate Limits**: Keep delay >= 1.0 seconds
5. **Check Output**: Spot-check a few files to verify content quality

### Troubleshooting

**No Content Extracted:**
- Page might be JavaScript-rendered
- Check if URL is accessible in browser
- Verify page has actual content

**Too Many 404 Errors:**
- Normal for some pages (moved/deleted)
- Check if site structure has changed

**Slow Performance:**
- Increase `--delay` if server is slow
- Use `--max-pages` to limit scope

**Out of Memory:**
- The scraper saves state periodically
- Restart with `--resume` to continue

### Integration with Chatbot

Use scraped content to:
1. **Build Dialogflow Intents**: Extract Q&A pairs from FAQ files
2. **Create Training Data**: Use questions as training phrases
3. **Generate Responses**: Use answers as fulfillment text
4. **Extract Entities**: Programs, departments, services, locations

### Other Scripts

- **scrape_faq.py**: Specialized FAQ scraper (kept for reference)

### License

This script is for educational purposes only. Always respect website terms of service and robots.txt files.
