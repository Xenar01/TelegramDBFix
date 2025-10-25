# MasajidChat - Telegram Export Data

## 📥 For Team Members: How to Set Up

This folder should contain your **Telegram Desktop export** of the mosque reconstruction chat.

### Step 1: Export from Telegram Desktop

1. Open **Telegram Desktop**
2. Go to the mosque reconstruction group: **"مشروع إعادة إعمار المساجد 🕌"**
3. Click the **three dots** (⋮) → **Export chat history**
4. Configure export settings:
   - ✅ **Format**: JSON
   - ✅ **Photos**: Yes
   - ✅ **Files**: Yes (Excel files)
   - ✅ **Video files**: Optional (if needed)
   - ✅ **Voice messages**: Optional
5. Click **Export**
6. Save the export folder as `MasajidChat`

### Step 2: Place Export in This Folder

After export completes, you should have:

```
MasajidChat/
├── result.json          ← Main export file (REQUIRED)
├── files/               ← Excel files and documents
├── photos/              ← Mosque photos
├── video_files/         ← Videos (optional)
└── voice_messages/      ← Audio (optional)
```

**Important:** Copy the **contents** of the exported folder into this `MasajidChat/` directory.

### Step 3: Verify the Export

Check that `result.json` exists:
```bash
ls MasajidChat/result.json
```

### ⚠️ Note

- This folder is **git-ignored** (not tracked)
- Your export data stays **private** on your machine
- Never commit this folder to GitHub (it's ~15 GB!)
- Each team member needs their own export

### ✅ Ready to Parse

Once `result.json` is in place, run:

```bash
python src/parse_export.py
```

See main [README.md](../README.md) for full instructions.
