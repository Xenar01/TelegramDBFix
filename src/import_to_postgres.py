#!/usr/bin/env python3
"""
Import CSV data to PostgreSQL database.
"""

import os
import csv
import psycopg2
from psycopg2 import sql
from pathlib import Path
from dotenv import load_dotenv


class PostgresImporter:
    """Import parsed CSV data into PostgreSQL."""

    def __init__(self, csv_dir: str = "out_csv"):
        load_dotenv()
        self.csv_dir = Path(csv_dir)

        # Database connection
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'mosques'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        self.cursor = self.conn.cursor()

        print("✅ Connected to PostgreSQL database")

    def create_schema(self):
        """Create database schema."""
        schema_file = Path('src/schema.sql')

        if schema_file.exists():
            print("📋 Creating database schema...")
            with open(schema_file, 'r', encoding='utf-8') as f:
                self.cursor.execute(f.read())
            self.conn.commit()
            print("✅ Schema created successfully")
        else:
            print("⚠️ Schema file not found, skipping...")

    def import_provinces(self):
        """Import provinces from CSV."""
        csv_file = self.csv_dir / 'provinces.csv'
        print(f"📥 Importing provinces from {csv_file}...")

        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:
                self.cursor.execute("""
                    INSERT INTO provinces (id, name_ar, topic_id, created_at)
                    VALUES (%(id)s, %(name_ar)s, %(topic_id)s, %(created_at)s)
                    ON CONFLICT (topic_id) DO NOTHING
                """, row)
                count += 1

        self.conn.commit()
        print(f"✅ Imported {count} provinces")

    def import_mosques(self):
        """Import mosques from CSV."""
        csv_file = self.csv_dir / 'mosques.csv'
        print(f"📥 Importing mosques from {csv_file}...")

        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:
                self.cursor.execute("""
                    INSERT INTO mosques (province_id, mosque_name, area_name, source_message_id, created_at)
                    VALUES (%(province_id)s, %(mosque_name)s, %(area_name)s, %(source_message_id)s, %(date)s)
                    ON CONFLICT (province_id, mosque_name, area_name) DO NOTHING
                    RETURNING id
                """, row)

                result = self.cursor.fetchone()
                if result:
                    count += 1

        self.conn.commit()
        print(f"✅ Imported {count} mosques")

    def import_locations(self):
        """Import locations from CSV."""
        csv_file = self.csv_dir / 'locations.csv'
        print(f"📥 Importing locations from {csv_file}...")

        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:
                # Get mosque_id from province and name
                self.cursor.execute("""
                    SELECT id FROM mosques
                    WHERE mosque_name = %s AND area_name = %s
                    LIMIT 1
                """, (row['mosque_name'], row['area_name']))

                result = self.cursor.fetchone()
                if result:
                    mosque_id = result[0]

                    self.cursor.execute("""
                        INSERT INTO locations (mosque_id, gmaps_url)
                        VALUES (%s, %s)
                    """, (mosque_id, row['gmaps_url']))
                    count += 1

        self.conn.commit()
        print(f"✅ Imported {count} locations")

    def import_photos(self):
        """Import photos from CSV."""
        csv_file = self.csv_dir / 'photos.csv'
        print(f"📥 Importing photos from {csv_file}...")

        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:
                # First create file entry
                self.cursor.execute("""
                    INSERT INTO files (file_path, file_type, file_size, message_id)
                    VALUES (%(file_path)s, 'photo', %(file_size)s, %(message_id)s)
                    RETURNING id
                """, row)

                file_id = self.cursor.fetchone()[0]

                # Then create photo entry linked to mosque
                self.cursor.execute("""
                    INSERT INTO photos (mosque_id, file_id, file_path, message_id)
                    VALUES (%(mosque_id)s, %s, %(file_path)s, %(message_id)s)
                """, {**row, 'file_id': file_id})

                count += 1

        self.conn.commit()
        print(f"✅ Imported {count} photos")

    def import_excel_files(self):
        """Import Excel files metadata from CSV."""
        csv_file = self.csv_dir / 'excel_files.csv'
        print(f"📥 Importing Excel files from {csv_file}...")

        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:
                self.cursor.execute("""
                    INSERT INTO files (file_path, file_type, file_size, message_id)
                    VALUES (%(file_path)s, 'excel', %(file_size)s, %(message_id)s)
                """, row)
                count += 1

        self.conn.commit()
        print(f"✅ Imported {count} Excel file records")

    def run(self, create_schema: bool = True):
        """Run the full import pipeline."""
        print("\n🚀 Starting PostgreSQL Import\n")

        try:
            if create_schema:
                self.create_schema()

            self.import_provinces()
            self.import_mosques()
            self.import_locations()
            self.import_photos()
            self.import_excel_files()

            print("\n✅ Import completed successfully!\n")

        except Exception as e:
            print(f"\n❌ Error during import: {e}\n")
            self.conn.rollback()
            raise

        finally:
            self.cursor.close()
            self.conn.close()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Import CSV data to PostgreSQL')
    parser.add_argument('--csv-dir', default='out_csv',
                       help='Directory containing CSV files')
    parser.add_argument('--no-schema', action='store_true',
                       help='Skip schema creation')

    args = parser.parse_args()

    importer = PostgresImporter(args.csv_dir)
    importer.run(create_schema=not args.no_schema)


if __name__ == '__main__':
    main()
