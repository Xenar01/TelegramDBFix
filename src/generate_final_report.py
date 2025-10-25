#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 5: Generate Final Reports and Database Summary
===================================================
Creates comprehensive reports and statistics for the complete V1 database.
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class FinalReportGenerator:
    """Generate comprehensive final reports for V1 database."""

    def __init__(self, mosques_csv: str, output_dir: str = "out_csv"):
        self.mosques_csv = Path(mosques_csv)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.df = None

        print("=" * 70)
        print("📊 FINAL REPORT GENERATOR - Day 5")
        print("=" * 70)

    def load_data(self):
        """Load enriched mosque database."""
        print("\n📖 Loading final database...")
        self.df = pd.read_csv(self.mosques_csv, encoding='utf-8')
        print(f"✅ Loaded {len(self.df)} mosques")

    def generate_comprehensive_report(self):
        """Generate comprehensive text report."""
        print("\n📝 Generating comprehensive report...")

        report_path = self.output_dir / "FINAL_V1_REPORT.txt"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("MOSQUE RECONSTRUCTION DATABASE - VERSION 1.0\n")
            f.write("FINAL COMPREHENSIVE REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

            # Executive Summary
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 70 + "\n\n")
            f.write(f"Total Mosques in Database: {len(self.df)}\n")
            f.write(f"Data Quality: High confidence records\n")
            f.write(f"Geographic Coverage: {self.df['province'].nunique()} provinces\n")
            f.write(f"Media Assets: {(self.df['photo_count'] > 0).sum()} mosques with photos\n")
            f.write(f"Location Data: {self.df['has_location'].sum()} mosques with GPS\n\n")

            # Data Sources
            f.write("DATA SOURCES\n")
            f.write("-" * 70 + "\n\n")
            source_counts = self.df['source'].value_counts()
            for source, count in source_counts.items():
                pct = count / len(self.df) * 100
                f.write(f"  • {source}: {count} mosques ({pct:.1f}%)\n")
            f.write("\n")

            # Province Breakdown
            f.write("PROVINCE BREAKDOWN\n")
            f.write("-" * 70 + "\n\n")
            f.write(f"{'Province':<30} {'Total':<8} {'Damaged':<10} {'Demolished':<12} {'Photos':<8}\n")
            f.write("-" * 70 + "\n")

            for province in sorted(self.df['province'].unique()):
                prov_df = self.df[self.df['province'] == province]
                total = len(prov_df)
                damaged = (prov_df['damage_type'] == 'damaged').sum()
                demolished = (prov_df['damage_type'] == 'demolished').sum()
                with_photos = (prov_df['photo_count'] > 0).sum()

                f.write(f"{province:<30} {total:<8} {damaged:<10} {demolished:<12} {with_photos:<8}\n")

            f.write("\n")

            # Damage Assessment
            f.write("DAMAGE ASSESSMENT\n")
            f.write("-" * 70 + "\n\n")
            damage_counts = self.df['damage_type'].value_counts()
            for dtype, count in damage_counts.items():
                pct = count / len(self.df) * 100
                f.write(f"  • {dtype}: {count} mosques ({pct:.1f}%)\n")
            f.write("\n")

            # Media Coverage
            f.write("MEDIA COVERAGE\n")
            f.write("-" * 70 + "\n\n")
            with_photos = (self.df['photo_count'] > 0).sum()
            total_photos = self.df['photo_count'].sum()
            avg_photos = self.df[self.df['photo_count'] > 0]['photo_count'].mean() if with_photos > 0 else 0
            with_maps = self.df['has_location'].sum()

            f.write(f"  • Mosques with photos: {with_photos}/{len(self.df)} ({with_photos/len(self.df)*100:.1f}%)\n")
            f.write(f"  • Total photos: {int(total_photos)}\n")
            f.write(f"  • Average photos per mosque: {avg_photos:.1f}\n")
            f.write(f"  • Mosques with GPS location: {with_maps}/{len(self.df)} ({with_maps/len(self.df)*100:.1f}%)\n\n")

            # Data Quality
            f.write("DATA QUALITY METRICS\n")
            f.write("-" * 70 + "\n\n")

            # Check completeness
            name_complete = (self.df['mosque_name'].notna() & (self.df['mosque_name'] != '')).sum()
            area_complete = (self.df['area'].notna() & (self.df['area'] != '')).sum()
            province_complete = (self.df['province'].notna() & (self.df['province'] != '')).sum()

            f.write(f"Field Completeness:\n")
            f.write(f"  • Mosque Name: {name_complete}/{len(self.df)} ({name_complete/len(self.df)*100:.1f}%)\n")
            f.write(f"  • Area: {area_complete}/{len(self.df)} ({area_complete/len(self.df)*100:.1f}%)\n")
            f.write(f"  • Province: {province_complete}/{len(self.df)} ({province_complete/len(self.df)*100:.1f}%)\n\n")

            # Recommendations
            f.write("RECOMMENDATIONS FOR NEXT STEPS\n")
            f.write("-" * 70 + "\n\n")
            f.write("1. Data Enrichment:\n")
            f.write("   - Verify and geocode the 288 Google Maps links\n")
            f.write("   - Manual review of 455 AI-only mosques for quality\n")
            f.write("   - Add missing damage classifications (455 unknown)\n\n")

            f.write("2. Photo Processing:\n")
            f.write(f"   - Organize and catalog {int(total_photos)} photos\n")
            f.write("   - Match remaining unmatched photos to mosques\n")
            f.write("   - Generate thumbnails for web dashboard\n\n")

            f.write("3. Database Export:\n")
            f.write("   - Import to PostgreSQL for production use\n")
            f.write("   - Create GeoJSON for GIS mapping\n")
            f.write("   - Export summary Excel for stakeholders\n\n")

            f.write("4. Version 2 Planning:\n")
            f.write("   - Implement real-time Telegram bot (see V2_IDEAS_AND_SPECS.md)\n")
            f.write("   - Build web dashboard for data entry and review\n")
            f.write("   - Set up automated workflows with n8n\n\n")

            # File Inventory
            f.write("OUTPUT FILES INVENTORY\n")
            f.write("-" * 70 + "\n\n")
            f.write("CSV Files:\n")
            csv_files = sorted(self.output_dir.glob("*.csv"))
            for csv_file in csv_files:
                size = csv_file.stat().st_size / 1024
                f.write(f"  • {csv_file.name} ({size:.1f} KB)\n")
            f.write("\n")

            f.write("Documentation:\n")
            docs = ['README.md', 'CLAUDE.md', 'VERSION_1_SUMMARY.md',
                   'V2_IDEAS_AND_SPECS.md', 'V3_IDEAS_AND_SPECS.md']
            for doc in docs:
                if Path(doc).exists():
                    f.write(f"  • {doc}\n")
            f.write("\n")

            f.write("=" * 70 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 70 + "\n")

        print(f"✅ Comprehensive report: {report_path}")

    def generate_province_summaries(self):
        """Generate individual summary files for each province."""
        print("\n📂 Generating province summaries...")

        province_dir = self.output_dir / "by_province"
        province_dir.mkdir(exist_ok=True)

        for province in sorted(self.df['province'].unique()):
            prov_df = self.df[self.df['province'] == province]

            # Export CSV
            csv_path = province_dir / f"{province.replace('/', '_')}.csv"
            prov_df.to_csv(csv_path, index=False, encoding='utf-8')

            # Export summary
            summary_path = province_dir / f"{province.replace('/', '_')}_summary.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"Province: {province}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Total Mosques: {len(prov_df)}\n")
                f.write(f"Damaged: {(prov_df['damage_type'] == 'damaged').sum()}\n")
                f.write(f"Demolished: {(prov_df['damage_type'] == 'demolished').sum()}\n")
                f.write(f"Unknown Status: {(prov_df['damage_type'] == 'unknown').sum()}\n\n")
                f.write(f"With Photos: {(prov_df['photo_count'] > 0).sum()}\n")
                f.write(f"With GPS: {prov_df['has_location'].sum()}\n\n")

                f.write("Top Areas:\n")
                area_counts = prov_df['area'].value_counts().head(10)
                for area, count in area_counts.items():
                    if pd.notna(area) and area != '':
                        f.write(f"  • {area}: {count} mosques\n")

        print(f"✅ Created summaries for {self.df['province'].nunique()} provinces in: {province_dir}")

    def generate_excel_summary(self):
        """Generate Excel file for stakeholders."""
        print("\n📊 Generating Excel summary...")

        excel_path = self.output_dir / "mosque_database_summary.xlsx"

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Overview sheet
            overview_data = {
                'Metric': [
                    'Total Mosques',
                    'Provinces',
                    'Damaged Mosques',
                    'Demolished Mosques',
                    'With Photos',
                    'With GPS Location'
                ],
                'Value': [
                    len(self.df),
                    self.df['province'].nunique(),
                    (self.df['damage_type'] == 'damaged').sum(),
                    (self.df['damage_type'] == 'demolished').sum(),
                    (self.df['photo_count'] > 0).sum(),
                    self.df['has_location'].sum()
                ]
            }
            overview_df = pd.DataFrame(overview_data)
            overview_df.to_excel(writer, sheet_name='Overview', index=False)

            # By Province
            province_summary = self.df.groupby('province').agg({
                'mosque_id': 'count',
                'photo_count': lambda x: (x > 0).sum(),
                'has_location': 'sum'
            }).rename(columns={
                'mosque_id': 'Total Mosques',
                'photo_count': 'With Photos',
                'has_location': 'With GPS'
            })
            province_summary.to_excel(writer, sheet_name='By Province')

            # Complete database (first 1000 rows to avoid size issues)
            self.df.head(1000).to_excel(writer, sheet_name='Mosque Data', index=False)

        print(f"✅ Excel summary: {excel_path}")

    def run(self):
        """Execute all report generation."""
        self.load_data()
        self.generate_comprehensive_report()
        self.generate_province_summaries()
        self.generate_excel_summary()

        print("\n" + "=" * 70)
        print("✅ ALL REPORTS GENERATED - VERSION 1.0 COMPLETE!")
        print("=" * 70)
        print(f"\nDatabase Stats:")
        print(f"  • Total Mosques: {len(self.df)}")
        print(f"  • Provinces: {self.df['province'].nunique()}")
        print(f"  • With Photos: {(self.df['photo_count'] > 0).sum()}")
        print(f"  • With GPS: {self.df['has_location'].sum()}")
        print(f"\nMain Report: out_csv/FINAL_V1_REPORT.txt")
        print(f"Excel Summary: out_csv/mosque_database_summary.xlsx")
        print(f"Province Files: out_csv/by_province/")


if __name__ == "__main__":
    generator = FinalReportGenerator(
        mosques_csv="out_csv/mosques_enriched_with_media.csv",
        output_dir="out_csv"
    )
    generator.run()
