#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversation-First Mosque Data Analyzer
========================================
Analyzes Telegram conversations to properly group photos, text, and maps.

Strategy:
1. Group messages by province (using reply_to_message_id → topics)
2. Cluster consecutive messages (same conversation)
3. Use Claude AI to parse each cluster intelligently
4. Extract complete mosque records with ALL media linked
"""

import sys
import os
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from anthropic import Anthropic
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()


class ConversationAnalyzer:
    """Analyze Telegram conversations to group mosque data properly."""

    def __init__(self, export_path: str, output_dir: str = "out_csv"):
        self.export_path = Path(export_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.export_data = None
        self.topics = {}  # topic_id -> province_name
        self.messages_by_topic = {}  # topic_id -> [messages]
        self.clusters = []  # Final conversation clusters

        # Initialize Claude AI
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
        self.client = Anthropic(api_key=api_key)

        self.api_calls = 0
        self.total_cost = 0.0

        print("=" * 70)
        print("🔍 CONVERSATION-FIRST ANALYZER")
        print("=" * 70)

    def load_export(self):
        """Load Telegram export JSON."""
        print("\n📖 Loading Telegram export...")
        with open(self.export_path, 'r', encoding='utf-8') as f:
            self.export_data = json.load(f)
        print(f"✅ Loaded {len(self.export_data['messages'])} messages")

    def extract_topics(self):
        """Extract topics (provinces) from service messages."""
        print("\n🏛️ Extracting topics (provinces)...")

        for msg in self.export_data['messages']:
            if msg.get('type') == 'service' and msg.get('action') == 'topic_created':
                topic_id = msg['id']
                # Clean topic title - remove "مساجد" prefix
                title = msg.get('title', 'غير معروف')
                if title.startswith('مساجد '):
                    title = title.replace('مساجد ', '')
                self.topics[topic_id] = title

        print(f"✅ Found {len(self.topics)} topics:")
        for topic_id, name in sorted(self.topics.items()):
            print(f"   • Topic {topic_id}: {name}")

    def group_by_topic(self):
        """Group all messages by their topic (province)."""
        print("\n📂 Grouping messages by province topic...")

        # Initialize lists for each topic
        for topic_id in self.topics.keys():
            self.messages_by_topic[topic_id] = []

        # Add an "unknown" topic for messages not in any topic
        unknown_topic_id = -1
        self.topics[unknown_topic_id] = "غير معروف"
        self.messages_by_topic[unknown_topic_id] = []

        # Group messages
        for msg in self.export_data['messages']:
            if msg.get('type') != 'message':
                continue

            reply_to = msg.get('reply_to_message_id')

            if reply_to in self.topics:
                self.messages_by_topic[reply_to].append(msg)
            else:
                # Message doesn't belong to any topic
                self.messages_by_topic[unknown_topic_id].append(msg)

        # Print statistics
        for topic_id, messages in self.messages_by_topic.items():
            province = self.topics[topic_id]
            print(f"   • {province}: {len(messages)} messages")

    def cluster_messages(self):
        """
        Cluster consecutive messages within each topic.

        A cluster is defined as:
        - Messages within 10 minutes of each other
        - Consecutive or near-consecutive message IDs
        - Same topic/province
        """
        print("\n🔗 Clustering consecutive messages...")

        all_clusters = []

        for topic_id, messages in self.messages_by_topic.items():
            if len(messages) == 0:
                continue

            province = self.topics[topic_id]

            # Sort by message ID
            sorted_msgs = sorted(messages, key=lambda m: m['id'])

            # Cluster parameters
            MAX_TIME_GAP_MINUTES = 10
            MAX_ID_GAP = 10

            current_cluster = []
            last_timestamp = None
            last_id = None

            for msg in sorted_msgs:
                msg_id = msg['id']
                timestamp = datetime.fromisoformat(msg['date'].replace('Z', '+00:00'))

                # Check if this message should start a new cluster
                start_new_cluster = False

                if current_cluster:
                    time_gap = (timestamp - last_timestamp).total_seconds() / 60
                    id_gap = msg_id - last_id

                    if time_gap > MAX_TIME_GAP_MINUTES or id_gap > MAX_ID_GAP:
                        start_new_cluster = True

                if start_new_cluster:
                    # Save current cluster
                    if len(current_cluster) > 0:
                        all_clusters.append({
                            'topic_id': topic_id,
                            'province': province,
                            'messages': current_cluster.copy()
                        })
                    current_cluster = []

                # Add message to current cluster
                current_cluster.append(msg)
                last_timestamp = timestamp
                last_id = msg_id

            # Save final cluster
            if len(current_cluster) > 0:
                all_clusters.append({
                    'topic_id': topic_id,
                    'province': province,
                    'messages': current_cluster
                })

        self.clusters = all_clusters
        print(f"✅ Created {len(self.clusters)} message clusters")

        # Statistics
        cluster_sizes = [len(c['messages']) for c in self.clusters]
        print(f"   • Average cluster size: {sum(cluster_sizes)/len(cluster_sizes):.1f} messages")
        print(f"   • Largest cluster: {max(cluster_sizes)} messages")
        print(f"   • Smallest cluster: {min(cluster_sizes)} messages")

    def extract_cluster_content(self, cluster: Dict) -> Dict:
        """Extract photos, maps, and text from a message cluster."""
        photos = []
        maps_urls = []
        text_content = []
        video_files = []

        for msg in cluster['messages']:
            msg_id = msg['id']

            # Extract photos
            if 'file' in msg or 'photo' in msg:
                file_path = msg.get('file') or msg.get('photo')
                if file_path and (file_path.lower().endswith(('.jpg', '.jpeg', '.png'))):
                    photos.append({
                        'message_id': msg_id,
                        'file_path': file_path
                    })

            # Extract videos
            if 'file' in msg:
                file_path = msg['file']
                if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    video_files.append({
                        'message_id': msg_id,
                        'file_path': file_path
                    })

            # Extract text
            text = self._extract_text(msg.get('text', ''))
            if text:
                text_content.append({
                    'message_id': msg_id,
                    'text': text
                })

                # Check for maps URLs in text
                if 'maps.app.goo.gl' in text or 'maps.google.com' in text:
                    # Extract URL
                    import re
                    url_pattern = r'(https?://[^\s]+)'
                    urls = re.findall(url_pattern, text)
                    for url in urls:
                        if 'maps' in url:
                            maps_urls.append({
                                'message_id': msg_id,
                                'url': url,
                                'context': text
                            })

        return {
            'photos': photos,
            'maps': maps_urls,
            'text': text_content,
            'videos': video_files
        }

    def _extract_text(self, text_field) -> str:
        """Extract plain text from Telegram text field."""
        if isinstance(text_field, str):
            return text_field.strip()
        elif isinstance(text_field, list):
            return ''.join([
                item.get('text', '') if isinstance(item, dict) else str(item)
                for item in text_field
            ]).strip()
        return ''

    def parse_cluster_with_ai(self, cluster_data: Dict, cluster_id: int) -> Optional[Dict]:
        """
        Use Claude AI to parse a message cluster and extract mosque information.

        This is where AI adds value - understanding context, extracting names,
        handling ambiguity in Arabic text.
        """
        province = cluster_data['province']
        content = self.extract_cluster_content(cluster_data)

        # Skip clusters with no meaningful content
        if not content['text'] and not content['photos'] and not content['maps']:
            return None

        # Build prompt for Claude
        combined_text = '\n'.join([t['text'] for t in content['text']])

        if not combined_text and len(content['photos']) == 0:
            return None  # Nothing to analyze

        prompt = f"""أنت خبير في تحليل بيانات المساجد من محادثات تيليجرام.

