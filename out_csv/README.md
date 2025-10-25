# Output Data Files - Clean Dataset

**Last Updated:** October 25, 2025
**Status:** Cleaned and ready for GUI/Database

---

## Core Dataset (USE THIS)

### `conversation_clusters_analyzed.csv` (PRIMARY DATA)
**517 mosques** extracted from Telegram conversation analysis

**Columns:**
- `name` - Mosque name (Arabic)
- `area` - Area/region within province
- `damage_type` - damaged/demolished/unknown
- `confidence` - high/medium/low (AI extraction confidence)
- `province` - Syrian province
- `photo_files` - Semicolon-separated list of photo paths
- `photo_count` - Number of photos
- `maps_urls` - Google Maps links
- `video_files` - Video file paths (if any)
- `message_ids` - Source Telegram message IDs
- `original_text` - Original text from Telegram

**Quality Metrics:**
- 192 mosques with photos (37.1%)
- 221 mosques with maps (42.7%)
- 395 high confidence (76.4%)
- 110 medium confidence (21.3%)
- 12 low confidence (2.3%)

**Usage:** This is your main dataset for the GUI application.

---

## Reference Data

### `provinces.csv`
List of Syrian provinces (9 entries)
- `province_id`
- `name_ar` - Arabic name
- `telegram_topic_id` - Telegram topic ID

### `photos_catalog.csv`
Complete catalog of all 1,368 photos from Telegram export
- `message_id` - Telegram message ID
- `date` - Upload date
- `province` - Province name
- `file_path` - Path to photo file
- `reply_to` - Topic/thread ID

### `maps_catalog.csv`
Complete catalog of all 288 Google Maps links from Telegram
- `message_id` - Telegram message ID
- `province` - Province name
- `maps_url` - Google Maps URL
- `full_text` - Text containing the maps link

### `excel_mosques_master.csv`
Original mosque data from Excel files (570 entries)
- Reference data from Excel spreadsheets
- Includes damage type classifications

### `excel_files.csv`
Metadata about Excel files in the export
- File names, provinces, damage types

---

## Summary Statistics

### `conversation_analysis_stats.txt`
Summary of conversation analysis results:
- Total clusters: 288
- Mosques extracted: 517
- API cost: $0.14
- Breakdown by province

### `excel_summary.txt`
Summary of Excel file processing

---

## Organized Data

### `by_province/` folder
Province-specific CSV files (if generated)

---

## Deleted Files (Obsolete)

The following files were removed as they contained failed matching attempts:
- `mosques_enriched_with_media.csv` (only 2.7% photos matched)
- `mosques_merged_master.csv` (failed merge)
- `mosques_high_confidence.csv` (subset of failed data)
- `ai_extracted_mosques.csv` (old AI extraction)
- `mosques.csv`, `photos.csv`, `locations.csv` (old pipeline)
- All failed matching reports and summaries

---

## Next Steps

1. **For GUI Development:** Use `conversation_clusters_analyzed.csv` as primary data source
2. **For Database Import:** Import from `conversation_clusters_analyzed.csv`
3. **For Media Files:** Reference paths in `photo_files` column (relative to MasajidChat/)
4. **For Validation:** Cross-reference with `excel_mosques_master.csv`

---

## Data Quality Notes

**Strengths:**
- High-quality conversation clustering
- Good photo/maps matching (37-43%)
- Clear province assignments
- Source message traceability

**Areas for Improvement:**
- Some mosques missing photos
- Some missing GPS coordinates
- Could benefit from manual verification of low-confidence entries

**Recommendation:** Build GUI to allow manual verification and enrichment of the 517 mosques.
