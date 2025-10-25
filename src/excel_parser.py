#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel Parser - Extract complete mosque list from 20 Excel files
This creates the MASTER list with 100% coverage
"""

import pandas as pd
import json
from pathlib import Path
from typing import List, Dict
import re
import sys

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class ExcelMosqueParser:
    """Parse all Excel files to get master mosque list."""

    def __init__(self, files_dir: str = "MasajidChat/files", output_dir: str = "out_csv"):
        self.files_dir = Path(files_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Load province mapping from Telegram export
        self.province_mapping = self.load_province_mapping()

        self.mosques = []

    def load_province_mapping(self) -> Dict:
        """Load province mapping from result.json"""
        try:
            with open('MasajidChat/result.json', encoding='utf-8') as f:
                data = json.load(f)

            provinces = {}
            for msg in data.get('messages', []):
                if msg.get('action') == 'topic_created':
                    title = msg.get('title', '')
                    # Extract province name (remove "مساجد " prefix)
                    province_name = title.replace('مساجد ', '').strip()
                    provinces[province_name] = {
                        'topic_id': msg['id'],
                        'name': province_name,
                        'title': title
                    }

            return provinces
        except Exception as e:
            print(f"Warning: Could not load province mapping: {e}")
            return {}

    def extract_province_from_filename(self, filename: str) -> tuple:
        """
        Extract province name and damage type from Excel filename.

        Examples:
        - "حلب_المساجد_المدمرة_نهائي_المدينة.xlsx" → ("حلب", "demolished")
        - "دمشق المساجد المتضررة نهائي ن.xlsx" → ("دمشق", "damaged")
        """
        # Remove extension
        name = filename.replace('.xlsx', '').replace('.xls', '')

        # Determine damage type
        damage_type = 'unknown'
        if 'متضررة' in name or 'متضرر' in name:
            damage_type = 'damaged'
        elif 'مدمرة' in name or 'مدمر' in name:
            damage_type = 'demolished'

        # Extract province name (first word/phrase before المساجد)
        # Handle different formats
        if 'المساجد' in name:
            province = name.split('المساجد')[0].strip()
        elif 'مساجد' in name:
            province = name.split('مساجد')[1].strip() if name.startswith('مساجد') else name.split('مساجد')[0].strip()
        else:
            # Fallback: take first part
            province = name.split()[0] if name else 'Unknown'

        # Clean up province name
        province = province.replace('_', ' ').strip()

        return province, damage_type

    def parse_excel_file(self, file_path: Path) -> List[Dict]:
        """
        Parse a single Excel file and extract mosque data.

        Returns list of mosque dictionaries.
        """
        mosques = []

        try:
            # Extract metadata from filename
            province, damage_type = self.extract_province_from_filename(file_path.name)

            print(f"\n📄 Parsing: {file_path.name}")
            print(f"   Province: {province}, Damage: {damage_type}")

            # Read Excel file
            # Try different engines in case of compatibility issues
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
            except:
                df = pd.read_excel(file_path)

            print(f"   Columns found: {list(df.columns)}")
            print(f"   Rows: {len(df)}")

            # Detect column names (Excel files might have different column names)
            name_col = None
            area_col = None
            notes_col = None

            # Common variations for mosque name column
            name_variations = ['اسم المسجد', 'المسجد', 'الاسم', 'name', 'mosque']
            area_variations = ['المنطقة', 'الموقع', 'المدينة', 'القرية', 'area', 'location']
            notes_variations = ['ملاحظات', 'notes', 'تفاصيل']

            for col in df.columns:
                col_str = str(col).strip()
                if any(var in col_str for var in name_variations):
                    name_col = col
                elif any(var in col_str for var in area_variations):
                    area_col = col
                elif any(var in col_str for var in notes_variations):
                    notes_col = col

            # If columns not found, try first 3 columns as name, area, notes
            if name_col is None:
                name_col = df.columns[0]
                print(f"   ⚠️ Name column not found, using: {name_col}")

            if area_col is None and len(df.columns) > 1:
                area_col = df.columns[1]
                print(f"   ⚠️ Area column not found, using: {area_col}")

            # Parse rows
            for idx, row in df.iterrows():
                mosque_name = str(row[name_col]).strip() if pd.notna(row[name_col]) else None

                # Skip empty rows or headers
                if not mosque_name or mosque_name in ['nan', '', 'اسم المسجد', 'المسجد']:
                    continue

                # Extract area
                area_name = None
                if area_col:
                    area_name = str(row[area_col]).strip() if pd.notna(row[area_col]) else None
                    if area_name in ['nan', '']:
                        area_name = None

                # Extract notes
                notes = None
                if notes_col:
                    notes = str(row[notes_col]).strip() if pd.notna(row[notes_col]) else None
                    if notes in ['nan', '']:
                        notes = None

                mosque = {
                    'source': 'excel',
                    'excel_file': file_path.name,
                    'province': province,
                    'damage_type': damage_type,
                    'mosque_name': mosque_name,
                    'area': area_name,
                    'notes': notes,
                    'row_number': idx + 1
                }

                mosques.append(mosque)

            print(f"   ✅ Extracted {len(mosques)} mosques")

        except Exception as e:
            print(f"   ❌ Error parsing {file_path.name}: {e}")

        return mosques

    def parse_all_excel_files(self):
        """Parse all Excel files in the directory."""
        print("🚀 Starting Excel Parser\n")
        print("="*60)

        # Find all Excel files
        excel_files = list(self.files_dir.glob("*.xlsx")) + list(self.files_dir.glob("*.xls"))

        print(f"Found {len(excel_files)} Excel files\n")

        # Parse each file
        for file_path in sorted(excel_files):
            mosques = self.parse_excel_file(file_path)
            self.mosques.extend(mosques)

        print("\n" + "="*60)
        print(f"\n✅ TOTAL MOSQUES EXTRACTED: {len(self.mosques)}")

        # Statistics
        self.print_statistics()

    def print_statistics(self):
        """Print extraction statistics."""
        print("\n📊 STATISTICS:")
        print("="*60)

        # By province
        provinces = {}
        for m in self.mosques:
            prov = m['province']
            if prov not in provinces:
                provinces[prov] = {'damaged': 0, 'demolished': 0, 'total': 0}
            provinces[prov][m['damage_type']] += 1
            provinces[prov]['total'] += 1

        print("\nMosques by Province:")
        for prov, counts in sorted(provinces.items()):
            print(f"  • {prov}: {counts['total']} total "
                  f"({counts['damaged']} damaged, {counts['demolished']} demolished)")

        # Overall damage type
        damaged = sum(1 for m in self.mosques if m['damage_type'] == 'damaged')
        demolished = sum(1 for m in self.mosques if m['damage_type'] == 'demolished')

        print(f"\nOverall Damage Distribution:")
        print(f"  • Damaged (متضررة): {damaged}")
        print(f"  • Demolished (مدمرة): {demolished}")

        # Mosques with/without area
        with_area = sum(1 for m in self.mosques if m['area'])
        print(f"\nData Completeness:")
        print(f"  • With area info: {with_area}/{len(self.mosques)} ({with_area/len(self.mosques)*100:.1f}%)")

    def export_to_csv(self):
        """Export extracted mosques to CSV."""
        output_file = self.output_dir / "excel_mosques_master.csv"

        # Convert to DataFrame
        df = pd.DataFrame(self.mosques)

        # Add ID column
        df.insert(0, 'mosque_id', range(1, len(df) + 1))

        # Reorder columns
        columns = ['mosque_id', 'province', 'mosque_name', 'area', 'damage_type',
                   'excel_file', 'row_number', 'notes', 'source']
        df = df[columns]

        # Export
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"\n💾 Exported to: {output_file}")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {len(df.columns)}")

        # Also export summary
        summary_file = self.output_dir / "excel_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Excel Parsing Summary\n")
            f.write(f"="*60 + "\n\n")
            f.write(f"Total Mosques: {len(self.mosques)}\n\n")

            # Province breakdown
            provinces = {}
            for m in self.mosques:
                prov = m['province']
                provinces[prov] = provinces.get(prov, 0) + 1

            f.write("Mosques by Province:\n")
            for prov, count in sorted(provinces.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {prov}: {count}\n")

        print(f"💾 Summary exported to: {summary_file}")


def main():
    """Main function"""
    parser = ExcelMosqueParser()
    parser.parse_all_excel_files()
    parser.export_to_csv()

    print("\n" + "="*60)
    print("✅ Excel parsing complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review: out_csv/excel_mosques_master.csv")
    print("2. Check: out_csv/excel_summary.txt")
    print("3. Ready for Day 2: AI extraction from Telegram")


if __name__ == "__main__":
    main()
