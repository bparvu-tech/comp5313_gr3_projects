#!/usr/bin/env python3
"""
Generate Dialogflow CX Playbook Instructions from Scraped Data

This script processes the scraped Lakehead University markdown files
and generates a comprehensive instruction set for a Dialogflow CX playbook.
"""

import os
import re
from pathlib import Path
from collections import defaultdict


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove markdown links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove markdown headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    return text.strip()


def extract_content(file_path: Path) -> dict:
    """Extract content from a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title (first heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem
        
        # Clean content
        cleaned = clean_text(content)
        
        return {
            'title': title,
            'content': cleaned[:500],  # First 500 chars
            'file': file_path.name
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def categorize_files(data_dir: Path) -> dict:
    """Categorize files by topic."""
    categories = defaultdict(list)
    
    for md_file in data_dir.glob('**/*.md'):
        if md_file.name == 'crawler_state.json':
            continue
        
        filename = md_file.name.lower()
        
        # Categorize based on filename
        if any(x in filename for x in ['admission', 'apply', 'application']):
            categories['Admissions'].append(md_file)
        elif any(x in filename for x in ['tuition', 'fee', 'cost', 'financial']):
            categories['Tuition & Financial Aid'].append(md_file)
        elif any(x in filename for x in ['residence', 'housing', 'accommodation']):
            categories['Residence & Housing'].append(md_file)
        elif any(x in filename for x in ['program', 'academics', 'course', 'department']):
            categories['Academic Programs'].append(md_file)
        elif any(x in filename for x in ['career', 'employment', 'job']):
            categories['Career Services'].append(md_file)
        elif any(x in filename for x in ['student-services', 'health', 'wellness', 'accessibility']):
            categories['Student Services'].append(md_file)
        elif any(x in filename for x in ['campus-life', 'club', 'event', 'recreation']):
            categories['Campus Life'].append(md_file)
        else:
            categories['General Information'].append(md_file)
    
    return categories


def generate_playbook_instructions(data_dir: Path, output_file: Path):
    """Generate playbook instructions from scraped data."""
    categories = categorize_files(data_dir)
    
    instructions = []
    instructions.append("# Lakehead University Virtual Assistant")
    instructions.append("\nYou are a helpful virtual assistant for Lakehead University.")
    instructions.append("Your role is to answer questions about the university, its programs, services, and campus life.")
    instructions.append("\n## Guidelines")
    instructions.append("- Provide accurate, helpful information based on the knowledge below")
    instructions.append("- Be friendly, professional, and supportive")
    instructions.append("- If you don't know something, acknowledge it and suggest contacting the relevant department")
    instructions.append("- Always prioritize student success and well-being")
    instructions.append("\n## Knowledge Base\n")
    
    # Generate summaries for each category
    for category, files in sorted(categories.items()):
        if not files:
            continue
        
        instructions.append(f"\n### {category}")
        instructions.append(f"\n({len(files)} resources available)\n")
        
        # Add sample content from first few files in category
        for file_path in files[:3]:  # Limit to 3 examples per category
            content_data = extract_content(file_path)
            if content_data and len(content_data['content']) > 50:
                instructions.append(f"\n**{content_data['title']}**")
                instructions.append(f"{content_data['content'][:300]}...\n")
    
    instructions.append("\n## Contact Information")
    instructions.append("\nFor specific questions not covered here, students can:")
    instructions.append("- Visit the Lakehead University website")
    instructions.append("- Contact Student Services")
    instructions.append("- Email admissions@lakeheadu.ca for admissions questions")
    instructions.append("- Visit the campus in person (Thunder Bay or Orillia)")
    
    instructions.append("\n## Response Format")
    instructions.append("\nWhen answering questions:")
    instructions.append("1. Provide a clear, direct answer")
    instructions.append("2. Include relevant details and context")
    instructions.append("3. Suggest next steps or additional resources when appropriate")
    instructions.append("4. Maintain a supportive, encouraging tone")
    
    # Write to file
    output_content = '\n'.join(instructions)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"\nPlaybook instructions generated: {output_file}")
    print(f"Total categories: {len(categories)}")
    print(f"Total files processed: {sum(len(files) for files in categories.values())}")
    print("\nNext steps:")
    print("1. Open the generated file and review the instructions")
    print("2. Copy the content")
    print("3. Go to your Dialogflow CX agent console")
    print("4. Navigate to Playbooks > Default Playbook")
    print("5. Paste the instructions into the 'Instructions' field")
    print("6. Save and test your agent")


if __name__ == '__main__':
    # Set paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / 'data' / 'lakehead_scraped'
    output_dir = project_root / 'data' / 'dialogflow_ready'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'playbook_instructions.txt'
    
    print("Generating Dialogflow CX Playbook Instructions...")
    print(f"Reading from: {data_dir}")
    print(f"Output to: {output_file}")
    
    generate_playbook_instructions(data_dir, output_file)

