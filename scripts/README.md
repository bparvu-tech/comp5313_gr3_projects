# Scripts

This directory contains utility scripts for the Lakehead University Chatbot project.

## Web Scraper

### Overview

The `scrape_lakehead.py` script collects data from Lakehead University's website and saves it to markdown files. This data can be used to enhance the chatbot's knowledge base.

### Features

- Scrapes multiple sections of the Lakehead University website
- Extracts and cleans text content
- Generates well-structured markdown files
- Includes proper rate limiting to be respectful to the server
- Saves all content to the `data/lakehead_scraped/` directory

### Usage

#### Prerequisites

Install the required dependencies:

```bash
pip install requests beautifulsoup4
```

Or if using conda:

```bash
conda install -c conda-forge requests beautifulsoup4
```

#### Running the Scraper

```bash
# From the project root directory
python scripts/scrape_lakehead.py
```

Or make it executable and run directly:

```bash
chmod +x scripts/scrape_lakehead.py
./scripts/scrape_lakehead.py
```

### Configuration

The scraper is configured to scrape the following sections:

- **Programs**: Academic programs offered at Lakehead University
- **Admissions**: Admissions information for prospective students
- **Tuition & Fees**: Tuition and fees information
- **Campus Life**: Student life and campus information
- **Research**: Research activities and opportunities
- **About**: About Lakehead University

You can modify the `SECTIONS` dictionary in the script to add or remove sections.

### Output

The scraper saves markdown files to:
```
data/lakehead_scraped/
├── programs.md
├── admissions.md
├── tuition_fees.md
├── campus_life.md
├── research.md
└── about.md
```

Each markdown file contains:
- Page title and metadata
- Table of contents from headings
- Main content (first 5000 characters)
- Related links

### Customization

You can customize the scraper by modifying:

- **Delay between requests**: Change the `delay` parameter in `LakeheadScraper()`
- **Content length**: Modify the character limit in `generate_markdown()`
- **Sections to scrape**: Update the `SECTIONS` dictionary

### Best Practices

1. **Be respectful**: The script includes a 1-second delay between requests
2. **Check robots.txt**: Always respect the website's robots.txt file
3. **Update content regularly**: Re-run the scraper periodically to keep data current
4. **Use responsibly**: Don't overload the server with requests

### Troubleshooting

If you encounter issues:

1. **Check internet connection**: Ensure you have internet access
2. **Verify URLs**: Some URLs may have changed - update them in the script
3. **Install dependencies**: Make sure all required packages are installed
4. **Check permissions**: Ensure the script has write permissions for the output directory

### License

This script is for educational purposes only. Always respect website terms of service and copyright laws.
