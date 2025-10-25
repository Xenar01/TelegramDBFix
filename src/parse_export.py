#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Export Parser for Mosque Reconstruction Project
Extracts mosque data from Telegram JSON export and organizes it into structured CSV files.
"""

import json
import csv
import os
import re
import shutil
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class TelegramMosqueParser:
    """Parse Telegram export and extract mosque reconstruction data."""

    def __init__(self, export_path: str, output_dir: str = "out_csv"):
        self.export_path = Path(export_path)
        self.output_dir = Path(output_dir)
        self.media_dir = Path("media_organized")

        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        self.media_dir.mkdir(exist_ok=True)

        # Data structures
        self.provinces = {}  # topic_id -> province_info
        self.mosques = []
        self.photos = []
        self.locations = []
        self.excel_files = []
        self.message_index = []

        print(f"📂 Initialized parser for: {self.export_path}")

    def load_export(self) -> dict:
        """Load the Telegram JSON export."""
        json_file = self.export_path / "result.json"
        print(f"📖 Loading {json_file}...")

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"✅ Loaded {len(data.get('messages', []))} messages")
        return data

    def extract_provinces(self, messages: List[dict]) -> Dict[int, dict]:
        """Extract province topics from service messages."""
        provinces = {}

        for msg in messages:
            if msg.get('type') == 'service' and msg.get('action') == 'topic_created':
                topic_id = msg['id']
                title = msg.get('title', '')

                # Extract province name (remove "مساجد" prefix)
                province_name = title.replace('مساجد ', '').strip()

                provinces[topic_id] = {
                    'id': len(provinces) + 1,
                    'topic_id': topic_id,
                    'name_ar': province_name,
                    'topic_title': title,
                    'created_at': msg.get('date', '')
                }

                print(f"📍 Found province: {province_name} (Topic ID: {topic_id})")

        self.provinces = provinces
        return provinces

    def get_province_by_topic(self, reply_to_id: int) -> Optional[dict]:
        """Get province info by topic reply ID."""
        return self.provinces.get(reply_to_id)

    def extract_text_content(self, text_field) -> str:
        """Extract text from Telegram's text field (can be string or list of objects)."""
        if isinstance(text_field, str):
            return text_field
        elif isinstance(text_field, list):
            return ' '.join(item.get('text', '') for item in text_field if isinstance(item, dict))
        return ''

    def is_google_maps_link(self, text: str) -> bool:
        """Check if text contains a Google Maps link."""
        maps_patterns = [
            r'maps\.google\.com',
            r'goo\.gl',
            r'maps\.app\.goo\.gl'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in maps_patterns)

    def extract_mosque_name_area(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract mosque name and area from text.
        Expected format:
        Line 1: مسجد [Name]
        Line 2: [Area]
        """
        lines = text.strip().split('\n')

        if len(lines) >= 2:
            mosque_name = lines[0].strip()
            area_name = lines[1].strip()
            return mosque_name, area_name
        elif len(lines) == 1 and 'مسجد' in lines[0]:
            return lines[0].strip(), None

        return None, None

    def group_mosque_messages(self, messages: List[dict]) -> List[dict]:
        """
        Group messages into mosque entries.
        Pattern: Photos -> Text (name+area) -> Maps link
        """
        mosques = []
        i = 0

        while i < len(messages):
            msg = messages[i]

            # Skip service messages and messages without topic
            if msg.get('type') != 'message' or not msg.get('reply_to_message_id'):
                i += 1
                continue

            topic_id = msg.get('reply_to_message_id')
            province = self.get_province_by_topic(topic_id)

            if not province:
                i += 1
                continue

            # Check if this is a text message with mosque name
            text = self.extract_text_content(msg.get('text', ''))
            mosque_name, area_name = self.extract_mosque_name_area(text)

            if mosque_name and area_name:
                # Found a mosque entry! Look for photos before this message
                photos = []
                j = i - 1

                # Collect photos that came just before this text message
                while j >= 0 and j > i - 20:  # Look back max 20 messages
                    prev_msg = messages[j]

                    # Same topic and has photo
                    if (prev_msg.get('reply_to_message_id') == topic_id and
                        prev_msg.get('mime_type', '').startswith('image/')):
                        photos.insert(0, prev_msg)
                        j -= 1
                    elif prev_msg.get('reply_to_message_id') == topic_id and prev_msg.get('text'):
                        # Hit another text message in same topic, stop
                        break
                    else:
                        j -= 1

                # Look for Google Maps link after this message
                maps_link = None
                if i + 1 < len(messages):
                    next_msg = messages[i + 1]
                    next_text = self.extract_text_content(next_msg.get('text', ''))

                    if (next_msg.get('reply_to_message_id') == topic_id and
                        self.is_google_maps_link(next_text)):
                        maps_link = next_text.strip()

                # Create mosque entry
                mosque_entry = {
                    'mosque_id': len(mosques) + 1,
                    'province_id': province['id'],
                    'province_name': province['name_ar'],
                    'mosque_name': mosque_name,
                    'area_name': area_name,
                    'photos': photos,
                    'maps_link': maps_link,
                    'source_message_id': msg['id'],
                    'date': msg.get('date', ''),
                    'from_user': msg.get('from', '')
                }

                mosques.append(mosque_entry)
                print(f"🕌 Found mosque: {mosque_name} - {area_name} ({province['name_ar']}) with {len(photos)} photos")

            i += 1

        return mosques

    def extract_excel_files(self, messages: List[dict]) -> List[dict]:
        """Extract Excel file attachments and categorize them."""
        excel_files = []

        for msg in messages:
            if msg.get('type') != 'message':
                continue

            file_name = msg.get('file_name', '')
            mime_type = msg.get('mime_type', '')

            # Check if it's an Excel file
            if 'spreadsheet' in mime_type or file_name.endswith(('.xlsx', '.xls')):
                topic_id = msg.get('reply_to_message_id')
                province = self.get_province_by_topic(topic_id)

                # Determine damage type from filename
                damage_type = 'unknown'
                if 'متضررة' in file_name or 'متضرر' in file_name:
                    damage_type = 'damaged'
                elif 'مدمرة' in file_name or 'مدمر' in file_name:
                    damage_type = 'demolished'

                excel_entry = {
                    'file_id': len(excel_files) + 1,
                    'file_name': file_name,
                    'file_path': msg.get('file', ''),
                    'file_size': msg.get('file_size', 0),
                    'province_id': province['id'] if province else None,
                    'province_name': province['name_ar'] if province else 'Unknown',
                    'damage_type': damage_type,
                    'message_id': msg['id'],
                    'date': msg.get('date', ''),
                }

                excel_files.append(excel_entry)
                print(f"📊 Found Excel: {file_name} ({damage_type}) - {province['name_ar'] if province else 'Unknown'}")

        return excel_files

    def organize_media_files(self):
        """Copy and organize media files by province and mosque."""
        print("\n📁 Organizing media files...")

        for mosque in self.mosques:
            province_name = mosque['province_name']
            mosque_name = re.sub(r'[^\w\s-]', '', mosque['mosque_name'])[:50]  # Clean name

            # Create province/mosque directory
            mosque_dir = self.media_dir / province_name / mosque_name
            mosque_dir.mkdir(parents=True, exist_ok=True)

            # Copy photos
            for idx, photo in enumerate(mosque['photos'], 1):
                src_path = self.export_path / photo.get('file', '')
                if src_path.exists():
                    ext = src_path.suffix
                    dst_path = mosque_dir / f"photo_{idx}{ext}"
                    shutil.copy2(src_path, dst_path)

        print(f"✅ Media organized in {self.media_dir}/")

    def export_to_csv(self):
        """Export all data to CSV files."""
        print("\n💾 Exporting to CSV...")

        # 1. Provinces
        with open(self.output_dir / 'provinces.csv', 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'topic_id', 'name_ar', 'topic_title', 'created_at'])
            writer.writeheader()
            writer.writerows(self.provinces.values())

        # 2. Mosques
        with open(self.output_dir / 'mosques.csv', 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['mosque_id', 'province_id', 'province_name', 'mosque_name', 'area_name',
                         'source_message_id', 'date', 'from_user', 'photo_count']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for mosque in self.mosques:
                row = {k: v for k, v in mosque.items() if k in fieldnames}
                row['photo_count'] = len(mosque.get('photos', []))
                writer.writerow(row)

        # 3. Locations
        with open(self.output_dir / 'locations.csv', 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['mosque_id', 'province_name', 'mosque_name', 'area_name', 'gmaps_url']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for mosque in self.mosques:
                if mosque.get('maps_link'):
                    writer.writerow({
                        'mosque_id': mosque['mosque_id'],
                        'province_name': mosque['province_name'],
                        'mosque_name': mosque['mosque_name'],
                        'area_name': mosque['area_name'],
                        'gmaps_url': mosque['maps_link']
                    })

        # 4. Photos
        with open(self.output_dir / 'photos.csv', 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['photo_id', 'mosque_id', 'province_name', 'mosque_name', 'file_path',
                         'file_name', 'file_size', 'message_id']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            photo_id = 1
            for mosque in self.mosques:
                for photo in mosque.get('photos', []):
                    writer.writerow({
                        'photo_id': photo_id,
                        'mosque_id': mosque['mosque_id'],
                        'province_name': mosque['province_name'],
                        'mosque_name': mosque['mosque_name'],
                        'file_path': photo.get('file', ''),
                        'file_name': photo.get('file_name', ''),
                        'file_size': photo.get('file_size', 0),
                        'message_id': photo['id']
                    })
                    photo_id += 1

        # 5. Excel Files
        with open(self.output_dir / 'excel_files.csv', 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['file_id', 'province_id', 'province_name', 'damage_type',
                         'file_name', 'file_path', 'file_size', 'message_id', 'date']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.excel_files)

        print(f"✅ CSV files exported to {self.output_dir}/")

    def generate_summary(self):
        """Generate a summary report."""
        print("\n" + "="*60)
        print("📊 EXTRACTION SUMMARY")
        print("="*60)
        print(f"Provinces: {len(self.provinces)}")
        print(f"Mosques: {len(self.mosques)}")
        print(f"Photos: {sum(len(m.get('photos', [])) for m in self.mosques)}")
        print(f"Locations (with maps): {sum(1 for m in self.mosques if m.get('maps_link'))}")
        print(f"Excel files: {len(self.excel_files)}")

        print("\n📍 Mosques by Province:")
        province_counts = defaultdict(int)
        for mosque in self.mosques:
            province_counts[mosque['province_name']] += 1

        for province, count in sorted(province_counts.items()):
            print(f"  • {province}: {count} mosques")

        print("\n📊 Excel Files by Type:")
        damage_counts = defaultdict(int)
        for excel in self.excel_files:
            damage_counts[excel['damage_type']] += 1

        for damage_type, count in damage_counts.items():
            print(f"  • {damage_type}: {count} files")

        print("="*60)

    def run(self, organize_media: bool = True):
        """Run the full ETL pipeline."""
        print("\n🚀 Starting Telegram Mosque Export Parser\n")

        # Load data
        data = self.load_export()
        messages = data.get('messages', [])

        # Extract provinces (topics)
        print("\n1️⃣ Extracting provinces...")
        self.extract_provinces(messages)

        # Extract mosques
        print("\n2️⃣ Extracting mosques...")
        self.mosques = self.group_mosque_messages(messages)

        # Extract Excel files
        print("\n3️⃣ Extracting Excel files...")
        self.excel_files = self.extract_excel_files(messages)

        # Organize media
        if organize_media:
            print("\n4️⃣ Organizing media files...")
            self.organize_media_files()

        # Export to CSV
        print("\n5️⃣ Exporting to CSV...")
        self.export_to_csv()

        # Generate summary
        self.generate_summary()

        print("\n✅ ETL Pipeline completed successfully!\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Parse Telegram mosque reconstruction export')
    parser.add_argument('--export-path', default='MasajidChat',
                       help='Path to Telegram export directory')
    parser.add_argument('--output-dir', default='out_csv',
                       help='Output directory for CSV files')
    parser.add_argument('--no-media', action='store_true',
                       help='Skip media file organization')

    args = parser.parse_args()

    # Run parser
    parser = TelegramMosqueParser(args.export_path, args.output_dir)
    parser.run(organize_media=not args.no_media)


if __name__ == '__main__':
    main()
