#!/usr/bin/env python3
"""
AI-Based Photo Assignment

Uses Claude AI to intelligently analyze conversation clusters and assign
photos/maps to the correct mosques based on context and message flow.

Author: Claude Code
Date: October 25, 2025
"""

import json
import pandas as pd
import anthropic
import os
from pathlib import Path
from typing import Dict, List
import time


class AIPhotoAssigner:
    """Use AI to assign photos to mosques based on conversation context"""

    def __init__(self, telegram_export_path: str, clusters_csv_path: str):
        self.telegram_export_path = Path(telegram_export_path)
        self.clusters_csv_path = Path(clusters_csv_path)

        # Load API key
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Load data
        print("Loading Telegram export...")
        with open(self.telegram_export_path / 'result.json', 'r', encoding='utf-8') as f:
            telegram_data = json.load(f)
        self.messages = {msg['id']: msg for msg in telegram_data['messages']}

        print("Loading conversation clusters...")
        self.clusters_df = pd.read_csv(clusters_csv_path, encoding='utf-8')

        print(f"Loaded {len(self.clusters_df)} mosque records")
        print(f"Loaded {len(self.messages)} Telegram messages")

        self.total_cost = 0
        self.api_calls = 0

    def _extract_text(self, text_obj) -> str:
        """Extract text from Telegram text object"""
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

    def build_conversation_context(self, msg_ids: List[int]) -> str:
        """
        Build a readable conversation context from message IDs.

        Returns formatted text showing the message sequence.
        """
        context_lines = []

        for msg_id in msg_ids:
            msg = self.messages.get(msg_id)
            if not msg:
                continue

            date = msg.get('date', '').split('T')[1][:5]  # HH:MM format

            if 'file' in msg and msg['file']:
                file_path = msg['file']
                if 'photo' in msg.get('media_type', '').lower() or file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                    context_lines.append(f"[{date}] Message {msg_id}: PHOTO - {file_path}")
                elif 'video' in msg.get('media_type', '').lower() or file_path.lower().endswith(('.mp4', '.mov')):
                    context_lines.append(f"[{date}] Message {msg_id}: VIDEO - {file_path}")
                else:
                    context_lines.append(f"[{date}] Message {msg_id}: FILE - {file_path}")

            elif 'text' in msg and msg['text']:
                text = self._extract_text(msg['text'])
                if text.strip():
                    # Check if text contains Google Maps link
                    if 'maps.app.goo.gl' in text or 'google.com/maps' in text:
                        context_lines.append(f"[{date}] Message {msg_id}: MAPS LINK + TEXT - {text[:100]}")
                    else:
                        context_lines.append(f"[{date}] Message {msg_id}: TEXT - {text[:150]}")

        return '\n'.join(context_lines)

    def analyze_cluster_with_ai(self, cluster_id: int, mosque_names: List[str],
                                 conversation_context: str) -> Dict:
        """
        Use Claude AI to analyze a cluster and assign media to mosques.

        Returns:
            Dict with mosque names as keys and their assigned media
        """
        prompt = f"""You are analyzing a Telegram conversation about mosque damage documentation in Syria.

CONVERSATION SEQUENCE:
{conversation_context}

MOSQUE NAMES MENTIONED:
{chr(10).join([f"- {name}" for name in mosque_names])}

TASK:
Analyze the conversation flow and determine which photos, videos, and maps links belong to which mosque.

RULES:
1. Photos/videos sent immediately after a mosque name usually belong to that mosque
2. A maps link with a mosque name in the same message belongs to that mosque
3. If multiple mosques share media (area documentation), assign to all of them
4. If unclear, assign to the nearest mosque name (before or after)

OUTPUT FORMAT (JSON):
{{
  "assignments": {{
    "Mosque Name 1": {{
      "photos": ["files/IMG_123.JPG", "files/IMG_124.JPG"],
      "videos": ["files/VIDEO_001.mp4"],
      "maps": ["https://maps.app.goo.gl/..."]
    }},
    "Mosque Name 2": {{
      "photos": ["files/IMG_125.JPG"],
      "videos": [],
      "maps": ["https://maps.app.goo.gl/..."]
    }}
  }},
  "reasoning": "Brief explanation of assignment decisions"
}}

Respond ONLY with valid JSON, no additional text."""

        try:
            self.api_calls += 1
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=2000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            # Calculate cost (Haiku: $0.25 per 1M input, $1.25 per 1M output)
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            cost = (input_tokens * 0.25 / 1_000_000) + (output_tokens * 1.25 / 1_000_000)
            self.total_cost += cost

            # Parse response
            response_text = message.content[0].text

            # Extract JSON from response (may have markdown formatting)
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]

            result = json.loads(response_text.strip())
            return result

        except Exception as e:
            print(f"  ⚠ Error analyzing cluster {cluster_id}: {str(e)}")
            return {
                "assignments": {name: {"photos": [], "videos": [], "maps": []} for name in mosque_names},
                "reasoning": f"Error: {str(e)}"
            }

    def process_all_clusters(self) -> pd.DataFrame:
        """
        Process all clusters with AI-based assignment.

        Returns:
            Updated DataFrame with AI-assigned media
        """
        results = []

        # Group by cluster_id
        cluster_groups = self.clusters_df.groupby('cluster_id')
        multi_mosque_clusters = [cid for cid, group in cluster_groups if len(group) > 1]

        print(f"\nFound {len(multi_mosque_clusters)} clusters with multiple mosques")
        print("Processing with AI...\n")

        processed = 0
        for cluster_id, group in cluster_groups:
            if len(group) == 1:
                # Single mosque - keep as-is
                row = group.iloc[0].copy()
                row['assignment_method'] = 'single_mosque_direct'
                row['ai_analyzed'] = False
                results.append(row)
            else:
                # Multiple mosques - use AI
                mosque_names = group['name'].tolist()
                msg_ids_str = group.iloc[0]['message_ids']
                msg_ids = [int(x.strip()) for x in msg_ids_str.split(';')]

                # Build context
                conversation_context = self.build_conversation_context(msg_ids)

                # Analyze with AI
                print(f"Analyzing Cluster #{cluster_id} ({len(group)} mosques)...")
                ai_result = self.analyze_cluster_with_ai(cluster_id, mosque_names, conversation_context)

                # Apply assignments
                for idx, row in group.iterrows():
                    new_row = row.copy()
                    mosque_name = row['name']

                    # Get AI assignments for this mosque
                    assignment = ai_result['assignments'].get(mosque_name, {
                        'photos': [], 'videos': [], 'maps': []
                    })

                    # Update photo data
                    if assignment['photos']:
                        new_row['photo_files'] = '; '.join(assignment['photos'])
                        new_row['photo_count'] = len(assignment['photos'])
                    else:
                        new_row['photo_files'] = None
                        new_row['photo_count'] = 0

                    # Update maps
                    if assignment['maps']:
                        new_row['maps_urls'] = '; '.join(assignment['maps'])
                    else:
                        new_row['maps_urls'] = None

                    # Update video data
                    if assignment['videos']:
                        new_row['video_files'] = '; '.join(assignment['videos'])
                    else:
                        new_row['video_files'] = None

                    # Add metadata
                    new_row['assignment_method'] = 'ai_context_based'
                    new_row['ai_analyzed'] = True
                    new_row['ai_reasoning'] = ai_result.get('reasoning', '')

                    results.append(new_row)

                processed += 1
                if processed % 10 == 0:
                    print(f"  Progress: {processed}/{len(multi_mosque_clusters)} clusters | Cost: ${self.total_cost:.4f}")

                # Rate limiting
                time.sleep(0.5)

        # Create result DataFrame
        result_df = pd.DataFrame(results)

        print(f"\n=== Processing Complete ===")
        print(f"Total API calls: {self.api_calls}")
        print(f"Total cost: ${self.total_cost:.4f}")
        print(f"Mosques processed: {len(result_df)}")
        print(f"AI-analyzed: {result_df['ai_analyzed'].sum()}")

        return result_df


