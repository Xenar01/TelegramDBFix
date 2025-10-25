# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Mosque Reconstruction Database ETL Pipeline** - Extract, transform, and load mosque damage data from Telegram group exports into structured databases for humanitarian reconstruction efforts in Syria.

### Data Source
- Telegram group: "مشروع إعادة إعمار المساجد 🕌" (Mosque Reconstruction Project)
- Export format: JSON (`MasajidChat/result.json`) with media files (photos, Excel, videos)
- Structure: Multiple Topics (each representing a Syrian province)

### Purpose
Transform semi-structured Telegram messages into a queryable database for:
- Reconstruction planning dashboards
- GIS visualization and mapping
- Donation platform integration
- Ministry of Awqaf official reports

---

## Architecture

### Data Flow
1. **Input**: Telegram Desktop export (JSON + media folders)
2. **Parse**: `src/parse_export.py` extracts provinces, mosques, photos, locations
3. **Output**: Structured CSV files in `out_csv/`
4. **Optional**: Import to PostgreSQL via `src/import_to_postgres.py`
5. **Media**: Photos organized in `media_organized/[province]/[mosque]/`

### Message Pattern Recognition

The ETL identifies mosque entries by this pattern:
```
[Photo messages] → [Text: "مسجد Name\nArea"] → [Google Maps link]
```

Example:
- Messages 52-54: Photos (JPG files)
- Message 55: "مسجد دك الباب\nالزبداني" (Name + Area)
- Message 56: "https://maps.app.goo.gl/..."

**Key Logic** (`parse_export.py:group_mosque_messages()`):
- Look backward up to 20 messages from text to find photos
- Photos must reply to same topic (province)
- Look forward 1 message for Google Maps link
- All messages grouped into one mosque record

---

## Database Schema

### Core Tables
- **provinces**: Syrian provinces (from Telegram Topics)
- **mosques**: Mosque records with name, area, province
- **photos**: Images linked to mosques (with file metadata)
- **locations**: Google Maps links and geocoded coordinates
- **files**: All attachments (Excel, photos) with provenance
- **damage_status**: Classification (damaged vs demolished)
- **message_index**: Source message tracking for verification

See `src/schema.sql` for full PostgreSQL schema.

---

## Common Commands

### Run ETL Pipeline

```bash
# Quick start (Windows)
run.bat

# Quick start (Linux/Mac)
bash run.sh

# Manual execution
python src/parse_export.py

# Custom paths
python src/parse_export.py --export-path MasajidChat --output-dir out_csv

# Skip media organization (faster for testing)
python src/parse_export.py --no-media
```

### Import to PostgreSQL

