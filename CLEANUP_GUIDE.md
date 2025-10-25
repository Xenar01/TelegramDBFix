# Repository Cleanup Guide

## ✅ Files/Folders to KEEP

### **Core Code** (Essential)
- `src/` - All Python scripts
  - `excel_parser.py` ✅
  - `ai_extract.py` ✅
  - `test_api.py` ✅
  - `check_available_models.py` ✅
  - `parse_export.py` (original)
  - `import_to_postgres.py`
  - `schema.sql`
- `requirements.txt` ✅
- `run.bat` / `run.sh` ✅
- `.gitignore` ✅
- `.env` ✅ (but never commit!)
- `.env.example` ✅

### **Essential Documentation**
- `README.md` ✅ - Main docs
- `CLAUDE.md` ✅ - AI assistant guide
- `VERSION_1_SUMMARY.md` ✅ - V1 complete spec

### **Version Planning** (For future projects)
- `V2_IDEAS_AND_SPECS.md` ✅
- `V3_IDEAS_AND_SPECS.md` ✅

### **Data** (Generated, but useful)
- `out_csv/` - Keep outputs
  - `excel_mosques_master.csv` ✅
  - `ai_extracted_mosques.csv` (when complete)
- `MasajidChat/` - Original data (keep!)
  - `result.json` ✅
  - `files/` ✅ (Excel + photos)

### **Git**
- `.git/` ✅ - Version control
- `.claude/` ✅ - Claude Code settings

---

## ❌ Files/Folders You CAN DELETE (Optional)

### **Redundant Documentation** (Nice to have, but not essential)
- `PROJECT_SUMMARY.md` ⚠️ (replaced by VERSION_1_SUMMARY.md)
- `TEST_REPORT.md` ⚠️ (one-time test, done)
- `ANALYSIS_AND_RECOMMENDATION.md` ⚠️ (planning phase, done)
- `TECH_SOLUTION_RECOMMENDATION.md` ⚠️ (merged into V2 specs)
- `SETUP_INSTRUCTIONS.md` ⚠️ (can merge into README)
- `docs/API_SETUP_GUIDE.md` ⚠️ (can merge into README)
- `docs/ONE_WEEK_PLAN.md` ⚠️ (done, historical)

### **Empty/Unused Folders**
- `logs/` ❌ (empty, not used yet)
- `out_db/` ❌ (empty, not used yet)
- `media_organized/` ❌ (empty or from old runs)

---

## 🧹 Recommended Cleanup Actions

### **Option 1: Minimal Cleanup** (Keep everything for reference)
```bash
# Only delete truly empty folders
rm -rf logs/
rm -rf out_db/
```
**Result:** Keep all docs for future reference

---

### **Option 2: Clean Documentation** (Recommended)
```bash
# Delete redundant docs
rm PROJECT_SUMMARY.md
rm TEST_REPORT.md
rm ANALYSIS_AND_RECOMMENDATION.md
rm TECH_SOLUTION_RECOMMENDATION.md
rm SETUP_INSTRUCTIONS.md
rm -rf docs/

# Delete empty folders
rm -rf logs/
rm -rf out_db/

# Clean old media organization (will regenerate)
rm -rf media_organized/
```
**Result:** Cleaner repo, keep only essential docs

---

### **Option 3: Production Ready** (Cleanest)
Keep only what's needed to run V1:

```bash
# Delete all planning/analysis docs
rm PROJECT_SUMMARY.md
rm TEST_REPORT.md
rm ANALYSIS_AND_RECOMMENDATION.md
rm TECH_SOLUTION_RECOMMENDATION.md
rm SETUP_INSTRUCTIONS.md
rm -rf docs/
rm CLEANUP_GUIDE.md  # This file itself

# Keep V2/V3 specs in separate folder
mkdir future_versions/
mv V2_IDEAS_AND_SPECS.md future_versions/
mv V3_IDEAS_AND_SPECS.md future_versions/

# Clean empty folders
rm -rf logs/
rm -rf out_db/
rm -rf media_organized/
```

**Result:** Production-ready V1, future specs organized

---

## 📁 Final Clean Structure (Option 3)

```
TelegramDBFix/
├── .env                          ← API keys
├── .gitignore                    ← Git settings
├── requirements.txt              ← Dependencies
├── run.bat / run.sh             ← Quick start
│
├── README.md                     ← Main documentation
├── CLAUDE.md                     ← AI guide
├── VERSION_1_SUMMARY.md         ← V1 complete spec
│
├── future_versions/
│   ├── V2_IDEAS_AND_SPECS.md    ← Future V2
│   └── V3_IDEAS_AND_SPECS.md    ← Future V3
│
├── src/
│   ├── excel_parser.py          ← Day 1 ✅
│   ├── ai_extract.py            ← Day 2 ✅
│   ├── test_api.py              ← Testing ✅
│   ├── check_available_models.py
│   ├── parse_export.py          ← Original
│   ├── import_to_postgres.py
│   └── schema.sql
│
├── out_csv/                      ← Outputs
│   ├── excel_mosques_master.csv
│   └── ai_extracted_mosques.csv
│
└── MasajidChat/                  ← Original data
    ├── result.json
    └── files/
```

---

## 🎯 My Recommendation

**Choose Option 2** (Clean Documentation):
- Delete redundant planning docs
- Keep V2/V3 specs (you'll use them later)
- Keep VERSION_1_SUMMARY (complete V1 reference)
- Delete empty folders

**Commands:**
```bash
rm PROJECT_SUMMARY.md
rm TEST_REPORT.md
rm ANALYSIS_AND_RECOMMENDATION.md
rm TECH_SOLUTION_RECOMMENDATION.md
rm SETUP_INSTRUCTIONS.md
rm -rf docs/
rm -rf logs/
rm -rf out_db/
rm -rf media_organized/
```

**This reduces clutter while keeping:**
- ✅ All working code
- ✅ Essential docs (README, CLAUDE, VERSION_1_SUMMARY)
- ✅ Future planning (V2, V3 specs)
- ✅ Generated data (out_csv/)

---

## ⚠️ **NEVER DELETE:**

- `.git/` - You'll lose version history!
- `.env` - Contains your API key
- `MasajidChat/` - Original data source
- `src/` - All your code
- `out_csv/` - Your results
- `requirements.txt` - Dependency list
- `VERSION_1_SUMMARY.md` - Complete V1 documentation

---

## 📊 Size Comparison

| What | Before | After Cleanup (Option 2) |
|------|--------|--------------------------|
| **Docs** | 10 files (~150KB) | 3 files (~80KB) |
| **Folders** | 9 folders | 6 folders |
| **Repo Size** | ~2MB (with data) | ~1.9MB |

Not a huge difference, but cleaner structure!

---

**Ready to clean up? Let me know which option you want!**
