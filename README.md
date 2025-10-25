# 🕌 Telegram Mosque Database ETL

**Mosque Reconstruction Project (مشروع إعادة إعمار المساجد)**

Extract, transform, and load mosque damage data from Telegram group exports into a structured database for reconstruction planning, GIS visualization, and donation platforms.

---

## 📋 Project Overview

This project processes exported Telegram group data containing mosque reconstruction information from multiple Syrian provinces. The data includes:

- **Excel files** with lists of damaged and demolished mosques
- **Photos** of mosque damage
- **Text descriptions** with mosque names and locations
- **Google Maps links** for geolocation

The ETL pipeline transforms this semi-structured data into clean CSV files and optionally imports it into PostgreSQL for advanced querying and integration with other systems.

---

## 🏗 Architecture

```
Telegram Export (JSON + Media)
    ↓
parse_export.py (ETL)
    ↓
CSV Files (out_csv/)
    ↓
PostgreSQL Database (optional)
    ↓
Future: Dashboards, GIS Maps, Donation Platforms
```

### Data Flow

1. **Export**: Telegram Desktop export creates `MasajidChat/result.json` + media files
2. **Parse**: Python ETL script extracts provinces, mosques, photos, and Excel files
3. **Transform**: Groups messages by pattern (photos → text → maps link)
4. **Load**: Outputs to CSV and optionally PostgreSQL
5. **Organize**: Copies photos to structured folders by province/mosque

---

## 📊 Database Schema

### Tables

| Table | Description |
|-------|-------------|
| `provinces` | Syrian provinces (from Telegram Topics) |
| `mosques` | Core mosque records with name and area |
| `damage_status` | Classification (damaged/demolished) |
| `photos` | Mosque photos linked to records |
| `locations` | Google Maps links and geocoded coordinates |
| `files` | All file attachments (Excel, photos) |
| `message_index` | Provenance tracking (source messages) |

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- (Optional) PostgreSQL 12+
- Telegram Desktop export data

### 2. Installation

```bash
# Clone or navigate to project
cd TelegramDBFix

# Install dependencies
pip install -r requirements.txt

# Copy environment template (if using PostgreSQL)
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Run ETL Pipeline

```bash
# Parse Telegram export and generate CSV files
python src/parse_export.py

# With custom paths
python src/parse_export.py --export-path MasajidChat --output-dir out_csv

# Skip media organization (faster)
python src/parse_export.py --no-media
```

### 4. Import to PostgreSQL (Optional)

```bash
# Create database
createdb mosques

# Import data
python src/import_to_postgres.py

# Skip schema creation if already exists
python src/import_to_postgres.py --no-schema
```

---

## 📂 Directory Structure

```
TelegramDBFix/
├── MasajidChat/              # Telegram export (not committed)
│   ├── result.json           # Main export file
│   ├── photos/               # Original photos
│   ├── files/                # Excel and other attachments
│   ├── video_files/
│   └── voice_messages/
├── src/
│   ├── parse_export.py       # Main ETL script
│   ├── import_to_postgres.py # PostgreSQL importer
│   └── schema.sql            # Database schema
├── out_csv/                  # Generated CSV files
│   ├── provinces.csv
│   ├── mosques.csv
│   ├── locations.csv
│   ├── photos.csv
│   └── excel_files.csv
├── media_organized/          # Photos organized by province/mosque
│   └── [province]/[mosque]/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📝 Message Pattern Recognition

The parser identifies mosque entries using this pattern:

```
Message Group:
  1. Photos (1-5 images)
  2. Text: "مسجد [Name]\n[Area]"
  3. Google Maps link

Example:
  [Photo 1] [Photo 2] [Photo 3]
  "مسجد الجسر
   الزبداني"
  "https://maps.app.goo.gl/..."
```

**Extraction Logic:**
- Topics → Provinces (e.g., "مساجد درعا" → Daraa)
- Text messages with two lines → Mosque name + area
- Preceding photos in same topic → Mosque photos
- Following maps link → Location

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mosques
DB_USER=postgres
DB_PASSWORD=your_password

