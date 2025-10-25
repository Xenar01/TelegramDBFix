#!/usr/bin/env python3
"""
Fix Photo Assignments - Hybrid Approach

This script implements the Hybrid approach to fix photo assignments:
1. Pattern A (text-then-photos): Auto-fix using proximity matching
2. Pattern B (photos-then-text): Flag for manual review
3. Pattern C (single mosque): Keep as-is

Author: Claude Code
Date: October 25, 2025
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple


class PhotoAssignmentFixer:
    """Fix photo assignments based on message patterns"""

    def __init__(self, telegram_export_path: str, clusters_csv_path: str):
        self.telegram_export_path = Path(telegram_export_path)
        self.clusters_csv_path = Path(clusters_csv_path)

        # Load data
        print("Loading Telegram export...")
        with open(self.telegram_export_path / 'result.json', 'r', encoding='utf-8') as f:
            telegram_data = json.load(f)
        self.messages = {msg['id']: msg for msg in telegram_data['messages']}

        print("Loading conversation clusters...")
        self.clusters_df = pd.read_csv(clusters_csv_path, encoding='utf-8')

        print(f"Loaded {len(self.clusters_df)} mosque records")
        print(f"Loaded {len(self.messages)} Telegram messages")

    def classify_cluster_pattern(self, msg_ids: List[int]) -> Tuple[str, List[Dict]]:
        """
        Classify the message pattern for a cluster.

        Returns:
            (pattern_type, sequence)
            pattern_type: 'single_mosque', 'text_then_photos', 'photos_then_text', 'unknown'
            sequence: List of {msg_id, type: 'TEXT'|'PHOTO', content}
        """
        sequence = []

        for msg_id in msg_ids:
            msg = self.messages.get(msg_id)
            if not msg:
                continue

            if 'file' in msg and msg['file']:
                sequence.append({
                    'msg_id': msg_id,
                    'type': 'PHOTO',
                    'content': msg['file']
                })
            elif 'text' in msg and msg['text']:
                text = msg['text'] if isinstance(msg['text'], str) else self._extract_text(msg['text'])
                if text.strip():
                    sequence.append({
                        'msg_id': msg_id,
                        'type': 'TEXT',
                        'content': text.strip()
                    })

        # Classify pattern
        if not sequence:
            return 'unknown', sequence

        text_count = sum(1 for s in sequence if s['type'] == 'TEXT')
        photo_count = sum(1 for s in sequence if s['type'] == 'PHOTO')

        if text_count <= 1:
            return 'single_mosque', sequence

        # Check first non-empty item
        first_type = sequence[0]['type'] if sequence else None

        if first_type == 'TEXT':
            return 'text_then_photos', sequence
        elif first_type == 'PHOTO':
            return 'photos_then_text', sequence
        else:
            return 'unknown', sequence

    def _extract_text(self, text_obj) -> str:
        """Extract text from Telegram text object (can be string or list)"""
        if isinstance(text_obj, str):
            return text_obj
        elif isinstance(text_obj, list):
            parts = []
            for item in text_obj:
                if isinstance(item, dict):
                    parts.append(item.get('text', ''))
                else:
                    parts.append(str(item))
            return ''.join(parts)
        return ''

    def assign_photos_pattern_a(self, sequence: List[Dict], mosque_texts: List[str]) -> Dict[str, List[str]]:
        """
        Assign photos for Pattern A (text-then-photos).

        Logic: Photos immediately after a text message belong to that text.

        Returns:
            Dict mapping mosque_text -> list of photo files
        """
        assignments = defaultdict(list)
        current_text = None

        for item in sequence:
            if item['type'] == 'TEXT':
                current_text = item['content']
            elif item['type'] == 'PHOTO' and current_text:
                assignments[current_text].append(item['content'])

        return dict(assignments)

    def process_clusters(self) -> pd.DataFrame:
        """
        Process all clusters and fix photo assignments.

        Returns:
            Updated DataFrame with fixed photo assignments
        """
        results = []
        stats = {
            'single_mosque': 0,
            'text_then_photos_fixed': 0,
            'photos_then_text_flagged': 0,
            'unknown': 0
        }

        # Group by cluster_id
        for cluster_id, group in self.clusters_df.groupby('cluster_id'):
            msg_ids_str = group.iloc[0]['message_ids']
            msg_ids = [int(x.strip()) for x in msg_ids_str.split(';')]

            # Classify pattern
            pattern, sequence = self.classify_cluster_pattern(msg_ids)

            if len(group) == 1:
                # Single mosque - keep as-is
                row = group.iloc[0].copy()
                row['photo_assignment_method'] = 'direct'
                row['cluster_pattern'] = 'single_mosque'
                row['needs_review'] = False
                results.append(row)
                stats['single_mosque'] += 1

            elif pattern == 'text_then_photos':
                # Pattern A - fix using proximity
                mosque_texts = group['name'].tolist()
                photo_assignments = self.assign_photos_pattern_a(sequence, mosque_texts)

                for idx, row in group.iterrows():
                    new_row = row.copy()
                    mosque_name = row['name']

                    # Find matching photos for this mosque
                    assigned_photos = []
                    for text_key, photos in photo_assignments.items():
                        # Match mosque name in text (fuzzy)
                        if mosque_name in text_key or self._fuzzy_match(mosque_name, text_key):
                            assigned_photos.extend(photos)

                    # Update photo data
                    if assigned_photos:
                        new_row['photo_files'] = '; '.join(assigned_photos)
                        new_row['photo_count'] = len(assigned_photos)
                    else:
                        new_row['photo_files'] = None
                        new_row['photo_count'] = 0

                    new_row['photo_assignment_method'] = 'proximity_auto'
                    new_row['cluster_pattern'] = 'text_then_photos'
                    new_row['needs_review'] = False
                    results.append(new_row)

                stats['text_then_photos_fixed'] += len(group)

            elif pattern == 'photos_then_text':
                # Pattern B - flag for manual review
                for idx, row in group.iterrows():
                    new_row = row.copy()
                    # Keep photos but flag as needing review
                    new_row['photo_assignment_method'] = 'shared_needs_review'
                    new_row['cluster_pattern'] = 'photos_then_text'
                    new_row['needs_review'] = True
                    results.append(new_row)

                stats['photos_then_text_flagged'] += len(group)

            else:
                # Unknown pattern - keep as-is but flag
                for idx, row in group.iterrows():
                    new_row = row.copy()
                    new_row['photo_assignment_method'] = 'unknown'
                    new_row['cluster_pattern'] = 'unknown'
                    new_row['needs_review'] = True
                    results.append(new_row)

                stats['unknown'] += len(group)

        # Create result DataFrame
        result_df = pd.DataFrame(results)

        # Print statistics
        print("\n=== Processing Statistics ===")
        print(f"Single mosque (kept as-is): {stats['single_mosque']}")
        print(f"Pattern A fixed: {stats['text_then_photos_fixed']}")
        print(f"Pattern B flagged: {stats['photos_then_text_flagged']}")
        print(f"Unknown pattern: {stats['unknown']}")
        print(f"Total mosques: {len(result_df)}")

        return result_df

    def _fuzzy_match(self, name1: str, name2: str, threshold: float = 0.7) -> bool:
        """Simple fuzzy matching for mosque names"""
        # Remove common prefixes
        name1_clean = name1.replace('مسجد', '').strip()
        name2_clean = name2.replace('مسجد', '').strip()

        # Check if one contains the other
        if name1_clean in name2_clean or name2_clean in name1_clean:
            return True

        return False


def main():
    """Main execution function"""
    print("=" * 60)
    print("Photo Assignment Fixer - Hybrid Approach")
    print("=" * 60)
    print()

    # Paths
    telegram_export = Path('MasajidChat')
    clusters_csv = Path('out_csv/conversation_clusters_analyzed.csv')
    output_csv = Path('out_csv/mosques_fixed_photos.csv')

    # Initialize fixer
    fixer = PhotoAssignmentFixer(telegram_export, clusters_csv)

    # Process clusters
    print("\nProcessing clusters...")
    fixed_df = fixer.process_clusters()

    # Save results
    print(f"\nSaving results to {output_csv}...")
    fixed_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

    # Generate summary report
    print("\n=== Quality Metrics ===")
    print(f"Total mosques: {len(fixed_df)}")
    print(f"With photos: {fixed_df['photo_count'].gt(0).sum()} ({fixed_df['photo_count'].gt(0).sum()/len(fixed_df)*100:.1f}%)")
    print(f"Needs review: {fixed_df['needs_review'].sum()} ({fixed_df['needs_review'].sum()/len(fixed_df)*100:.1f}%)")
    print()
    print("Assignment methods:")
    print(fixed_df['photo_assignment_method'].value_counts())
    print()
    print(f"Output saved to: {output_csv}")
    print("\nDone! ✓")


if __name__ == '__main__':
    main()
