# Organized Media Files

This folder contains **mosque photos organized by province and name**.

## 📁 Structure

After running the ETL with media organization enabled:

```
media_organized/
├── ريف دمشق/
│   ├── مسجد دك الباب/
│   │   ├── photo_1.JPG
│   │   ├── photo_2.JPG
│   │   └── photo_3.JPG
│   ├── مسجد الجسر/
│   │   ├── photo_1.JPG
│   │   └── photo_2.JPG
│   └── ...
├── حلب/
│   └── ...
└── درعا/
    └── ...
```

## 🚀 How to Generate

Run the parser **with** media organization:

```bash
python src/parse_export.py
```

Or explicitly enable it:

```bash
python src/parse_export.py --export-path MasajidChat
```

Skip media organization (faster for testing):

```bash
python src/parse_export.py --no-media
```

## 📊 What This Contains

- Original photos from Telegram export
- Organized by: `[Province]/[Mosque Name]/photo_N.ext`
- Copies (not moves) from `MasajidChat/files/`
- Easier browsing for human review

## ⚠️ Git Ignore

This folder is **git-ignored**. Media files are large (100+ MB) and should stay local.

## 💡 Use Cases

- Manual verification of mosque photos
- Creating photo galleries for reports
- Visual inspection before uploading to websites
- Preparing media for Ministry of Awqaf documentation

See [README.md](../README.md) for full workflow.
