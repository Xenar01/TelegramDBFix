#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 3: Merge Excel and AI Extracted Data
========================================
Combines the two data sources, deduplicates, and creates master mosque database.

Strategy:
1. Excel data is the "ground truth" (598 mosques from official files)
2. AI data adds additional mosques not in Excel (461 mosques from Telegram)
3. Use fuzzy matching to detect duplicates
4. Create master CSV with source tracking
"""

import sys
import os
from pathlib import Path
import pandas as pd
from difflib import SequenceMatcher
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class MosqueMerger:
    """Merge Excel and AI extracted mosque data with deduplication."""

    def __init__(self, excel_path: str, ai_path: str, output_dir: str = "out_csv"):
        self.excel_path = Path(excel_path)
        self.ai_path = Path(ai_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.excel_df = None
        self.ai_df = None
        self.merged_df = None

        print("=" * 60)
        print("🔗 Mosque Data Merger - Day 3")
        print("=" * 60)

    def load_data(self):
        """Load Excel and AI extracted data."""
        print("\n📖 Loading data sources...")

        # Load Excel data
        self.excel_df = pd.read_csv(self.excel_path, encoding='utf-8')
        print(f"✅ Excel data: {len(self.excel_df)} mosques")

        # Load AI data
        self.ai_df = pd.read_csv(self.ai_path, encoding='utf-8')
        print(f"✅ AI data: {len(self.ai_df)} mosques")

        # Show columns
        print(f"\n📋 Excel columns: {list(self.excel_df.columns)}")
        print(f"📋 AI columns: {list(self.ai_df.columns)}")

    def normalize_text(self, text: str) -> str:
        """Normalize Arabic text for comparison."""
        if pd.isna(text) or text == '':
            return ''

        text = str(text).strip()

        # Remove common mosque prefixes for matching
        text = re.sub(r'^(مسجد|جامع|مصلى)\s+', '', text)

        # Normalize Arabic characters
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه')
        text = text.replace('ى', 'ي')

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text.lower()

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two strings."""
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)

        if not norm1 or not norm2:
            return 0.0

        return SequenceMatcher(None, norm1, norm2).ratio()

    def find_duplicates(self, excel_row, ai_df, threshold: float = 0.85):
        """
        Find potential duplicate in AI data for a given Excel row.

        Matching criteria:
        1. Same province
        2. Similar mosque name (> threshold)
        3. Similar area if available
        """
        province = excel_row['province']
        name = excel_row['mosque_name']
        area = excel_row.get('area', '')

        # Filter AI data by province
        province_matches = ai_df[ai_df['province'] == province]

        if len(province_matches) == 0:
            return None

        best_match = None
        best_score = 0.0

        for idx, ai_row in province_matches.iterrows():
            # Calculate name similarity
            name_sim = self.calculate_similarity(name, ai_row['mosque_name'])

            # Calculate area similarity if both have area
            area_sim = 0.0
            if area and pd.notna(ai_row.get('area')):
                area_sim = self.calculate_similarity(area, ai_row['area'])

            # Combined score (name is more important)
            score = name_sim * 0.7 + area_sim * 0.3

            if score > best_score and score >= threshold:
                best_score = score
                best_match = (idx, ai_row, score)

        return best_match

    def merge_datasets(self, similarity_threshold: float = 0.85):
        """
        Merge Excel and AI data with deduplication.

        Process:
        1. Start with all Excel mosques (ground truth)
        2. For each AI mosque, check if it's a duplicate of Excel
        3. If not duplicate, add as new mosque
        4. Track source and merge quality
        """
        print(f"\n🔗 Merging datasets (similarity threshold: {similarity_threshold})...")

        merged_records = []
        ai_matched_indices = set()

        # Process Excel data first (ground truth)
        for idx, excel_row in self.excel_df.iterrows():
            record = {
                'mosque_id': f"EXL_{idx+1:04d}",
                'mosque_name': excel_row['mosque_name'],
                'area': excel_row.get('area', ''),
                'province': excel_row['province'],
                'damage_type': excel_row.get('damage_type', 'unknown'),
                'source': 'excel',
                'excel_source': excel_row.get('excel_source', ''),
                'telegram_msg_id': None,
                'confidence': 'high',
                'merge_notes': 'From Excel master list'
            }

            # Try to find matching AI data to enrich
            match = self.find_duplicates(excel_row, self.ai_df, similarity_threshold)

            if match:
                match_idx, ai_row, score = match
                ai_matched_indices.add(match_idx)

                # Enrich with AI data
                record['telegram_msg_id'] = ai_row.get('source_message_id')
                record['source'] = 'excel+ai'
                record['merge_notes'] = f'Matched with AI data (similarity: {score:.2%})'

                # Use AI area if Excel missing
                if not record['area'] and pd.notna(ai_row.get('area')):
                    record['area'] = ai_row['area']

                # Use AI damage type if Excel unknown
                if record['damage_type'] == 'unknown' and pd.notna(ai_row.get('damage_type')):
                    record['damage_type'] = ai_row['damage_type']

            merged_records.append(record)

        print(f"✅ Processed {len(merged_records)} Excel mosques")
        print(f"✅ Matched {len(ai_matched_indices)} with AI data")

        # Add unmatched AI mosques (new discoveries)
        ai_only_count = 0
        for idx, ai_row in self.ai_df.iterrows():
            if idx not in ai_matched_indices:
                # Skip low confidence AI extractions
                if ai_row.get('confidence', '').lower() == 'low':
                    continue

                record = {
                    'mosque_id': f"AI_{idx+1:04d}",
                    'mosque_name': ai_row['mosque_name'],
                    'area': ai_row.get('area', ''),
                    'province': ai_row['province'],
                    'damage_type': ai_row.get('damage_type', 'unknown'),
                    'source': 'ai_only',
                    'excel_source': '',
                    'telegram_msg_id': ai_row.get('source_message_id'),
                    'confidence': ai_row.get('confidence', 'medium'),
                    'merge_notes': 'AI extraction only (not in Excel)'
                }
                merged_records.append(record)
                ai_only_count += 1

        print(f"✅ Added {ai_only_count} AI-only mosques")

        # Create DataFrame
        self.merged_df = pd.DataFrame(merged_records)

        print(f"\n📊 MERGE COMPLETE:")
        print(f"   Total mosques: {len(self.merged_df)}")
        print(f"   Excel only: {len(self.merged_df[self.merged_df['source'] == 'excel'])}")
        print(f"   Excel+AI: {len(self.merged_df[self.merged_df['source'] == 'excel+ai'])}")
        print(f"   AI only: {len(self.merged_df[self.merged_df['source'] == 'ai_only'])}")

    def export_results(self):
        """Export merged data to CSV."""
        print("\n💾 Exporting merged data...")

        # Main merged file
        output_path = self.output_dir / "mosques_merged_master.csv"
        self.merged_df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"✅ Master file: {output_path} ({len(self.merged_df)} rows)")

        # Statistics by province
        province_stats = self.merged_df.groupby('province').agg({
            'mosque_id': 'count',
            'source': lambda x: (x == 'excel').sum(),  # Excel count
        }).rename(columns={'mosque_id': 'total', 'source': 'excel_count'})

        province_stats['ai_only_count'] = self.merged_df[
            self.merged_df['source'] == 'ai_only'
        ].groupby('province').size()
        province_stats['ai_only_count'] = province_stats['ai_only_count'].fillna(0).astype(int)

        province_stats_path = self.output_dir / "merge_stats_by_province.csv"
        province_stats.to_csv(province_stats_path, encoding='utf-8')
        print(f"✅ Province stats: {province_stats_path}")

        # High confidence subset (for immediate use)
        high_conf = self.merged_df[
            (self.merged_df['source'].isin(['excel', 'excel+ai'])) |
            (self.merged_df['confidence'] == 'high')
        ]
        high_conf_path = self.output_dir / "mosques_high_confidence.csv"
        high_conf.to_csv(high_conf_path, index=False, encoding='utf-8')
        print(f"✅ High confidence: {high_conf_path} ({len(high_conf)} rows)")

        # Summary report
        summary_path = self.output_dir / "merge_summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("MOSQUE DATA MERGE SUMMARY - Day 3\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Input Sources:\n")
            f.write(f"  • Excel mosques: {len(self.excel_df)}\n")
            f.write(f"  • AI extracted: {len(self.ai_df)}\n\n")

            f.write(f"Merge Results:\n")
            f.write(f"  • Total unique mosques: {len(self.merged_df)}\n")
            f.write(f"  • Excel only: {len(self.merged_df[self.merged_df['source'] == 'excel'])}\n")
            f.write(f"  • Excel+AI matched: {len(self.merged_df[self.merged_df['source'] == 'excel+ai'])}\n")
            f.write(f"  • AI only: {len(self.merged_df[self.merged_df['source'] == 'ai_only'])}\n")
            f.write(f"  • High confidence: {len(high_conf)}\n\n")

            f.write(f"By Province:\n")
            for province, stats in province_stats.iterrows():
                f.write(f"  • {province}: {int(stats['total'])} mosques ")
                f.write(f"({int(stats['excel_count'])} Excel, {int(stats['ai_only_count'])} AI-only)\n")

            f.write(f"\nDamage Type Distribution:\n")
            damage_counts = self.merged_df['damage_type'].value_counts()
            for dtype, count in damage_counts.items():
                f.write(f"  • {dtype}: {count}\n")

            f.write(f"\nOutput Files:\n")
            f.write(f"  • mosques_merged_master.csv - All mosques\n")
            f.write(f"  • mosques_high_confidence.csv - Vetted subset\n")
            f.write(f"  • merge_stats_by_province.csv - Province statistics\n")

        print(f"✅ Summary report: {summary_path}")

    def run(self):
        """Execute the full merge process."""
        self.load_data()
        self.merge_datasets(similarity_threshold=0.85)
        self.export_results()

        print("\n" + "=" * 60)
        print("✅ Day 3 Complete - Data Merged Successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review: out_csv/mosques_merged_master.csv")
        print("2. Check: out_csv/merge_summary.txt")
        print("3. Ready for Day 4: Photo/Maps matching")


if __name__ == "__main__":
    merger = MosqueMerger(
        excel_path="out_csv/excel_mosques_master.csv",
        ai_path="out_csv/ai_extracted_mosques.csv",
        output_dir="out_csv"
    )
    merger.run()
