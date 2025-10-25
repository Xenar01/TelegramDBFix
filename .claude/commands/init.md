# Project Initialization Context

## Project: Mosque Reconstruction Database ETL Pipeline

You are working on **TelegramDBFix** - an ETL pipeline for extracting mosque reconstruction data from Telegram group exports into structured databases for humanitarian reconstruction efforts in Syria.

---

## Current Status

- **Repository**: Clean, all code committed and pushed
- **Branch**: main
- **Latest Updates**: README.md enhanced with bilingual Arabic/English documentation for team collaboration

---

## Project Structure

```
TelegramDBFix/
├── src/
│   ├── parse_export.py       # Main ETL script - extracts mosque data from Telegram JSON
│   ├── import_to_postgres.py # PostgreSQL importer
│   └── schema.sql            # Database schema
├── MasajidChat/              # Telegram export (NOT committed - user's local data)
│   ├── result.json           # Main export file
│   ├── photos/               # Original photos
│   └── files/                # Excel files
├── out_csv/                  # Generated CSV output (git-ignored)
├── media_organized/          # Photos organized by province/mosque (git-ignored)
├── README.md                 # Main documentation (bilingual Arabic/English)
├── CLAUDE.md                 # AI assistant instructions
└── requirements.txt          # Python dependencies
```

---

## Key Information

### Data Source
- **Telegram Group**: "مشروع إعادة إعمار المساجد 🕌" (Mosque Reconstruction Project)
- **Format**: JSON export with media files
- **Structure**: Topics (provinces) → Messages (mosques with photos and locations)

### Core Functionality
The ETL pipeline (`src/parse_export.py`) identifies mosque entries using pattern recognition:
1. **Photos** (1-5 images) → **Text** ("مسجد [Name]\n[Area]") → **Google Maps link**
2. Groups messages by Topic (province)
3. Outputs to CSV files: provinces, mosques, locations, photos, excel_files

### Important Files to Reference
- **CLAUDE.md** - Complete project instructions, architecture, code structure
- **README.md** - User documentation with setup and usage (now bilingual)
- **src/parse_export.py:group_mosque_messages()** - Core pattern matching logic

---

## Common Tasks

### For Code Changes
```bash
# Always pull latest first
git pull

# Make changes to src/ files
# Test with: python src/parse_export.py --no-media

# Commit and push
git add src/
git commit -m "Description of changes"
git push
```

### For Documentation Updates
```bash
# Edit README.md or CLAUDE.md
git add README.md
git commit -m "Update documentation"
git push
```

### For Running ETL
```bash
# Full pipeline (requires MasajidChat/ export locally)
python src/parse_export.py

# Fast testing (skip media organization)
python src/parse_export.py --no-media

# Import to PostgreSQL (optional)
python src/import_to_postgres.py
```

---

## What NOT to Commit
❌ `MasajidChat/**` - Large Telegram export (~15 GB)
❌ `out_csv/**` - Generated output
❌ `media_organized/**` - Organized photos
❌ `logs/**`, `out_db/**` - Runtime artifacts

✅ Only commit: code (`src/`), docs, config templates

---

## Team Context

This project is designed for **multiple team members** who:
1. Clone the repository
2. Export Telegram data locally (each member has their own copy)
3. Run the ETL pipeline on their local machine
4. Only push code changes (not data)

Recent Update: README.md enhanced with Arabic instructions for colleagues explaining:
- How to set up the project
- How to export Telegram data
- How to run the pipeline
- FAQ and troubleshooting
- Team collaboration workflow

---

## GitHub Tools Available

You have **GitHub CLI (gh)** installed. You can:
- Create PRs: `gh pr create`
- Check workflow runs: `gh run list`
- Manage issues: `gh issue list`

---

## Next Steps / Common Requests

1. **Improve pattern matching** - Enhance `group_mosque_messages()` for edge cases
2. **Add geocoding** - Extract lat/lng from Google Maps links
3. **Parse Excel files** - Merge Excel data with message data
4. **Add validation** - Data quality checks and duplicate detection
5. **Create dashboards** - Visualization of mosque data
6. **Set up GitHub Actions** - Automated testing/validation

---

## Reference Links

- **Repository**: https://github.com/Xenar01/TelegramDBFix
- **Main Script**: `src/parse_export.py` (TelegramMosqueParser class)
- **Schema**: `src/schema.sql`
- **Full Project Docs**: `CLAUDE.md`

---

## Important Notes

- All text is UTF-8 encoded (Arabic content)
- Humanitarian project context - handle data responsibly
- Every record must maintain source message provenance
- Pattern matching is the core logic - be careful when modifying

---

**Use this command (`/init`) anytime you need to refresh the project context or start a new session.**
