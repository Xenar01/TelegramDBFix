#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-Powered Mosque Data Extraction from Telegram Messages
Uses Claude Haiku to intelligently parse messy text and extract structured data
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import time
import pandas as pd

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

class AIMosqueExtractor:
    """Extract mosque data from Telegram messages using Claude AI."""

    def __init__(self, export_path: str = "MasajidChat/result.json", output_dir: str = "out_csv"):
        self.export_path = Path(export_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Initialize Claude API
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-haiku-20240307"

        # Load data
        self.messages = []
        self.provinces = {}
        self.extracted_mosques = []

        # Statistics
        self.stats = {
            'total_messages': 0,
            'messages_analyzed': 0,
            'mosques_found': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'api_calls': 0,
            'api_cost': 0.0
        }

    def load_data(self):
        """Load Telegram export and extract provinces"""
        print("📖 Loading Telegram export...")

        with open(self.export_path, encoding='utf-8') as f:
            data = json.load(f)

        self.messages = data.get('messages', [])
        self.stats['total_messages'] = len(self.messages)

        print(f"✅ Loaded {len(self.messages)} messages")

        # Extract provinces (topics)
        for msg in self.messages:
            if msg.get('action') == 'topic_created':
                topic_id = msg['id']
                title = msg.get('title', '')
                province_name = title.replace('مساجد ', '').strip()

                self.provinces[topic_id] = {
                    'id': topic_id,
                    'name': province_name,
                    'title': title
                }

        print(f"✅ Found {len(self.provinces)} provinces")

    def extract_text_content(self, text) -> str:
        """Extract text from Telegram text field (handles string and list formats)"""
        if isinstance(text, str):
            return text.strip()
        elif isinstance(text, list):
            # Handle complex text with links, mentions, etc.
            result = []
            for item in text:
                if isinstance(item, dict):
                    result.append(item.get('text', ''))
                else:
                    result.append(str(item))
            return ''.join(result).strip()
        return ''

    def get_province_by_topic(self, topic_id: int) -> Optional[Dict]:
        """Get province info by topic ID"""
        return self.provinces.get(topic_id)

    def analyze_message_with_ai(self, message: Dict, context_messages: List[Dict]) -> Optional[Dict]:
        """
        Use Claude AI to analyze a message and extract mosque data.

        Args:
            message: The message to analyze
            context_messages: Surrounding messages for context

        Returns:
            Extracted mosque data or None
        """

        # Extract text
        text = self.extract_text_content(message.get('text', ''))

        if not text or len(text) < 3:
            return None

        # Get province context
        topic_id = message.get('reply_to_message_id')
        province = self.get_province_by_topic(topic_id)
        province_name = province['name'] if province else 'غير معروف'

        # Build context from surrounding messages
        context_text = ""
        for ctx_msg in context_messages[-3:]:  # Last 3 messages
            ctx_text = self.extract_text_content(ctx_msg.get('text', ''))
            if ctx_text:
                context_text += f"\n- {ctx_text[:100]}"

        # Build prompt for Claude
        prompt = f"""أنت خبير في استخراج بيانات المساجد من رسائل تيليجرام.

**المقاطعة:** {province_name}

**الرسالة المراد تحليلها:**
{text}

**السياق (الرسائل السابقة):**
{context_text if context_text else 'لا يوجد سياق'}

**المطلوب:**
حلل هذه الرسالة واستخرج معلومات المساجد.

- هل هذه رسالة تحتوي على بيانات مسجد؟ (نعم/لا/ربما)
- إذا كانت رسالة مسجد، استخرج:
  * اسم المسجد (يجب أن يحتوي على كلمة "مسجد" أو "جامع" أو "مصلى")
  * المنطقة/الحي/القرية
  * حالة الضرر (مدمر/متضرر/تاريخي) إن وُجدت
  * أي تكاليف مذكورة
  * أي ملاحظات إضافية

- إذا كانت رسالة نقاش/تنسيق (مثل "انتهيت"، "أرسل الملفات"، "بدي الملف")، اذكر "ليست بيانات"

**الرد بصيغة JSON فقط:**
{{
  "is_mosque_data": true/false,
  "confidence": "high/medium/low",
  "mosques": [
    {{
      "name": "اسم المسجد الكامل",
      "area": "المنطقة",
      "damage_status": "destroyed/damaged/historical/unknown",
      "cost": "التكلفة إن وجدت",
      "notes": "ملاحظات"
    }}
  ],
  "reasoning": "سبب قصير للقرار"
}}

إذا كانت الرسالة تحتوي على أكثر من مسجد، أدرج كل مسجد في القائمة."""

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.1,  # Low temperature for consistent extraction
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Update statistics
            self.stats['api_calls'] += 1
            # Haiku pricing: $0.25 per 1M input tokens, $1.25 per 1M output tokens
            # Rough estimate: ~500 tokens per call
            self.stats['api_cost'] += 0.0002  # Approximate cost per call

            # Extract response
            response_text = response.content[0].text.strip()

            # Parse JSON response
            # Claude sometimes wraps JSON in code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()

            result = json.loads(response_text)

            # Validate and return
            if result.get('is_mosque_data'):
                return {
                    'source_message_id': message['id'],
                    'province': province_name,
                    'confidence': result.get('confidence', 'low'),
                    'mosques': result.get('mosques', []),
                    'reasoning': result.get('reasoning', ''),
                    'original_text': text,
                    'date': message.get('date', ''),
                    'from_user': message.get('from', '')
                }

            return None

        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse error for message {message.get('id')}: {e}")
            print(f"   Response was: {response_text[:200]}")
            return None
        except Exception as e:
            print(f"❌ API error for message {message.get('id')}: {e}")
            return None

    def extract_mosques_from_messages(self):
        """Extract mosque data from all relevant messages using AI"""
        print("\n🤖 Starting AI extraction...")
        print("="*60)

        # Filter messages containing "مسجد" or related keywords
        keywords = ['مسجد', 'جامع', 'مصلى']
        candidate_messages = []

        for msg in self.messages:
            if msg.get('type') != 'message':
                continue

            text = self.extract_text_content(msg.get('text', ''))

            if any(keyword in text for keyword in keywords):
                candidate_messages.append(msg)

        print(f"📝 Found {len(candidate_messages)} messages containing mosque keywords")
        print(f"⏳ Estimated time: ~{len(candidate_messages) * 2} seconds")
        print(f"💰 Estimated cost: ~${len(candidate_messages) * 0.0002:.2f}")
        print()

        # Process each message with AI
        for idx, msg in enumerate(candidate_messages):
            # Get context (previous messages)
            msg_index = self.messages.index(msg)
            context = self.messages[max(0, msg_index-5):msg_index]

            # Analyze with AI
            result = self.analyze_message_with_ai(msg, context)

            if result:
                # Update statistics
                self.stats['mosques_found'] += len(result['mosques'])
                confidence = result['confidence']

                if confidence == 'high':
                    self.stats['high_confidence'] += 1
                elif confidence == 'medium':
                    self.stats['medium_confidence'] += 1
                else:
                    self.stats['low_confidence'] += 1

                # Store extracted data
                self.extracted_mosques.append(result)

                # Print progress
                for mosque in result['mosques']:
                    conf_icon = "✅" if confidence == "high" else "⚠️" if confidence == "medium" else "❓"
                    print(f"{conf_icon} {mosque['name']} - {mosque.get('area', 'N/A')} ({result['province']}) [{confidence}]")

            self.stats['messages_analyzed'] += 1

            # Progress update every 50 messages
            if (idx + 1) % 50 == 0:
                progress = (idx + 1) / len(candidate_messages) * 100
                print(f"\n📊 Progress: {idx + 1}/{len(candidate_messages)} ({progress:.1f}%) - Found {self.stats['mosques_found']} mosques")

            # Rate limiting: Small delay to avoid API throttling
            time.sleep(0.1)

        print("\n" + "="*60)
        print("✅ AI extraction complete!")

    def print_statistics(self):
        """Print extraction statistics"""
        print("\n📊 EXTRACTION STATISTICS:")
        print("="*60)
        print(f"Total messages in export: {self.stats['total_messages']}")
        print(f"Messages analyzed with AI: {self.stats['messages_analyzed']}")
        print(f"Mosques extracted: {self.stats['mosques_found']}")
        print(f"\nConfidence breakdown:")
        print(f"  • High confidence: {self.stats['high_confidence']}")
        print(f"  • Medium confidence: {self.stats['medium_confidence']}")
        print(f"  • Low confidence: {self.stats['low_confidence']}")
        print(f"\nAPI Usage:")
        print(f"  • API calls made: {self.stats['api_calls']}")
        print(f"  • Estimated cost: ${self.stats['api_cost']:.2f}")

    def export_to_csv(self):
        """Export extracted data to CSV"""
        print("\n💾 Exporting to CSV...")

        # Flatten the data structure for CSV
        rows = []
        for entry in self.extracted_mosques:
            for mosque in entry['mosques']:
                row = {
                    'source': 'telegram_ai',
                    'source_message_id': entry['source_message_id'],
                    'province': entry['province'],
                    'mosque_name': mosque['name'],
                    'area': mosque.get('area', ''),
                    'damage_status': mosque.get('damage_status', 'unknown'),
                    'cost': mosque.get('cost', ''),
                    'notes': mosque.get('notes', ''),
                    'confidence': entry['confidence'],
                    'reasoning': entry['reasoning'],
                    'original_text': entry['original_text'][:200],  # Truncate for CSV
                    'date': entry['date'],
                    'from_user': entry['from_user']
                }
                rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(rows)

        # Add ID column
        df.insert(0, 'mosque_id', range(1, len(df) + 1))

        # Export
        output_file = self.output_dir / "ai_extracted_mosques.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"✅ Exported to: {output_file}")
        print(f"   Rows: {len(df)}")

        # Also export by confidence level
        high_conf = df[df['confidence'] == 'high']
        high_conf_file = self.output_dir / "ai_extracted_high_confidence.csv"
        high_conf.to_csv(high_conf_file, index=False, encoding='utf-8-sig')
        print(f"✅ High confidence mosques: {high_conf_file} ({len(high_conf)} rows)")


def main():
    """Main function"""
    print("="*60)
    print("🤖 AI-Powered Mosque Data Extraction")
    print("="*60)

    extractor = AIMosqueExtractor()

    # Load data
    extractor.load_data()

    # Extract mosques using AI
    extractor.extract_mosques_from_messages()

    # Print statistics
    extractor.print_statistics()

    # Export to CSV
    extractor.export_to_csv()

    print("\n" + "="*60)
    print("✅ Day 2 Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review: out_csv/ai_extracted_mosques.csv")
    print("2. Check high confidence: out_csv/ai_extracted_high_confidence.csv")
    print("3. Ready for Day 3: Merge with Excel data")


if __name__ == "__main__":
    main()