```bash
# Setup database
createdb mosques
cp .env.example .env
# Edit .env with DB credentials

# Import
python src/import_to_postgres.py

# Re-import without recreating schema
python src/import_to_postgres.py --no-schema
```

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Check outputs
ls out_csv/
wc -l out_csv/*.csv

# Verify media organization
ls media_organized/*/
```

---

## Code Structure

### `src/parse_export.py` (Main ETL)

**Class: `TelegramMosqueParser`**

Key methods:
- `load_export()`: Read `result.json`
- `extract_provinces()`: Find Topics (service messages with `action: topic_created`)
- `group_mosque_messages()`: **Core logic** - pattern matching for mosque entries
- `extract_excel_files()`: Find Excel attachments, classify by damage type (متضررة/مدمرة)
- `organize_media_files()`: Copy photos to `media_organized/[province]/[mosque]/`
- `export_to_csv()`: Generate 5 CSV files (provinces, mosques, locations, photos, excel_files)

**Critical Pattern Matching Logic** (lines ~160-230):
1. Iterate through messages
2. When finding text with format "مسجد X\nY":
   - Look back for photos (same topic, within 20 messages)
   - Look forward for maps link (next message)
   - Group into mosque entry with all metadata
3. Track province via `reply_to_message_id` → topic_id → province

**Text Extraction** (`extract_text_content()`):
- Handles both `string` and `list of objects` formats from Telegram
- Telegram links stored as `[{"type": "link", "text": "url"}]`

### `src/import_to_postgres.py`

**Class: `PostgresImporter`**

Import order (maintains foreign key constraints):
1. provinces
2. mosques (references provinces)
3. locations (references mosques)
4. photos → files (references mosques)
5. excel_files → files

Uses `ON CONFLICT DO NOTHING` to handle re-imports safely.

### `src/schema.sql`

PostgreSQL schema with:
- Foreign key relationships
- Indexes on common query fields (province_id, mosque_id, topic_id)
- CHECK constraints (damage_type)
- Timestamps for all records

---

## Data Quality Notes

### Expected Patterns

**Excel Files**:
- Naming: `[Province] المساجد المتضررة نهائي.xlsx` (damaged)
- Naming: `[Province] المساجد المدمرة نهائي.xlsx` (demolished)
- Each province should have 2 files (damaged + demolished)

**Mosque Text Messages**:
- Line 1: Must contain "مسجد" followed by name
- Line 2: Area/region within province
- May have variations but pattern is consistent

**Photos**:
- JPG files in `MasajidChat/files/` or `photos/`
- Usually 1-5 photos per mosque
- All photos for one mosque sent consecutively

**Topics** (Provinces):
- درعا (Daraa)
- ريف دمشق (Damascus countryside)
- إدلب (Idlib)
- حلب (Aleppo)
- اللاذقية (Latakia)
- حمص (Homs)
- القنيطرة (Quneitra)
- حماة (Hama)
- دير الزور (Deir ez-Zor)

### Common Issues

1. **Missing maps links**: Not all mosques have location data
2. **Photo grouping**: If users don't send photos consecutively, parser may miss them
3. **Text format variations**: Some messages may not follow exact two-line format
4. **Excel file naming**: Variations in spelling (متضررة vs متضرر)

### Validation Checks

After running ETL, verify:
- Province count matches Topics in export
- Each province has mosques assigned
- Photo count seems reasonable
- Excel files classified correctly (damaged/demolished)
- Maps links are valid URLs

---

## Development Patterns

### When modifying the parser:

1. **Test on small dataset first**: Use `--no-media` for faster iterations
2. **Check message grouping**: Add debug prints in `group_mosque_messages()`
3. **Verify CSV output**: Always check `out_csv/*.csv` after changes
4. **Preserve provenance**: Never remove `source_message_id` tracking

### Adding new features:

**Geocoding from Google Maps**:
- Parse `gmaps_url` to extract coordinates
- Use Nominatim or Google Maps API
- Update `locations` table with lat/lng

**Excel parsing**:
- Use `openpyxl` to read Excel files
- Match mosque names between Excel and messages
- Cross-reference damage types

**Incremental sync** (Phase 2):
- Use Telethon/Pyrogram API
- Track last processed `message_id`
- Only parse new messages since last run

### File Paths

All paths in Windows use backslashes (`C:\AI\Projects\...`) but Path objects handle cross-platform automatically.

When copying files:
- Source: `MasajidChat/files/IMG_4656.JPG`
- Destination: `media_organized/ريف دمشق/مسجد دك الباب/photo_1.JPG`

---

## Environment & Dependencies

### Python Packages
- `pandas`: CSV manipulation and analysis
- `openpyxl`: Excel file reading (future feature)
- `psycopg2-binary`: PostgreSQL connection
- `python-dotenv`: Environment variable loading
- `Pillow`: Image processing (future feature)
- `geopy`: Geocoding via Nominatim (future feature)

### Database
- PostgreSQL 12+ (optional, CSV files work standalone)
- Configure via `.env` file (see `.env.example`)

---

## Future Enhancements (Phase 2)

Planned but not implemented:
1. **Telethon userbot**: Real-time sync from Telegram
2. **n8n workflow**: Automated processing on new messages
3. **Geocoding**: Extract lat/lng from Google Maps
4. **Excel integration**: Parse and merge Excel data
5. **Duplicate detection**: Find duplicate mosque entries
6. **GIS export**: GeoJSON/KML for mapping tools
7. **Web dashboard**: Browse and search interface
8. **Image analysis**: Detect damage level from photos (ML)

---

## Testing Strategy

### Unit Testing (not yet implemented)
Should test:
- Text extraction from various formats
- Mosque name/area parsing
- Google Maps link detection
- Province topic mapping

### Integration Testing
Run full pipeline and verify:
```bash
python src/parse_export.py
wc -l out_csv/*.csv
head -5 out_csv/mosques.csv
```

Expected output counts (approximate):
- Provinces: ~9
- Mosques: varies by data collection progress
- Excel files: ~18 (2 per province)

---

## Important Constraints

1. **No sensitive data**: Avoid committing large media files or personal info
2. **Encoding**: All text is UTF-8 (Arabic content)
3. **Source integrity**: Always keep original `MasajidChat/` export
4. **Provenance**: Every record must trace back to source message
5. **Humanitarian context**: Data is for mosque reconstruction planning

---

## Key Files

- `src/parse_export.py`: **Main ETL script** - start here for any changes
- `src/schema.sql`: Database design - modify when adding tables/fields
- `requirements.txt`: Dependencies - update when adding packages
- `.gitignore`: Excludes large media files and output directories
- `README.md`: User-facing documentation
- `CLAUDE.md`: **This file** - for AI code assistance

---

## Tips for AI Code Assistance

When working with this codebase:
1. Always read `MasajidChat/result.json` structure first to understand data
2. Test changes on a subset of messages before full run
3. Check CSV outputs in `out_csv/` to verify parser changes
4. Use `--no-media` flag during development to speed up testing
5. Preserve backward compatibility - existing CSV schema should not break
6. Add logging for debugging (currently uses print statements)
7. Keep functions focused - don't merge parsing logic with DB logic

**Most common task**: Improving `group_mosque_messages()` to handle edge cases in message patterns.