def main():
    """Main execution function"""
    print("=" * 60)
    print("AI-Based Photo Assignment")
    print("=" * 60)
    print()

    # Paths
    telegram_export = Path('MasajidChat')
    clusters_csv = Path('out_csv/conversation_clusters_analyzed.csv')
    output_csv = Path('out_csv/mosques_ai_assigned.csv')

    # Check API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please set it with: export ANTHROPIC_API_KEY=your_key")
        return

    # Initialize assigner
    assigner = AIPhotoAssigner(telegram_export, clusters_csv)

    # Estimate cost
    multi_mosque_clusters = len([cid for cid, group in assigner.clusters_df.groupby('cluster_id') if len(group) > 1])
    estimated_cost = multi_mosque_clusters * 0.02  # ~$0.02 per cluster

    print(f"\nEstimated cost: ${estimated_cost:.2f}")
    print(f"Clusters to analyze: {multi_mosque_clusters}")
    print()

    response = input("Proceed with AI analysis? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return

    # Process clusters
    print("\nProcessing clusters with AI...\n")
    result_df = assigner.process_all_clusters()

    # Save results
    print(f"\nSaving results to {output_csv}...")
    result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

    # Generate comparison
    print("\n=== Quality Comparison ===")
    print(f"Mosques with photos: {result_df['photo_count'].gt(0).sum()} ({result_df['photo_count'].gt(0).sum()/len(result_df)*100:.1f}%)")
    print(f"Mosques with maps: {result_df['maps_urls'].notna().sum()} ({result_df['maps_urls'].notna().sum()/len(result_df)*100:.1f}%)")
    print()
    print("Assignment method breakdown:")
    print(result_df['assignment_method'].value_counts())

    print(f"\nOutput saved to: {output_csv}")
    print(f"Final cost: ${assigner.total_cost:.4f}")
    print("\nDone!")


if __name__ == '__main__':
    main()
