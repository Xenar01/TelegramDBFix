# 🕌 قاعدة بيانات مشروع إعادة إعمار المساجد
## Mosque Reconstruction Database ETL

**مشروع إعادة إعمار المساجد في سوريا**

نظام لاستخراج وتحويل وتحميل بيانات المساجد المتضررة والمدمرة من مجموعات تيليجرام إلى قاعدة بيانات منظمة لتسهيل التخطيط لإعادة الإعمار، إنشاء الخرائط، ومنصات التبرعات.

---

## 📋 نظرة عامة | Project Overview

### ما هو هذا المشروع؟

هذا المشروع يعالج البيانات المُصدّرة من مجموعة تيليجرام "مشروع إعادة إعمار المساجد 🕌" والتي تحتوي على معلومات المساجد من عدة محافظات سورية. البيانات تشمل:

- **ملفات Excel** تحتوي على قوائم المساجد المتضررة والمدمرة
- **صور** توثّق أضرار المساجد
- **أوصاف نصية** بأسماء المساجد ومواقعها
- **روابط خرائط Google Maps** لتحديد المواقع الجغرافية

البرنامج يحوّل هذه البيانات شبه المنظمة إلى ملفات CSV نظيفة ويمكن استيرادها اختيارياً إلى قاعدة بيانات PostgreSQL للاستعلام المتقدم والتكامل مع أنظمة أخرى.

---

## 🎯 ملخص للزملاء: كيف تبدأ؟ | Quick Summary for Colleagues

### خطوات البدء السريعة (3 خطوات فقط!)

#### 1️⃣ حمّل المشروع
```bash
git clone https://github.com/Xenar01/TelegramDBFix.git
cd TelegramDBFix
pip install -r requirements.txt
```

#### 2️⃣ صدّر بيانات التيليجرام
- افتح **Telegram Desktop**
- اذهب لمجموعة **"مشروع إعادة إعمار المساجد 🕌"**
- اضغط **⋮** ← **Export chat history**
- اختر **JSON** + **Photos** + **Files**
- انسخ المجلد المُصدَّر إلى `MasajidChat/`

#### 3️⃣ شغّل البرنامج
```bash
python src/parse_export.py
```

**النتيجة:**
- ✅ ملفات CSV جاهزة في `out_csv/`
- ✅ صور منظمة في `media_organized/`

---

## 🏗 البنية التقنية | Architecture

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

## 🚀 البداية السريعة | Quick Start

### ✅ المتطلبات الأساسية | Prerequisites

قبل البدء، تأكد من توفر:
- Python 3.8+ (برنامج بايثون)
- Telegram Desktop (تطبيق تيليجرام لسطح المكتب)
- PostgreSQL 12+ (اختياري - لقاعدة البيانات المتقدمة)

---

### 📥 الخطوة 1: تحميل المشروع | Download Project

```bash
# استنساخ المشروع من GitHub
git clone https://github.com/Xenar01/TelegramDBFix.git
cd TelegramDBFix

# تثبيت المكتبات المطلوبة
pip install -r requirements.txt
```

---

### 📤 الخطوة 2: تصدير بيانات التيليجرام | Export Telegram Data

**مهم جداً**: كل عضو في الفريق يحتاج لتصدير بيانات المجموعة محلياً على جهازه.

#### خطوات التصدير:

1. افتح **Telegram Desktop** (تطبيق تيليجرام لسطح المكتب)
2. انتقل إلى مجموعة: **"مشروع إعادة إعمار المساجد 🕌"**
3. اضغط على **⋮** (ثلاث نقاط) ← **Export chat history** (تصدير سجل المحادثة)
4. اختر الإعدادات التالية:
   - **Format**: JSON
   - **Include**:
     - ✅ Photos (الصور)
     - ✅ Files (الملفات - ملفات Excel)
     - ⬜ Videos (اختياري)
     - ⬜ Voice messages (اختياري)
5. احفظ التصدير

6. **انسخ المجلد المُصدَّر** إلى مجلد `MasajidChat/` داخل المشروع

