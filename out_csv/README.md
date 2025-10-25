# Output CSV Files

This folder contains **generated CSV files** from the ETL pipeline.

## 📊 Expected Files

After running `python src/parse_export.py`, you'll find:

```
out_csv/
├── provinces.csv      ← Syrian provinces (Topics)
├── mosques.csv        ← Mosque records with names and areas
├── locations.csv      ← Google Maps links
├── photos.csv         ← Photo metadata linked to mosques
└── excel_files.csv    ← Excel file metadata (damaged/demolished)
```

## 🔍 What's in Each File

### provinces.csv
- Province ID, name (Arabic), Telegram topic ID
- Example: `1,2,درعا,مساجد درعا,2025-08-13T08:32:21`

### mosques.csv
- Mosque ID, province, name, area, photo count
- Example: `1,2,ريف دمشق,مسجد دك الباب,الزبداني,55,2025-08-13T11:32:09,3`

### locations.csv
- Mosque ID, Google Maps URL
- Example: `1,ريف دمشق,مسجد دك الباب,الزبداني,https://maps.app.goo.gl/...`

### photos.csv
- Photo ID, mosque ID, file path, size
- Links photos to specific mosques

### excel_files.csv
- Excel file metadata (damaged vs demolished lists)
- Province, damage type, file path

## ⚠️ Git Ignore

This folder is **git-ignored**. CSV outputs are generated locally and not committed to the repository.

## 📈 Usage

Import CSVs into:
- Excel/LibreOffice for analysis
- PostgreSQL database (see `src/import_to_postgres.py`)
- Python pandas for data processing

See [README.md](../README.md) for more details.