**المقاطعة:** {province}

**النصوص في المحادثة:**
{combined_text if combined_text else 'لا يوجد نص (فقط صور)'}

**عدد الصور:** {len(content['photos'])}
**عدد روابط الخرائط:** {len(content['maps'])}
**عدد الفيديوهات:** {len(content['videos'])}

**المطلوب:**
1. استخرج أسماء المساجد من النصوص
2. حدد المنطقة/المدينة إذا كانت مذكورة
3. حدد إذا كان هناك مسجد واحد أم عدة مساجد
4. حدد نوع الضرر إذا ذُكر (متضرر/مدمر)

**الرد بصيغة JSON فقط (بدون أي نص إضافي):**
{{
  "mosques_count": عدد المساجد,
  "mosques": [
    {{
      "name": "اسم المسجد",
      "area": "المنطقة",
      "damage_type": "damaged/demolished/unknown",
      "confidence": "high/medium/low",
      "reasoning": "سبب هذا الاستنتاج"
    }}
  ],
  "has_photos": true/false,
  "has_maps": true/false
}}

إذا لم تجد معلومات عن مساجد، أرجع: {{"mosques_count": 0, "mosques": []}}
"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )

            self.api_calls += 1
            # Estimate cost (Haiku: $0.00025 per 1K input tokens, $0.00125 per 1K output)
            self.total_cost += 0.0005  # Rough estimate

            # Parse JSON response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                # Find the JSON content (skip the ``` lines)
                json_lines = [l for l in lines if l.strip() and not l.strip().startswith('```')]
                response_text = '\n'.join(json_lines)

            # Try to extract JSON even if there's extra text
            # Find the first { and last }
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                response_text = response_text[start_idx:end_idx+1]

            # Replace any problematic quotes in Arabic text
            # This is a workaround for malformed JSON from AI
            result = json.loads(response_text)

            # Enhance result with cluster content
            if result.get('mosques_count', 0) > 0:
                for mosque in result['mosques']:
                    mosque['cluster_id'] = cluster_id
                    mosque['province'] = province
                    mosque['photo_files'] = [p['file_path'] for p in content['photos']]
                    mosque['photo_count'] = len(content['photos'])
                    mosque['maps_urls'] = [m['url'] for m in content['maps']]
                    mosque['video_files'] = [v['file_path'] for v in content['videos']]
                    mosque['message_ids'] = [m['id'] for m in cluster_data['messages']]
                    mosque['original_text'] = combined_text

            return result

        except json.JSONDecodeError as e:
            print(f"   ⚠️ JSON Error cluster {cluster_id}: {str(e)[:100]}")
            # Return empty result to skip this cluster
            return {'mosques_count': 0, 'mosques': []}
        except Exception as e:
            print(f"   ⚠️ Error cluster {cluster_id}: {str(e)[:100]}")
            return {'mosques_count': 0, 'mosques': []}

    def analyze_all_clusters(self):
        """Analyze all message clusters using AI."""
        print(f"\n🤖 Analyzing {len(self.clusters)} clusters with Claude AI...")
        print(f"   Estimated cost: ${len(self.clusters) * 0.0005:.2f}")

        extracted_mosques = []
        processed = 0

        for idx, cluster in enumerate(self.clusters):
            if idx % 50 == 0 and idx > 0:
                print(f"   Progress: {idx}/{len(self.clusters)} ({idx/len(self.clusters)*100:.1f}%)")

            result = self.parse_cluster_with_ai(cluster, idx)

            if result and result.get('mosques_count', 0) > 0:
                for mosque in result['mosques']:
                    extracted_mosques.append(mosque)
                    print(f"   ✅ {mosque['name']} - {mosque['area']} ({mosque['province']}) [{mosque['confidence']}]")

            processed += 1

        print(f"\n✅ AI Analysis complete!")
        print(f"   • Clusters analyzed: {processed}")
        print(f"   • Mosques extracted: {len(extracted_mosques)}")
        print(f"   • API calls: {self.api_calls}")
        print(f"   • Total cost: ${self.total_cost:.2f}")

        return extracted_mosques

    def export_results(self, mosques: List[Dict]):
        """Export analyzed mosque data to CSV."""
        print("\n💾 Exporting results...")

        if len(mosques) == 0:
            print("⚠️ No mosques extracted!")
            return

        # Convert to DataFrame
        df = pd.DataFrame(mosques)

        # Convert list columns to strings for CSV
        for col in ['photo_files', 'maps_urls', 'video_files', 'message_ids']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: '; '.join(map(str, x)) if x else '')

        # Export
        output_path = self.output_dir / "conversation_clusters_analyzed.csv"
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"✅ Exported: {output_path} ({len(df)} rows)")

        # Statistics
        stats_path = self.output_dir / "conversation_analysis_stats.txt"
        with open(stats_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("CONVERSATION ANALYSIS STATISTICS\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Total Clusters Analyzed: {len(self.clusters)}\n")
            f.write(f"Mosques Extracted: {len(df)}\n")
            f.write(f"API Calls: {self.api_calls}\n")
            f.write(f"Total Cost: ${self.total_cost:.2f}\n\n")

            f.write("By Province:\n")
            for province in df['province'].unique():
                count = len(df[df['province'] == province])
                with_photos = (df[df['province'] == province]['photo_count'] > 0).sum()
                with_maps = (df[df['province'] == province]['maps_urls'].str.len() > 0).sum()
                f.write(f"  • {province}: {count} mosques ({with_photos} with photos, {with_maps} with maps)\n")

            f.write("\nConfidence Levels:\n")
            for conf in df['confidence'].unique():
                count = (df['confidence'] == conf).sum()
                pct = count / len(df) * 100
                f.write(f"  • {conf}: {count} ({pct:.1f}%)\n")

        print(f"✅ Statistics: {stats_path}")

    def run(self):
        """Execute the full conversation analysis."""
        self.load_export()
        self.extract_topics()
        self.group_by_topic()
        self.cluster_messages()
        mosques = self.analyze_all_clusters()
        self.export_results(mosques)

        print("\n" + "=" * 70)
        print("✅ CONVERSATION ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"\nExtracted {len(mosques)} mosques with proper media linkage")
        print(f"Output: out_csv/conversation_clusters_analyzed.csv")
        print(f"Cost: ${self.total_cost:.2f}")


if __name__ == "__main__":
    analyzer = ConversationAnalyzer(
        export_path="MasajidChat/result.json",
        output_dir="out_csv"
    )
    analyzer.run()