#### البنية المطلوبة:
```
MasajidChat/
├── result.json          ← ملف JSON الرئيسي (مطلوب)
├── files/               ← ملفات Excel والمرفقات
├── photos/              ← صور المساجد
├── video_files/         ← (اختياري)
└── voice_messages/      ← (اختياري)
```

**📖 للمزيد من التفاصيل، راجع:** [MasajidChat/README.md](MasajidChat/README.md)

---

### ⚙️ الخطوة 3: تشغيل البرنامج | Run the ETL Pipeline

بعد تصدير البيانات، شغّل البرنامج:

```bash
# تشغيل البرنامج الرئيسي
python src/parse_export.py
```

**النتائج:**
- ملفات CSV في مجلد `out_csv/`
- صور منظمة حسب المحافظة والمسجد في `media_organized/`

#### أوامر إضافية:

```bash
# استخدام مسارات مخصصة
python src/parse_export.py --export-path MasajidChat --output-dir out_csv

# تخطي تنظيم الصور (أسرع للاختبار)
python src/parse_export.py --no-media
```

---

### 🗄️ الخطوة 4: الاستيراد لقاعدة البيانات (اختياري) | Import to PostgreSQL

إذا كنت تريد استخدام قاعدة بيانات متقدمة:

```bash
# إنشاء قاعدة البيانات
createdb mosques

# نسخ ملف الإعدادات
cp .env.example .env
# عدّل ملف .env بمعلومات قاعدة البيانات

# استيراد البيانات
python src/import_to_postgres.py
```

---

## 👥 العمل الجماعي | Team Collaboration

### 📌 نقاط مهمة للفريق | Important Notes

هذا المشروع مصمم ليعمل عليه عدة أشخاص **بدون رفع الملفات الكبيرة** إلى GitHub.

#### ✅ ما الذي يُرفع لـ GitHub؟
- الأكواد البرمجية (`src/`)
- الوثائق (`README.md`, `CLAUDE.md`)
- ملفات الإعدادات (`.env.example`, `.gitignore`)

#### 🔒 ما الذي لا يُرفع لـ GitHub؟ (يبقى على جهازك)
- `MasajidChat/**` - تصدير التيليجرام (~15 GB)
- `out_csv/**` - ملفات CSV الناتجة
- `out_db/**` - تصديرات قاعدة البيانات
- `media_organized/**` - الصور المنظمة
- `logs/**` - سجلات التشغيل

**كل عضو في الفريق يعمل على نسخته الخاصة من البيانات محلياً.**

---

### 🔄 سير العمل اليومي | Daily Workflow

1. **سحب آخر التحديثات**: `git pull`
2. **إجراء التعديلات** على الأكواد أو الوثائق
3. **الاختبار محلياً** باستخدام تصدير التيليجرام الخاص بك
4. **رفع التعديلات** (الأكواد فقط - لا ترفع البيانات!)
   ```bash
   git add src/
   git commit -m "وصف التعديل"
   git push
   ```

---

### 📊 ماذا سأحصل بعد تشغيل البرنامج؟ | Output Files

بعد تشغيل `python src/parse_export.py`، ستحصل على:

#### 1️⃣ ملفات CSV منظمة في `out_csv/`:

**provinces.csv** - قائمة المحافظات
```csv
id,topic_id,name_ar,topic_title,created_at
1,2,درعا,مساجد درعا,2025-08-13T08:32:21
2,3,ريف دمشق,مساجد ريف دمشق,2025-08-13T09:15:30
```

**mosques.csv** - بيانات المساجد
```csv
mosque_id,province_id,province_name,mosque_name,area_name,source_message_id,date,photo_count
1,2,ريف دمشق,مسجد دك الباب,الزبداني,55,2025-08-13T11:32:09,3
```

**locations.csv** - روابط المواقع
```csv
mosque_id,province_name,mosque_name,area_name,gmaps_url
1,ريف دمشق,مسجد دك الباب,الزبداني,https://maps.app.goo.gl/Ah9PHvv6DXYEaZZ86
```