# Geocoding (future feature)
NOMINATIM_USER_AGENT=MosqueReconstructionProject
```

---

## 📈 Output Files

### CSV Files

**provinces.csv**
```csv
id,topic_id,name_ar,topic_title,created_at
1,2,درعا,مساجد درعا,2025-08-13T08:32:21
```

**mosques.csv**
```csv
mosque_id,province_id,province_name,mosque_name,area_name,source_message_id,date,photo_count
1,3,ريف دمشق,مسجد دك الباب,الزبداني,55,2025-08-13T11:32:09,3
```

**locations.csv**
```csv
mosque_id,province_name,mosque_name,area_name,gmaps_url
1,ريف دمشق,مسجد دك الباب,الزبداني,https://maps.app.goo.gl/Ah9PHvv6DXYEaZZ86
```

**photos.csv**
```csv
photo_id,mosque_id,province_name,mosque_name,file_path,file_name,file_size,message_id
1,1,ريف دمشق,مسجد دك الباب,files/IMG_4656.JPG,IMG_4656.JPG,5942448,52
```

**excel_files.csv**
```csv
file_id,province_id,province_name,damage_type,file_name,file_path,file_size,message_id,date
1,1,درعا,demolished,مساجد درعا مدمرة نهائي.xlsx,files/...,119144,26,2025-08-13T08:37:45
```

---

## 🛠 Development Workflow

### Phase 1: Immediate Archiving (Current)

✅ Export Telegram group data
✅ Run ETL pipeline
✅ Generate CSV files
✅ Organize photos by mosque
⬜ Verify data quality
⬜ Import to PostgreSQL

### Phase 2: Future Enhancements

- **Geocoding**: Use Nominatim to extract lat/lng from Google Maps links
- **Excel Integration**: Parse Excel files and merge with message data
- **Telethon Bot**: Incremental sync for new messages
- **n8n Workflow**: Real-time processing pipeline
- **GIS Export**: GeoJSON/KML for mapping tools
- **Web Dashboard**: Browse and search mosques
- **Duplicate Detection**: Identify duplicate entries

---

## 📊 Usage Examples

### Query with PostgreSQL

```sql
-- Count mosques by province
SELECT p.name_ar, COUNT(m.id) as mosque_count
FROM provinces p
LEFT JOIN mosques m ON p.id = m.province_id
GROUP BY p.name_ar
ORDER BY mosque_count DESC;

-- Find mosques with photos and locations
SELECT m.mosque_name, m.area_name, l.gmaps_url, COUNT(ph.id) as photo_count
FROM mosques m
JOIN locations l ON m.id = l.mosque_id
LEFT JOIN photos ph ON m.id = ph.mosque_id
GROUP BY m.id, m.mosque_name, m.area_name, l.gmaps_url;

-- Search by province and damage type
SELECT m.*, ds.damage_type
FROM mosques m
JOIN provinces p ON m.province_id = p.id
JOIN damage_status ds ON m.id = ds.mosque_id
WHERE p.name_ar = 'حلب' AND ds.damage_type = 'demolished';
```

### Analyze with Pandas

```python
import pandas as pd

# Load data
mosques = pd.read_csv('out_csv/mosques.csv')
locations = pd.read_csv('out_csv/locations.csv')

# Count by province
province_counts = mosques['province_name'].value_counts()

# Mosques with locations
with_maps = mosques.merge(locations, on='mosque_id')
coverage = len(with_maps) / len(mosques) * 100
print(f"Location coverage: {coverage:.1f}%")

# Filter by area
zabadani = mosques[mosques['area_name'] == 'الزبداني']
```

---

## 🔐 Data Governance

- **Source Tracking**: Every record includes `source_message_id`
- **Provenance**: Full message index with timestamps and users
- **Backup**: Keep original `MasajidChat/` export intact
- **Privacy**: Sanitize personal data before public sharing
- **Versioning**: Git tracks schema and script changes

---

## 🧪 Testing

### Verify Export

```bash
# Check record counts
wc -l out_csv/*.csv

# Verify provinces match topics
head out_csv/provinces.csv

# Check photo organization
ls -R media_organized/ | head -20

# Validate Excel files
head out_csv/excel_files.csv
```

### Data Quality Checks

- [ ] All provinces have both damaged + demolished Excel files?
- [ ] Mosque names follow "مسجد [name]" pattern?
- [ ] All photos have corresponding mosque records?
- [ ] Maps links are valid Google Maps URLs?
- [ ] No duplicate mosque entries (name + area)?

---

## 🤝 Contributing

Future contributors should:

1. **Understand the pattern**: Read message grouping logic in `parse_export.py`
2. **Test on sample data**: Don't run on full export until logic is verified
3. **Preserve provenance**: Always keep `source_message_id` references
4. **Document changes**: Update this README for new features

---

## 📞 Support

For issues with:
- **Telegram export**: See Telegram Desktop documentation
- **Database setup**: Check PostgreSQL connection in `.env`
- **Parsing errors**: Review message pattern in `result.json`
- **Missing data**: Verify Telegram export included all Topics

---

## 📜 License

This project is for humanitarian purposes (mosque reconstruction in Syria). Data should be handled responsibly and used only for reconstruction planning and coordination with the Ministry of Awqaf.

---

## 🙏 Acknowledgments

- Telegram Desktop for export functionality
- Field data collectors across Syrian provinces
- Project coordinators managing the reconstruction effort

---

**Last Updated**: 2025-01-13
**Version**: 1.0.0
**Status**: Phase 1 - Initial ETL Pipeline ✅
