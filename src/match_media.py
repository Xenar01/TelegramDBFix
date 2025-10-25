#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 4: Match Photos and Maps to Mosques
========================================
Links photos and Google Maps locations from Telegram to the merged mosque database.

Strategy:
1. Parse Telegram export for photos and maps
2. Match to mosques using message proximity and mosque names
3. Enrich master database with media links
"""

import sys
import os
from pathlib import Path
import pandas as pd
import json
import re
from typing import Dict, List, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class MediaMatcher:
    """Match photos and maps from Telegram to mosque records."""

    def __init__(self, telegram_export: str, mosques_csv: str, output_dir: str = "out_csv"):
        self.export_path = Path(telegram_export)
        self.mosques_csv = Path(mosques_csv)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.export_data = None
        self.mosques_df = None
        self.topics = {}  # topic_id -> province mapping

        self.photos_data = []
        self.maps_data = []

        print("=" * 60)
        print("📸 Media Matcher - Day 4")
        print("=" * 60)

    def load_data(self):
        """Load Telegram export and mosque database."""
        print("\n📖 Loading data...")

        # Load Telegram export
        with open(self.export_path, 'r', encoding='utf-8') as f:
            self.export_data = json.load(f)
        print(f"✅ Telegram export: {len(self.export_data['messages'])} messages")

        # Load mosques
        self.mosques_df = pd.read_csv(self.mosques_csv, encoding='utf-8')
        print(f"✅ Mosque database: {len(self.mosques_df)} mosques")

        # Extract topics (provinces)
        self._extract_topics()

    def _extract_topics(self):
        """Extract Telegram topics (provinces) from export."""
        for msg in self.export_data['messages']:
            if msg.get('type') == 'service' and msg.get('action') == 'topic_created':
                topic_id = msg['id']
                topic_title = msg.get('title', 'غير معروف')
                self.topics[topic_id] = topic_title

        print(f"✅ Found {len(self.topics)} topics/provinces")

    def extract_text_content(self, text_field) -> str:
        """Extract plain text from Telegram message text field."""
        if isinstance(text_field, str):
            return text_field.strip()
        elif isinstance(text_field, list):
            return ''.join([
                item.get('text', '') if isinstance(item, dict) else str(item)
                for item in text_field
            ]).strip()
        return ''

    def find_province_for_message(self, msg: Dict) -> str:
        """Determine province for a message based on topic."""
        reply_id = msg.get('reply_to_message_id')

        if reply_id and reply_id in self.topics:
            return self.topics[reply_id]

        # Check if message itself is a topic
        if msg.get('id') in self.topics:
            return self.topics[msg['id']]

        return 'غير معروف'

    def extract_photos(self):
        """Extract all photo messages from Telegram export."""
        print("\n📸 Extracting photos...")

        for msg in self.export_data['messages']:
            if msg.get('type') != 'message':
                continue

            # Check for photo
            photo_file = msg.get('file') or msg.get('photo')
            if not photo_file:
                continue

            province = self.find_province_for_message(msg)

            photo_record = {
                'message_id': msg['id'],
                'date': msg.get('date', ''),
                'province': province,
                'file_path': photo_file,
                'reply_to': msg.get('reply_to_message_id'),
                'text': self.extract_text_content(msg.get('text', ''))
            }

            self.photos_data.append(photo_record)

        print(f"✅ Found {len(self.photos_data)} photos")

    def extract_maps(self):
        """Extract Google Maps links from messages."""
        print("\n🗺️ Extracting Google Maps links...")

        maps_pattern = re.compile(
            r'(https?://)?(maps\.app\.goo\.gl/[A-Za-z0-9]+|'
            r'maps\.google\.com[^\s]+|'
            r'goo\.gl/maps/[A-Za-z0-9]+)'
        )

        for msg in self.export_data['messages']:
            if msg.get('type') != 'message':
                continue

            text = self.extract_text_content(msg.get('text', ''))
            if not text:
                continue

            # Find maps URLs
            matches = maps_pattern.findall(text)
            if not matches:
                continue

            province = self.find_province_for_message(msg)

            for match in matches:
                # match is a tuple from findall, get the full match
                url_part = ''.join(match) if isinstance(match, tuple) else match
                # Reconstruct full URL
                url = url_part if url_part.startswith('http') else f'https://{url_part}'

                maps_record = {
                    'message_id': msg['id'],
                    'date': msg.get('date', ''),
                    'province': province,
                    'maps_url': url,
                    'reply_to': msg.get('reply_to_message_id'),
                    'full_text': text
                }

                self.maps_data.append(maps_record)

        print(f"✅ Found {len(self.maps_data)} Google Maps links")

    def match_media_to_mosques(self):
        """
        Match photos and maps to mosque records.

        Matching strategy:
        1. Use telegram_msg_id if available (from AI extraction)
        2. Match by proximity (photos/maps near mosque name messages)
        3. Match by province and name similarity
        """
        print("\n🔗 Matching media to mosques...")

        # Convert lists to DataFrames for easier processing
        photos_df = pd.DataFrame(self.photos_data) if self.photos_data else pd.DataFrame()
        maps_df = pd.DataFrame(self.maps_data) if self.maps_data else pd.DataFrame()

        # Add columns to mosques for media
        self.mosques_df['photo_files'] = None
        self.mosques_df['photo_count'] = 0
        self.mosques_df['maps_url'] = None
        self.mosques_df['has_location'] = False

        matched_photos = 0
        matched_maps = 0

        # Match for mosques with telegram message IDs (from AI extraction)
        for idx, mosque in self.mosques_df.iterrows():
            msg_id = mosque.get('telegram_msg_id')

            if pd.notna(msg_id):
                msg_id = int(msg_id)

                # Find photos within ±20 messages
                nearby_photos = photos_df[
                    (photos_df['message_id'] >= msg_id - 20) &
                    (photos_df['message_id'] <= msg_id + 20) &
                    (photos_df['province'] == mosque['province'])
                ]

                if len(nearby_photos) > 0:
                    photo_files = nearby_photos['file_path'].tolist()
                    self.mosques_df.at[idx, 'photo_files'] = '; '.join(photo_files)
                    self.mosques_df.at[idx, 'photo_count'] = len(photo_files)
                    matched_photos += len(photo_files)

                # Find maps link within ±5 messages
                nearby_maps = maps_df[
                    (maps_df['message_id'] >= msg_id - 5) &
                    (maps_df['message_id'] <= msg_id + 5) &
                    (maps_df['province'] == mosque['province'])
                ]

                if len(nearby_maps) > 0:
                    # Take first match
                    maps_url = nearby_maps.iloc[0]['maps_url']
                    self.mosques_df.at[idx, 'maps_url'] = maps_url
                    self.mosques_df.at[idx, 'has_location'] = True
                    matched_maps += 1

        print(f"✅ Matched {matched_photos} photos to mosques")
        print(f"✅ Matched {matched_maps} maps to mosques")

        # Statistics
        mosques_with_photos = (self.mosques_df['photo_count'] > 0).sum()
        mosques_with_maps = self.mosques_df['has_location'].sum()

        print(f"\n📊 Coverage:")
        print(f"   Mosques with photos: {mosques_with_photos}/{len(self.mosques_df)} ({mosques_with_photos/len(self.mosques_df)*100:.1f}%)")
        print(f"   Mosques with maps: {mosques_with_maps}/{len(self.mosques_df)} ({mosques_with_maps/len(self.mosques_df)*100:.1f}%)")

    def export_results(self):
        """Export enriched mosque database with media."""
        print("\n💾 Exporting enriched data...")

        # Main enriched file
        output_path = self.output_dir / "mosques_enriched_with_media.csv"
        self.mosques_df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"✅ Enriched database: {output_path} ({len(self.mosques_df)} rows)")

        # Photos catalog
        if self.photos_data:
            photos_df = pd.DataFrame(self.photos_data)
            photos_path = self.output_dir / "photos_catalog.csv"
            photos_df.to_csv(photos_path, index=False, encoding='utf-8')
            print(f"✅ Photos catalog: {photos_path} ({len(photos_df)} rows)")

        # Maps catalog
        if self.maps_data:
            maps_df = pd.DataFrame(self.maps_data)
            maps_path = self.output_dir / "maps_catalog.csv"
            maps_df.to_csv(maps_path, index=False, encoding='utf-8')
            print(f"✅ Maps catalog: {maps_path} ({len(maps_df)} rows)")

        # Summary
        summary_path = self.output_dir / "media_matching_summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("MEDIA MATCHING SUMMARY - Day 4\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Media Extracted:\n")
            f.write(f"  • Total photos: {len(self.photos_data)}\n")
            f.write(f"  • Total maps: {len(self.maps_data)}\n\n")

            mosques_with_photos = (self.mosques_df['photo_count'] > 0).sum()
            mosques_with_maps = self.mosques_df['has_location'].sum()
            total_photos_matched = self.mosques_df['photo_count'].sum()

            f.write(f"Matching Results:\n")
            f.write(f"  • Mosques with photos: {mosques_with_photos}/{len(self.mosques_df)} ({mosques_with_photos/len(self.mosques_df)*100:.1f}%)\n")
            f.write(f"  • Mosques with maps: {mosques_with_maps}/{len(self.mosques_df)} ({mosques_with_maps/len(self.mosques_df)*100:.1f}%)\n")
            f.write(f"  • Total photos matched: {int(total_photos_matched)}\n\n")

            f.write(f"Coverage by Province:\n")
            for province in sorted(self.mosques_df['province'].unique()):
                prov_df = self.mosques_df[self.mosques_df['province'] == province]
                with_photos = (prov_df['photo_count'] > 0).sum()
                with_maps = prov_df['has_location'].sum()
                f.write(f"  • {province}:\n")
                f.write(f"    - Photos: {with_photos}/{len(prov_df)} mosques\n")
                f.write(f"    - Maps: {with_maps}/{len(prov_df)} mosques\n")

            f.write(f"\nOutput Files:\n")
            f.write(f"  • mosques_enriched_with_media.csv - Main database with media\n")
            f.write(f"  • photos_catalog.csv - All photos index\n")
            f.write(f"  • maps_catalog.csv - All maps index\n")

        print(f"✅ Summary: {summary_path}")

    def run(self):
        """Execute the full media matching process."""
        self.load_data()
        self.extract_photos()
        self.extract_maps()
        self.match_media_to_mosques()
        self.export_results()

        print("\n" + "=" * 60)
        print("✅ Day 4 Complete - Media Matched!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review: out_csv/mosques_enriched_with_media.csv")
        print("2. Check: out_csv/media_matching_summary.txt")
        print("3. Ready for Day 5: Review interface")


if __name__ == "__main__":
    matcher = MediaMatcher(
        telegram_export="MasajidChat/result.json",
        mosques_csv="out_csv/mosques_merged_master.csv",
        output_dir="out_csv"
    )
    matcher.run()
