#!/usr/bin/env python3
"""
Extract GPS Coordinates from Google Maps URLs

Parses Google Maps links to extract latitude and longitude coordinates.

Author: Claude Code
Date: October 25, 2025
"""

import pandas as pd
import re
import requests
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import time


class GPSExtractor:
    """Extract GPS coordinates from Google Maps URLs"""

    def __init__(self, mosques_csv_path: str):
        self.mosques_df = pd.read_csv(mosques_csv_path, encoding='utf-8')
        print(f"Loaded {len(self.mosques_df)} mosque records")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def extract_coordinates(self, maps_url: str) -> tuple:
        """
        Extract lat, lng from Google Maps URL.

        Supports multiple formats:
        - https://maps.app.goo.gl/... (short links - will follow redirect)
        - https://www.google.com/maps/@33.5689,36.3456,15z
        - https://www.google.com/maps/place/@33.5689,36.3456
        - https://www.google.com/maps?q=33.5689,36.3456

        Returns:
            (latitude, longitude, method) or (None, None, error)
        """
        if not isinstance(maps_url, str):
            return None, None, 'invalid_url'

        # Pattern 1: @lat,lng format
        match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', maps_url)
        if match:
            return float(match.group(1)), float(match.group(2)), 'direct_parse'

        # Pattern 2: ?q=lat,lng format
        match = re.search(r'[?&]q=(-?\d+\.?\d*),(-?\d+\.?\d*)', maps_url)
        if match:
            return float(match.group(1)), float(match.group(2)), 'direct_parse'

        # Pattern 3: Short links (maps.app.goo.gl) - follow redirect
        if 'maps.app.goo.gl' in maps_url or 'goo.gl' in maps_url:
            try:
                time.sleep(0.1)  # Rate limiting
                response = self.session.head(maps_url, allow_redirects=True, timeout=5)
                expanded_url = response.url

                # Try to extract from expanded URL
                match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', expanded_url)
                if match:
                    return float(match.group(1)), float(match.group(2)), 'redirect_followed'

                return None, None, 'redirect_no_coords'
            except Exception as e:
                return None, None, f'redirect_error'

        return None, None, 'unknown_format'

    def process_mosques(self) -> pd.DataFrame:
        """
        Process all mosques and extract GPS coordinates.

        Returns:
            Updated DataFrame with latitude and longitude columns
        """
        latitudes = []
        longitudes = []
        extraction_methods = []

        total = len(self.mosques_df)
        for idx, row in self.mosques_df.iterrows():
            if (idx + 1) % 50 == 0:
                print(f"Processing {idx + 1}/{total}...")

            maps_url = row.get('maps_urls')

            if pd.notna(maps_url) and maps_url:
                lat, lng, method = self.extract_coordinates(maps_url)
                latitudes.append(lat)
                longitudes.append(lng)
                extraction_methods.append(method)
            else:
                latitudes.append(None)
                longitudes.append(None)
                extraction_methods.append('no_maps_url')

        # Add new columns
        self.mosques_df['latitude'] = latitudes
        self.mosques_df['longitude'] = longitudes
        self.mosques_df['gps_extraction_method'] = extraction_methods

        return self.mosques_df

    def generate_statistics(self):
        """Print statistics about GPS extraction"""
        total = len(self.mosques_df)
        with_maps = self.mosques_df['maps_urls'].notna().sum()
        with_gps = self.mosques_df['latitude'].notna().sum()

        print("\n=== GPS Extraction Statistics ===")
        print(f"Total mosques: {total}")
        print(f"With Google Maps URLs: {with_maps} ({with_maps/total*100:.1f}%)")
        print(f"GPS coordinates extracted: {with_gps} ({with_gps/total*100:.1f}%)")
        print(f"Short links (need API): {with_maps - with_gps}")
        print()
        print("Extraction method breakdown:")
        print(self.mosques_df['gps_extraction_method'].value_counts())


def main():
    """Main execution function"""
    print("=" * 60)
    print("GPS Coordinate Extractor")
    print("=" * 60)
    print()

    # Paths
    input_csv = Path('out_csv/mosques_fixed_photos.csv')
    output_csv = Path('out_csv/mosques_with_gps.csv')

    # Initialize extractor
    extractor = GPSExtractor(input_csv)

    # Process mosques
    print("Extracting GPS coordinates from Google Maps URLs...")
    result_df = extractor.process_mosques()

    # Generate statistics
    extractor.generate_statistics()

    # Save results
    print(f"\nSaving results to {output_csv}...")
    result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

    print(f"\nOutput saved to: {output_csv}")
    print("Done!")


if __name__ == '__main__':
    main()