**photos.csv** - معلومات الصور
```csv
photo_id,mosque_id,province_name,mosque_name,file_path,file_name,file_size,message_id
1,1,ريف دمشق,مسجد دك الباب,files/IMG_4656.JPG,IMG_4656.JPG,5942448,52
```

**excel_files.csv** - ملفات Excel المرفقة
```csv
file_id,province_id,province_name,damage_type,file_name,file_path,file_size,message_id
1,1,درعا,demolished,مساجد درعا مدمرة نهائي.xlsx,files/...,119144,26
```

#### 2️⃣ الصور منظمة في `media_organized/`:
```
media_organized/
├── درعا/
│   ├── مسجد الحراك/
│   │   ├── photo_1.jpg
│   │   └── photo_2.jpg
│   └── مسجد الصنمين/
│       └── photo_1.jpg
├── ريف دمشق/
│   └── مسجد دك الباب/
│       ├── photo_1.jpg
│       ├── photo_2.jpg
│       └── photo_3.jpg
└── حلب/
    └── ...
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

## ❓ الأسئلة الشائعة | FAQ

### س: أين أجد ملفات CSV الناتجة؟
**ج:** في مجلد `out_csv/` داخل المشروع. إذا لم يظهر المجلد، تأكد من تشغيل البرنامج أولاً.

### س: هل يجب أن أرفع مجلد `MasajidChat/` إلى GitHub؟
**ج:** **لا، إطلاقاً!** هذا المجلد يحتوي على بيانات ضخمة وهو مُستثنى تلقائياً عبر `.gitignore`.

### س: كيف أتأكد من نجاح عملية المعالجة؟
**ج:** افحص ملفات CSV:
```bash
# عدد السجلات في كل ملف
wc -l out_csv/*.csv

# عرض أول 5 سطور من ملف المساجد
head -5 out_csv/mosques.csv
```

### س: البرنامج لا يجد ملف `result.json`؟
**ج:** تأكد من:
1. مجلد `MasajidChat/` موجود في نفس مستوى المشروع
2. ملف `result.json` موجود داخل `MasajidChat/`
3. إذا كان التصدير في مكان آخر، استخدم:
   ```bash
   python src/parse_export.py --export-path "مسار/التصدير/الخاص/بك"
   ```

### س: هل يمكن تشغيل البرنامج على Windows؟
**ج:** نعم! البرنامج يعمل على Windows, Mac, Linux.

### س: كم من الوقت يستغرق البرنامج؟
**ج:**
- بدون تنظيم الصور (`--no-media`): 1-3 دقائق
- مع تنظيم الصور: 5-15 دقيقة (حسب عدد الصور)

---

## 🧪 الفحص والتحقق | Testing & Validation

### فحص النتائج | Verify Output

```bash
# عدد السجلات
wc -l out_csv/*.csv

# عرض المحافظات
head out_csv/provinces.csv

# فحص تنظيم الصور
ls -R media_organized/ | head -20

# التحقق من ملفات Excel
head out_csv/excel_files.csv
```

### قائمة التحقق من جودة البيانات | Data Quality Checklist

- [ ] كل محافظة لديها ملفي Excel (متضررة + مدمرة)؟
- [ ] أسماء المساجد تتبع نمط "مسجد [الاسم]"؟
- [ ] كل صورة مرتبطة بسجل مسجد؟
- [ ] روابط الخرائط صالحة (Google Maps)؟
- [ ] لا توجد سجلات مكررة (اسم + منطقة)؟

---

## 🤝 Contributing

Future contributors should:

1. **Understand the pattern**: Read message grouping logic in `parse_export.py`
2. **Test on sample data**: Don't run on full export until logic is verified
3. **Preserve provenance**: Always keep `source_message_id` references
4. **Document changes**: Update this README for new features

---

## 🔧 استكشاف الأخطاء | Troubleshooting

### خطأ: `FileNotFoundError: result.json not found`

**الحل:**
```bash
# تأكد من وجود الملف
ls MasajidChat/result.json

# إذا كان المجلد بمكان آخر
python src/parse_export.py --export-path "المسار/الصحيح"
```

### خطأ: `ModuleNotFoundError: No module named 'pandas'`

**الحل:**
```bash
# أعد تثبيت المكتبات
pip install -r requirements.txt
```

### خطأ في الاتصال بقاعدة البيانات PostgreSQL

**الحل:**
1. تأكد من تشغيل PostgreSQL: `pg_isready`
2. افحص ملف `.env` - تأكد من صحة المعلومات
3. جرب الاتصال يدوياً: `psql -U postgres`

### البرنامج يعمل ببطء شديد

**الحل:**
```bash
# تخطي تنظيم الصور للإسراع
python src/parse_export.py --no-media
```

### لا توجد صور في `media_organized/`

**السبب المحتمل:**
- استخدمت العلم `--no-media`
- الصور غير موجودة في تصدير التيليجرام

**الحل:**
```bash
# أعد التشغيل بدون --no-media
python src/parse_export.py
```

---

## 📞 الدعم والمساعدة | Support

للمساعدة في:
- **مشاكل تصدير التيليجرام**: راجع دليل Telegram Desktop
- **إعداد قاعدة البيانات**: افحص ملف `.env` ومعلومات الاتصال
- **أخطاء المعالجة**: راجع نمط الرسائل في `result.json`
- **بيانات مفقودة**: تأكد أن التصدير شمل جميع المواضيع (Topics)

**للتواصل مع الفريق:**
- افتح Issue على GitHub: [github.com/Xenar01/TelegramDBFix/issues](https://github.com/Xenar01/TelegramDBFix/issues)

---

## 🔍 كيف يعمل البرنامج؟ | How It Works

### نمط التعرف على المساجد | Message Pattern Recognition

البرنامج يحدد سجلات المساجد من خلال هذا النمط:

```
مجموعة الرسائل:
  1️⃣ صور (1-5 صور للمسجد)
  2️⃣ نص: "مسجد [الاسم]\n[المنطقة]"
  3️⃣ رابط خرائط Google Maps

مثال:
  📷 [صورة 1] [صورة 2] [صورة 3]
  📝 "مسجد الجسر
      الزبداني"
  🗺️ "https://maps.app.goo.gl/..."
```

### منطق الاستخراج | Extraction Logic

1. **المواضيع ← المحافظات**: كل موضوع (Topic) يمثل محافظة
   - "مساجد درعا" → درعا
   - "مساجد حلب" → حلب

2. **الرسائل النصية ← المساجد**:
   - السطر الأول: اسم المسجد (يحتوي "مسجد")
   - السطر الثاني: المنطقة داخل المحافظة

3. **الصور السابقة ← صور المسجد**:
   - البرنامج يبحث عن الصور قبل النص (حتى 20 رسالة)
   - فقط الصور من نفس الموضوع (Topic)

4. **الرسالة التالية ← موقع المسجد**:
   - البرنامج يبحث عن رابط خرائط بعد النص مباشرة

---

## 📜 الترخيص | License

هذا المشروع لأغراض إنسانية (إعادة إعمار المساجد في سوريا).
يجب التعامل مع البيانات بمسؤولية واستخدامها فقط لأغراض التخطيط لإعادة الإعمار والتنسيق مع وزارة الأوقاف.

---

## 🙏 شكر وتقدير | Acknowledgments

- **Telegram Desktop** لوظيفة التصدير
- **جامعو البيانات الميدانيون** عبر المحافظات السورية
- **منسقو المشروع** الذين يديرون جهود إعادة الإعمار
- جميع المساهمين في **مشروع إعادة إعمار المساجد 🕌**

---

## 📌 معلومات المشروع | Project Info

**آخر تحديث**: 2025-01-13
**الإصدار**: 1.0.0
**الحالة**: المرحلة الأولى - ETL Pipeline ✅

**المستودع**: [github.com/Xenar01/TelegramDBFix](https://github.com/Xenar01/TelegramDBFix)

---

> 🕌 **"إِنَّمَا يَعْمُرُ مَسَاجِدَ اللَّهِ مَنْ آمَنَ بِاللَّهِ وَالْيَوْمِ الْآخِرِ"** - سورة التوبة
>
> *May Allah accept this effort and aid in the reconstruction of His houses.*
