#!/usr/bin/env python3
"""Generate Dialogflow intents from scraped Lakehead University data.

This script processes markdown files from the lakehead_scraped directory
and generates Dialogflow-compatible intent JSON files for bulk import.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class DialogflowIntentGenerator:
    """Generate Dialogflow intents from scraped markdown content."""

    def __init__(self, input_dir: Path, output_dir: Path):
        """Initialize the generator.

        Args:
            input_dir: Directory containing scraped markdown files
            output_dir: Directory to output Dialogflow intent JSON files
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Track generated intents
        self.intents = []
        self.entities = {
            'programs': set(),
            'departments': set(),
            'services': set(),
            'locations': set()
        }

    def parse_markdown_file(self, file_path: Path) -> Optional[Dict]:
        """Parse a markdown file and extract metadata and content.

        Args:
            file_path: Path to markdown file

        Returns:
            Dictionary with parsed content or None if parsing fails
        """
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract metadata
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            source_match = re.search(r'\*\*Source\*\*:\s*(.+)$', content, re.MULTILINE)

            # Extract main content section
            content_match = re.search(r'##\s+Content\s*\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)

            if not title_match:
                return None

            return {
                'title': title_match.group(1).strip(),
                'source': source_match.group(1).strip() if source_match else '',
                'content': content_match.group(1).strip() if content_match else '',
                'filename': file_path.stem,
                'is_faq': 'faq' in file_path.stem.lower()
            }

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def extract_entities(self, text: str):
        """Extract common entities from text.

        Args:
            text: Text to extract entities from
        """
        # Common program keywords
        programs = re.findall(r'\b(Computer Science|Engineering|Business|Biology|Chemistry|'
                             r'Physics|Mathematics|Psychology|English|History|'
                             r'Nursing|Education|Law|Medicine|MBA|MSc|PhD|'
                             r'Bachelor|Master|Doctorate|BA|BSc|HBA|BEd)\b', text, re.I)
        self.entities['programs'].update(p.lower() for p in programs)

        # Department keywords
        departments = re.findall(r'\b(Department of|Faculty of|School of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                                 text)
        self.entities['departments'].update(d[1].lower() for d in departments)

        # Service keywords
        services = re.findall(r'\b(library|health|wellness|housing|residence|dining|'
                              r'career services|accessibility|counseling|financial aid|'
                              r'student success|LUSU)\b', text, re.I)
        self.entities['services'].update(s.lower() for s in services)

        # Location keywords
        locations = re.findall(r'\b(Thunder Bay|Orillia|campus|building)\b', text, re.I)
        self.entities['locations'].update(loc.lower() for loc in locations)

    def generate_training_phrases(self, title: str, is_faq: bool = False) -> List[str]:
        """Generate training phrases from title.

        Args:
            title: Title of the page
            is_faq: Whether this is from an FAQ page

        Returns:
            List of training phrases
        """
        phrases = []

        # Clean title
        clean_title = title.replace(' | Lakehead University', '').strip()

        if is_faq:
            # FAQ-style phrases
            phrases.extend([
                clean_title,
                f"What is {clean_title}?",
                f"Tell me about {clean_title}",
                f"Can you explain {clean_title}?",
                f"I need information about {clean_title}",
                f"Help with {clean_title}"
            ])
        else:
            # General information phrases
            phrases.extend([
                clean_title,
                f"Tell me about {clean_title}",
                f"Information about {clean_title}",
                f"What do you know about {clean_title}?",
                f"I want to learn about {clean_title}"
            ])

        # Add variations based on keywords
        lower_title = clean_title.lower()

        if 'program' in lower_title:
            phrases.extend([
                f"What programs are available?",
                f"Tell me about academic programs"
            ])
        elif 'admission' in lower_title:
            phrases.extend([
                "How do I apply?",
                "What are the admission requirements?",
                "Application process"
            ])
        elif 'tuition' in lower_title or 'fee' in lower_title:
            phrases.extend([
                "How much does it cost?",
                "What are the fees?",
                "Tuition information"
            ])
        elif 'housing' in lower_title or 'residence' in lower_title:
            phrases.extend([
                "Where can I live?",
                "Tell me about residence",
                "Housing options"
            ])

        return phrases[:10]  # Limit to 10 phrases per intent

    def chunk_content(self, content: str, max_length: int = 500) -> List[str]:
        """Split content into chunks suitable for Dialogflow responses.

        Args:
            content: Content to chunk
            max_length: Maximum length per chunk

        Returns:
            List of content chunks
        """
        # Split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def create_intent(self, parsed_data: Dict) -> Dict:
        """Create a Dialogflow intent from parsed data.

        Args:
            parsed_data: Parsed markdown data

        Returns:
            Dialogflow intent JSON structure
        """
        # Generate intent name
        intent_name = parsed_data['filename'].replace('_', '.').replace('-', '.')

        # Generate training phrases
        training_phrases_list = self.generate_training_phrases(
            parsed_data['title'],
            parsed_data['is_faq']
        )

        # Format training phrases for Dialogflow
        training_phrases = []
        for phrase in training_phrases_list:
            training_phrases.append({
                "parts": [{"text": phrase}],
                "type": "EXAMPLE",
                "timesAddedCount": 1
            })

        # Chunk content for responses
        content_chunks = self.chunk_content(parsed_data['content'])

        # Create response messages
        messages = []
        if content_chunks:
            # Use first chunk as main response
            main_response = content_chunks[0]

            # Add source link if available
            if parsed_data['source']:
                main_response += f"\n\nFor more information, visit: {parsed_data['source']}"

            messages.append({
                "text": {
                    "text": [main_response]
                },
                "lang": "en"
            })

        # Create intent structure
        intent = {
            "name": intent_name,
            "auto": True,
            "contexts": [],
            "responses": [{
                "resetContexts": False,
                "action": intent_name,
                "affectedContexts": [],
                "parameters": [],
                "messages": messages,
                "defaultResponsePlatforms": {},
                "speech": []
            }],
            "priority": 500000,
            "webhookUsed": False,
            "webhookForSlotFilling": False,
            "fallbackIntent": False,
            "events": [],
            "conditionalResponses": [],
            "condition": "",
            "conditionalFollowupEvents": []
        }

        # Add training phrases
        if training_phrases:
            intent["responses"][0]["parameters"] = []
            intent["userSays"] = training_phrases

        return intent

    def generate_welcome_intent(self) -> Dict:
        """Generate a welcome intent for the chatbot.

        Returns:
            Welcome intent JSON structure
        """
        return {
            "name": "Default Welcome Intent",
            "auto": True,
            "contexts": [],
            "responses": [{
                "resetContexts": False,
                "action": "input.welcome",
                "affectedContexts": [],
                "parameters": [],
                "messages": [{
                    "text": {
                        "text": [
                            "Hello! I'm the Lakehead University assistant. I can help you with "
                            "information about programs, admissions, tuition, housing, student services, "
                            "and more. What would you like to know?"
                        ]
                    },
                    "lang": "en"
                }],
                "defaultResponsePlatforms": {},
                "speech": []
            }],
            "priority": 500000,
            "webhookUsed": False,
            "webhookForSlotFilling": False,
            "fallbackIntent": False,
            "events": [{
                "name": "WELCOME"
            }],
            "conditionalResponses": [],
            "condition": "",
            "conditionalFollowupEvents": [],
            "userSays": []
        }

    def generate_fallback_intent(self) -> Dict:
        """Generate a fallback intent for unmatched queries.

        Returns:
            Fallback intent JSON structure
        """
        return {
            "name": "Default Fallback Intent",
            "auto": True,
            "contexts": [],
            "responses": [{
                "resetContexts": False,
                "action": "input.unknown",
                "affectedContexts": [],
                "parameters": [],
                "messages": [{
                    "text": {
                        "text": [
                            "I'm sorry, I didn't understand that. I can help you with information "
                            "about Lakehead University programs, admissions, tuition, housing, and "
                            "student services. Could you rephrase your question?",
                            "I'm not sure I understand. Try asking about programs, admissions, "
                            "housing, or student services at Lakehead University.",
                            "I don't have information about that yet. You can ask me about academic "
                            "programs, campus life, admissions, or student services."
                        ]
                    },
                    "lang": "en"
                }],
                "defaultResponsePlatforms": {},
                "speech": []
            }],
            "priority": 500000,
            "webhookUsed": False,
            "webhookForSlotFilling": False,
            "fallbackIntent": True,
            "events": [],
            "conditionalResponses": [],
            "condition": "",
            "conditionalFollowupEvents": [],
            "userSays": []
        }

    def process_all_files(self, max_intents: Optional[int] = 100):
        """Process all markdown files and generate intents.

        Args:
            max_intents: Maximum number of intents to generate (None for all)
        """
        print("=" * 80)
        print("Dialogflow Intent Generator for Lakehead University Chatbot")
        print("=" * 80)
        print()

        # Get all markdown files
        md_files = list(self.input_dir.glob('*.md'))
        print(f"Found {len(md_files)} markdown files")

        # Prioritize FAQ files
        faq_files = [f for f in md_files if 'faq' in f.stem.lower()]
        other_files = [f for f in md_files if 'faq' not in f.stem.lower()]

        print(f"  - FAQ files: {len(faq_files)}")
        print(f"  - Other files: {len(other_files)}")
        print()

        # Process files (FAQs first)
        files_to_process = faq_files + other_files
        if max_intents:
            files_to_process = files_to_process[:max_intents]

        print(f"Processing {len(files_to_process)} files...")
        print()

        processed = 0
        skipped = 0

        for file_path in files_to_process:
            parsed = self.parse_markdown_file(file_path)

            if not parsed or not parsed['content']:
                skipped += 1
                continue

            # Extract entities
            self.extract_entities(parsed['content'])

            # Create intent
            intent = self.create_intent(parsed)
            self.intents.append(intent)

            processed += 1
            if processed % 10 == 0:
                print(f"Processed {processed} intents...")

        print()
        print(f"✓ Processed {processed} intents")
        print(f"✗ Skipped {skipped} files (no content)")
        print()

    def save_intents(self):
        """Save generated intents to JSON files."""
        print("Saving intents to Dialogflow format...")
        print()

        # Add default intents
        self.intents.insert(0, self.generate_welcome_intent())
        self.intents.append(self.generate_fallback_intent())

        # Save as individual intent files (Dialogflow format)
        intents_dir = self.output_dir / "intents"
        intents_dir.mkdir(exist_ok=True)

        for intent in self.intents:
            intent_name = intent['name'].replace(' ', '_').replace('.', '_')
            intent_file = intents_dir / f"{intent_name}.json"

            with open(intent_file, 'w', encoding='utf-8') as f:
                json.dump(intent, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved {len(self.intents)} intent files to {intents_dir}")

        # Save bulk import file
        bulk_file = self.output_dir / "intents_bulk_import.json"
        with open(bulk_file, 'w', encoding='utf-8') as f:
            json.dump(self.intents, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved bulk import file to {bulk_file}")

        # Save entities
        self.save_entities()

        # Save statistics
        self.save_statistics()

    def save_entities(self):
        """Save extracted entities."""
        entities_dir = self.output_dir / "entities"
        entities_dir.mkdir(exist_ok=True)

        for entity_type, values in self.entities.items():
            if not values:
                continue

            entity_data = {
                "name": entity_type,
                "entries": [
                    {
                        "value": value,
                        "synonyms": [value]
                    }
                    for value in sorted(values)
                ],
                "isEnum": False,
                "automatedExpansion": True
            }

            entity_file = entities_dir / f"{entity_type}.json"
            with open(entity_file, 'w', encoding='utf-8') as f:
                json.dump(entity_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved {len(self.entities)} entity types to {entities_dir}")

    def save_statistics(self):
        """Save generation statistics."""
        stats = {
            "generated_at": datetime.now().isoformat(),
            "total_intents": len(self.intents),
            "entities": {
                entity_type: len(values)
                for entity_type, values in self.entities.items()
            }
        }

        stats_file = self.output_dir / "statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved statistics to {stats_file}")

    def generate_upload_instructions(self):
        """Generate instructions for uploading to Dialogflow."""
        instructions = """
# Dialogflow Upload Instructions

## Generated Files

This directory contains Dialogflow-compatible intent and entity files:

- `intents/` - Individual intent JSON files
- `intents_bulk_import.json` - Bulk import file with all intents
- `entities/` - Entity definition files
- `statistics.json` - Generation statistics

## Uploading to Dialogflow Console

### Method 1: Bulk Import (Recommended)

1. Go to [Dialogflow Console](https://dialogflow.cloud.google.com/)
2. Select your agent: **lu-assistant-bot**
3. Click the gear icon (⚙️) next to the agent name
4. Go to the **Export and Import** tab
5. Click **RESTORE FROM ZIP**
6. Upload the generated intents (you may need to zip the intents folder first)

### Method 2: Manual Intent Import

For each intent file in `intents/`:

1. Go to **Intents** in the left sidebar
2. Click **CREATE INTENT**
3. Copy the intent name from the JSON file
4. Add training phrases from the `userSays` field
5. Add responses from the `messages` field
6. Click **SAVE**

### Method 3: Using Dialogflow API (Advanced)

```python
from google.cloud import dialogflow

# Initialize client
client = dialogflow.IntentsClient()
parent = client.agent_path('lu-assistant-bot', 'global')

# Import intents
# (See Dialogflow API documentation for details)
```

## Entity Import

1. Go to **Entities** in the left sidebar
2. Click **CREATE ENTITY**
3. Use the entity name from the JSON file
4. Add entity values and synonyms from the `entries` field
5. Enable **Automated Expansion**
6. Click **SAVE**

## Testing

After uploading:

1. Use the **Try it now** panel on the right side of the console
2. Test with various queries related to Lakehead University
3. Review and refine intents based on results

## Tips

- Start with a subset of intents (e.g., FAQ intents) to test
- Monitor the **Training** section to improve intent matching
- Use the **History** tab to see actual user queries
- Regularly update intents based on user interactions

## Support

For issues or questions:
- Dialogflow Documentation: https://cloud.google.com/dialogflow/docs
- Google Cloud Support: https://cloud.google.com/support
"""

        instructions_file = self.output_dir / "UPLOAD_INSTRUCTIONS.md"
        instructions_file.write_text(instructions, encoding='utf-8')

        print(f"✓ Generated upload instructions: {instructions_file}")


def main():
    """Main entry point."""
    # Set up paths
    project_root = Path(__file__).parent.parent
    input_dir = project_root / "data" / "lakehead_scraped"
    output_dir = project_root / "data" / "dialogflow_ready"

    # Check if input directory exists
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return

    # Create generator
    generator = DialogflowIntentGenerator(input_dir, output_dir)

    # Process files (limit to 100 for initial prototype)
    generator.process_all_files(max_intents=100)

    # Save results
    generator.save_intents()

    # Generate upload instructions
    generator.generate_upload_instructions()

    print()
    print("=" * 80)
    print("Generation Complete!")
    print("=" * 80)
    print()
    print(f"Output directory: {output_dir}")
    print()
    print("Next steps:")
    print("1. Review the generated intents in the output directory")
    print("2. Follow UPLOAD_INSTRUCTIONS.md to upload to Dialogflow")
    print("3. Test the intents in the Dialogflow console")
    print()


if __name__ == "__main__":
    main()

