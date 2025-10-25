# PRODUCTION SYSTEM PLAN - Mosque Database Management

**Version:** 1.5 (GUI + Database System)
**Date:** October 25, 2025
**Status:** Planning Phase

---

## 🎯 User Requirements

Based on your clarification:

> "My goal from the GUI is to:
> 1. Load new telegram chat folder from it
> 2. Display results in useful way
> 3. Create abilities to reorganize things through GUI when auditing
> 4. Any change in GUI applies to database
> 5. Last goal: have a correct SQL database we can use in another projects"

---

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (GUI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Load Telegram│  │ Browse/Search│  │ Audit/Edit   │      │
│  │ Export       │  │ Mosques      │  │ Data         │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              APPLICATION LAYER (Python Backend)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Telegram     │  │ Data         │  │ Database     │      │
│  │ Parser       │  │ Validator    │  │ Manager      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATA LAYER (PostgreSQL)                    │
│                                                             │
│  Tables: mosques, provinces, photos, locations,            │
│          excel_files, ai_extractions, audit_log            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  FILE SYSTEM (Organized)                    │
│                                                             │
│  organized_data/{province}/{mosque}/photos/                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ SQL Database Schema

### Design Principles
1. **Normalized structure** - Avoid duplication
2. **Audit trail** - Track all changes
3. **Flexible** - Support future enhancements
4. **PostgreSQL** - Production-grade RDBMS

### Core Tables

```sql
-- ============================================
-- MOSQUE RECONSTRUCTION DATABASE SCHEMA
-- PostgreSQL 12+
-- ============================================

-- 1. Provinces (Syrian administrative regions)
CREATE TABLE provinces (
    province_id SERIAL PRIMARY KEY,
    name_ar VARCHAR(100) NOT NULL UNIQUE,
    name_en VARCHAR(100),
    telegram_topic_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Mosques (Core entity)
CREATE TABLE mosques (
    mosque_id SERIAL PRIMARY KEY,
    province_id INTEGER REFERENCES provinces(province_id) ON DELETE CASCADE,

    -- Names
    name_ar VARCHAR(200) NOT NULL,
    name_normalized VARCHAR(200), -- For searching
    area VARCHAR(200),

    -- Damage info
    damage_type VARCHAR(20) CHECK (damage_type IN ('damaged', 'demolished', 'unknown')),
    damage_severity INTEGER CHECK (damage_severity BETWEEN 1 AND 10),

    -- Data sources
    source VARCHAR(50) CHECK (source IN ('excel', 'ai', 'excel+ai', 'manual')),
    excel_source VARCHAR(200),
    telegram_cluster_id INTEGER,
    confidence VARCHAR(20) CHECK (confidence IN ('high', 'medium', 'low')),

    -- Metadata
    notes TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of INTEGER REFERENCES mosques(mosque_id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    updated_by VARCHAR(100) DEFAULT 'system'
);

-- Indexes for performance
CREATE INDEX idx_mosques_province ON mosques(province_id);
CREATE INDEX idx_mosques_name ON mosques(name_normalized);
CREATE INDEX idx_mosques_damage ON mosques(damage_type);
CREATE INDEX idx_mosques_verified ON mosques(is_verified);

-- 3. Photos
CREATE TABLE photos (
    photo_id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(mosque_id) ON DELETE CASCADE,

    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    width INTEGER,
    height INTEGER,

    telegram_message_id INTEGER,
    uploaded_date TIMESTAMP,

    is_primary BOOLEAN DEFAULT FALSE,
    caption TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_photos_mosque ON photos(mosque_id);

-- 4. Locations (GPS coordinates)
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(mosque_id) ON DELETE CASCADE,

    google_maps_url VARCHAR(500),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    source VARCHAR(50) CHECK (source IN ('telegram', 'manual', 'geocoded')),
    accuracy VARCHAR(20),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_locations_mosque ON locations(mosque_id);
CREATE INDEX idx_locations_coords ON locations(latitude, longitude);

-- 5. Videos
CREATE TABLE videos (
    video_id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(mosque_id) ON DELETE CASCADE,

    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    duration INTEGER,

    telegram_message_id INTEGER,
    uploaded_date TIMESTAMP,

    caption TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_videos_mosque ON videos(mosque_id);

-- 6. Telegram Messages (Original data provenance)
CREATE TABLE telegram_messages (
    message_id INTEGER PRIMARY KEY,
    cluster_id INTEGER,
    topic_id INTEGER,

    date TIMESTAMP,
    from_user VARCHAR(200),

    text TEXT,
    message_type VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_telegram_cluster ON telegram_messages(cluster_id);
CREATE INDEX idx_telegram_topic ON telegram_messages(topic_id);

-- 7. Excel Import Log
CREATE TABLE excel_imports (
    import_id SERIAL PRIMARY KEY,
    file_name VARCHAR(200),
    province_id INTEGER REFERENCES provinces(province_id),
    damage_type VARCHAR(20),

    rows_imported INTEGER,
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imported_by VARCHAR(100)
);

-- 8. Audit Log (Track ALL changes)
CREATE TABLE audit_log (
    audit_id SERIAL PRIMARY KEY,

    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(20) CHECK (action IN ('INSERT', 'UPDATE', 'DELETE', 'MERGE')),

    old_values JSONB,
    new_values JSONB,

    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    reason TEXT,
    ip_address INET
);

CREATE INDEX idx_audit_table ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_user ON audit_log(changed_by);
CREATE INDEX idx_audit_date ON audit_log(changed_at);

-- 9. Users (For GUI authentication)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,

    role VARCHAR(20) CHECK (role IN ('admin', 'editor', 'viewer')),

    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Data Quality Issues
CREATE TABLE quality_issues (
    issue_id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(mosque_id),

    issue_type VARCHAR(50) CHECK (issue_type IN
        ('missing_location', 'missing_photos', 'duplicate',
         'name_unclear', 'province_mismatch', 'other')),

    description TEXT,
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high')),

    status VARCHAR(20) CHECK (status IN ('open', 'in_progress', 'resolved', 'ignored')),
    assigned_to VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_notes TEXT
);

CREATE INDEX idx_quality_mosque ON quality_issues(mosque_id);
CREATE INDEX idx_quality_status ON quality_issues(status);
```

### Views for Common Queries

```sql
-- Complete mosque view (most commonly used)
CREATE VIEW v_mosques_complete AS
SELECT
    m.mosque_id,
    m.name_ar,
    m.area,
    p.name_ar AS province,
    m.damage_type,
    m.source,
    m.confidence,
    m.is_verified,

    COUNT(DISTINCT ph.photo_id) AS photo_count,
    COUNT(DISTINCT v.video_id) AS video_count,
    COUNT(DISTINCT l.location_id) AS location_count,

    l.google_maps_url,
    l.latitude,
    l.longitude,

    m.created_at,
    m.updated_at
FROM mosques m
LEFT JOIN provinces p ON m.province_id = p.province_id
LEFT JOIN photos ph ON m.mosque_id = ph.mosque_id
LEFT JOIN videos v ON m.mosque_id = v.mosque_id
LEFT JOIN locations l ON m.mosque_id = l.mosque_id
GROUP BY m.mosque_id, p.name_ar, l.google_maps_url, l.latitude, l.longitude;

-- Province statistics
CREATE VIEW v_province_stats AS
SELECT
    p.name_ar AS province,
    COUNT(m.mosque_id) AS total_mosques,
    SUM(CASE WHEN m.damage_type = 'damaged' THEN 1 ELSE 0 END) AS damaged,
    SUM(CASE WHEN m.damage_type = 'demolished' THEN 1 ELSE 0 END) AS demolished,
    SUM(CASE WHEN m.is_verified THEN 1 ELSE 0 END) AS verified,
    COUNT(DISTINCT ph.photo_id) AS total_photos,
    SUM(CASE WHEN l.location_id IS NOT NULL THEN 1 ELSE 0 END) AS with_location
FROM provinces p
LEFT JOIN mosques m ON p.province_id = m.province_id
LEFT JOIN photos ph ON m.mosque_id = ph.mosque_id
LEFT JOIN locations l ON m.mosque_id = l.mosque_id
GROUP BY p.province_id, p.name_ar;

-- Data quality dashboard
CREATE VIEW v_quality_dashboard AS
SELECT
    'Missing Photos' AS issue,
    COUNT(*) AS count
FROM mosques m
LEFT JOIN photos p ON m.mosque_id = p.mosque_id
WHERE p.photo_id IS NULL

UNION ALL

SELECT
    'Missing Location' AS issue,
    COUNT(*) AS count
FROM mosques m
LEFT JOIN locations l ON m.mosque_id = l.mosque_id
WHERE l.location_id IS NULL

UNION ALL

SELECT
    'Unverified' AS issue,
    COUNT(*) AS count
FROM mosques
WHERE NOT is_verified

UNION ALL

SELECT
    'Low Confidence' AS issue,
    COUNT(*) AS count
FROM mosques
WHERE confidence = 'low';
```

---

## 🎨 GUI Application Design

### Technology Stack

**Option 1: Desktop Application (Recommended)**
- **Framework:** PyQt6 or PySide6 (Python Qt bindings)
- **Why:** Native performance, no browser needed, best for file operations
- **Package size:** ~50MB standalone

**Option 2: Web Application**
- **Framework:** Flask/FastAPI + React or Vue.js
- **Why:** Accessible from anywhere, easier updates
- **Requires:** Running web server

**Recommendation:** Start with PyQt6 (desktop) - easier for file operations, local database, and your use case.

### GUI Components and Features

#### 1. Main Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Mosque Database Management v1.5              [User: Admin] [×] │
├─────────────────────────────────────────────────────────────────┤
│ [File] [Import] [Export] [Tools] [Help]                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌───────────────────────────────────┐    │
│  │  Province Tree  │  │   Mosque List View                │    │
│  │                 │  │                                   │    │
│  │  □ All (1,053)  │  │  [Search: ____] [Filter ▼]       │    │
│  │  ├─ ريف دمشق    │  │                                   │    │
│  │  │  (120)       │  │  ID  │ Name │ Area │ Photos│GPS  │    │
│  │  ├─ حماة (250)  │  │  001 │ مسجد │ حرستا│  3   │ ✓   │    │
│  │  ├─ إدلب (214)  │  │  002 │ ...  │ ... │  0   │ ✗   │    │
│  │  └─ ...         │  │  ...                             │    │
│  │                 │  │                                   │    │
│  │ Filters:        │  │  [< Prev] Page 1/21 [Next >]     │    │
│  │ ☑ Verified      │  │                                   │    │
│  │ ☑ Has Photos    │  └───────────────────────────────────┘    │
│  │ ☐ Has Location  │                                           │
│  │                 │  ┌───────────────────────────────────┐    │
│  │ Damage Type:    │  │   Mosque Details Panel            │    │
│  │ ☑ Damaged       │  │                                   │    │
│  │ ☑ Demolished    │  │  Name: مسجد حذيفة بن اليمان       │    │
│  │ ☐ Unknown       │  │  Area: حرستا                       │    │
│  │                 │  │  Province: ريف دمشق               │    │
│  └─────────────────┘  │  Damage: Damaged                  │    │
│                       │                                   │    │
│                       │  Photos (3):                      │    │
│                       │  [🖼️] [🖼️] [🖼️]                     │    │
│                       │                                   │    │
│                       │  Location: 📍 Show on Map         │    │
│                       │                                   │    │
│                       │  [Edit] [Mark as Verified]        │    │
│                       └───────────────────────────────────┘    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Status: 1,053 mosques │ 450 verified │ Last import: 2025-...  │
└─────────────────────────────────────────────────────────────────┘
```

#### 2. Import Telegram Dialog

**Purpose:** Load new Telegram export folder and process it

```
┌──────────────────────────────────────────────────────┐
│  Import Telegram Export                         [×]  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Step 1: Select Telegram Export Folder              │
│  ┌────────────────────────────────────────────────┐ │
│  │ C:\Downloads\TelegramExport\MasajidChat        │ │
│  │                                      [Browse]  │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  Step 2: Verify Export Contents                     │
│  ✓ result.json found (2,615 messages)               │
│  ✓ files/ folder found (1,367 files)                │
│  ✓ 10 topics detected                               │
│                                                      │
│  Step 3: Processing Options                         │
│  ☑ Run AI analysis (Claude API)                     │
│  ☑ Extract photos and videos                        │
│  ☑ Extract GPS locations                            │
│  ☑ Match with existing Excel data                   │
│  ☐ Auto-merge duplicates                            │
│                                                      │
│  Estimated cost: $0.15                               │
│  Estimated time: 15 minutes                          │
│                                                      │
│  [Cancel]                          [Start Import]   │
└──────────────────────────────────────────────────────┘
```

**Processing Progress Dialog:**

```
┌──────────────────────────────────────────────────────┐
│  Processing Telegram Export...                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Current Step: AI Analysis (288 clusters)           │
│  Progress: ████████████░░░░░░░░ 65% (188/288)       │
│                                                      │
│  ✓ Loaded export                                    │
│  ✓ Extracted topics                                 │
│  ✓ Clustered messages                               │
│  ⏳ Analyzing with AI... (cluster 188)              │
│  ⏺ Match with Excel                                 │
│  ⏺ Organize files                                   │
│  ⏺ Import to database                               │
│                                                      │
│  Mosques extracted so far: 453                       │
│  Photos found: 1,083                                 │
│  Maps links: 288                                     │
│                                                      │
│  [View Log]                            [Cancel]     │
└──────────────────────────────────────────────────────┘
```

#### 3. Audit/Edit Mode

**Purpose:** Review and correct extracted data

```
┌──────────────────────────────────────────────────────────────┐
│  Edit Mosque: مسجد حذيفة بن اليمان (ID: 245)           [×]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Basic Information                                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Name (Arabic):  [مسجد حذيفة بن اليمان____________]    │ │
│  │ Area:           [حرستا_________________________]       │ │
│  │ Province:       [ريف دمشق ▼]                           │ │
│  │ Damage Type:    [● Damaged  ○ Demolished  ○ Unknown]  │ │
│  │ Confidence:     [High ▼]                               │ │
│  │ Verified:       [☑]                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Photos (3)                                [Add Photos...]  │
│  ┌──────┐ ┌──────┐ ┌──────┐                                │
│  │ IMG_ │ │ IMG_ │ │ IMG_ │                                │
│  │ 4656 │ │ 4650 │ │ 4658 │                                │
│  │      │ │      │ │      │                                │
│  └──────┘ └──────┘ └──────┘                                │
│  [⭐ Primary] [🗑️ Delete]                                   │
│                                                              │
│  Location                                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Google Maps: [https://maps.app.goo.gl/xyz_____] [Test]│ │
│  │ Latitude:    [33.568920___]  (auto from maps)          │ │
│  │ Longitude:   [36.345678___]                            │ │
│  │                                            [📍 Pick]    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Source Information                                          │
│  Excel: ريف_دمشق_المساجد_المتضررة.xlsx (Row 42)            │
│  Telegram: Cluster #12 (Messages: 55-58)                    │
│                                                              │
│  Notes:                                                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ [User notes here...___________________________]        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Audit Trail: Last modified by Admin on 2025-10-25 16:30    │
│                                                              │
│  [Cancel]  [Save]  [Save & Next]  [Mark as Duplicate]      │
└──────────────────────────────────────────────────────────────┘
```

#### 4. Duplicate Management

```
┌──────────────────────────────────────────────────────┐
│  Potential Duplicate Found                      [×]  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  These records appear to be the same mosque:         │
│                                                      │
│  Record A (ID: 245) - From Excel                     │
│  Name: مسجد حذيفة بن اليمان                         │
│  Area: حرستا                                         │
│  Province: ريف دمشق                                  │
│  Photos: 0  |  Location: No                          │
│                                                      │
│  Record B (ID: 678) - From AI Extraction             │
│  Name: حذيفة بن اليمان                               │
│  Area: حرستا                                         │
│  Province: ريف دمشق                                  │
│  Photos: 3  |  Location: Yes ✓                       │
│                                                      │
│  Similarity: 95%                                     │
│                                                      │
│  Action:                                             │
│  ○ Merge (Keep A, add B's data)                      │
│  ● Merge (Keep B, add A's data)                      │
│  ○ Keep both (not duplicates)                        │
│  ○ Decide later                                      │
│                                                      │
│  [Cancel]                      [Apply]               │
└──────────────────────────────────────────────────────┘
```

#### 5. Map View

**Purpose:** Visualize mosque locations on interactive map

```
┌──────────────────────────────────────────────────────┐
│  Map View - 288 mosques with locations          [×]  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │                                                │ │
│  │           [Interactive Leaflet Map]            │ │
│  │                                                │ │
│  │    📍 📍  📍                                    │ │
│  │       📍      📍 📍                             │ │
│  │  📍        📍                                   │ │
│  │     📍  📍         📍                           │ │
│  │                                                │ │
│  │  Legend:                                       │ │
│  │  🟢 Verified  🟡 Unverified  🔴 Issue          │ │
│  │                                                │ │
│  │  [+ Zoom In] [- Zoom Out] [🏠 Home]            │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  Filters:  ☑ Show verified  ☑ Show unverified       │
│            ☐ Cluster markers                        │
│                                                      │
│  [Export to GeoJSON]  [Export to KML]               │
└──────────────────────────────────────────────────────┘
```

#### 6. Statistics Dashboard

```
┌──────────────────────────────────────────────────────┐
│  Statistics Dashboard                           [×]  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Overall Statistics                                  │
│  ┌────────────────────────────────────────────────┐ │
│  │  Total Mosques:     1,053                      │ │
│  │  Verified:          450 (42.7%)                │ │
│  │  With Photos:       623 (59.2%)                │ │
│  │  With Location:     288 (27.4%)                │ │
│  │  Damaged:           307 (29.2%)                │ │
│  │  Demolished:        291 (27.6%)                │ │
│  │  Unknown Status:    455 (43.2%)                │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  By Province (Bar Chart)                             │
│  ┌────────────────────────────────────────────────┐ │
│  │ حماة     ████████████████ 250                  │ │
│  │ إدلب     ████████████ 214                      │ │
│  │ حمص      ████████ 111                          │ │
│  │ دير الزور ████████ 88                          │ │
│  │ اللاذقية  ███████ 86                           │ │
│  │ ريف دمشق  █████ 54                             │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  Data Quality Score: 68/100                          │
│  ⚠️ 15 issues need attention                        │
│                                                      │
│  [View Detailed Report]  [Export PDF]               │
└──────────────────────────────────────────────────────┘
```

#### 7. Export Options

```
┌──────────────────────────────────────────────────────┐
│  Export Data                                    [×]  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Export Format:                                      │
│  ○ Excel (.xlsx) - For stakeholders                  │
│  ● CSV - For data analysis                           │
│  ○ GeoJSON - For GIS mapping                         │
│  ○ KML - For Google Earth                            │
│  ○ SQL Dump - Full database backup                   │
│  ○ PDF Report - Summary document                     │
│                                                      │
│  Include:                                            │
│  ☑ All mosques                                       │
│  ☐ Only verified mosques                             │
│  ☐ Filter by province: [Select ▼]                    │
│                                                      │
│  Photo Export:                                       │
│  ☑ Include photo references                          │
│  ☐ Copy actual photo files                           │
│  ☐ Organize in folders by province                   │
│                                                      │
│  Output Location:                                    │
│  [C:\Exports\mosques_2025-10-25.csv_____] [Browse]  │
│                                                      │
│  [Cancel]                            [Export]        │
└──────────────────────────────────────────────────────┘
```

---

## 🔧 Backend Python Modules

### Module Structure

```
src/
├── gui/
│   ├── __init__.py
│   ├── main_window.py          # Main GUI
│   ├── import_dialog.py        # Telegram import
│   ├── edit_dialog.py          # Mosque editing
│   ├── map_view.py             # Map visualization
│   └── widgets/                # Reusable components
│
├── database/
│   ├── __init__.py
│   ├── models.py               # SQLAlchemy models
│   ├── manager.py              # Database operations
│   ├── migrations/             # Database migrations
│   └── schema.sql              # Initial schema
│
├── processing/
│   ├── __init__.py
│   ├── telegram_parser.py      # Conversation analyzer
│   ├── ai_extractor.py         # Claude AI integration
│   ├── excel_matcher.py        # Match with Excel
│   └── file_organizer.py       # File system ops
│
├── utils/
│   ├── __init__.py
│   ├── config.py               # Configuration
│   ├── logger.py               # Logging
│   └── validators.py           # Data validation
│
└── main.py                      # Entry point
```

### Key Classes

```python
# database/models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

Base = declarative_base()

class Mosque(Base):
    __tablename__ = 'mosques'

    mosque_id = Column(Integer, primary_key=True)
    province_id = Column(Integer, ForeignKey('provinces.province_id'))
    name_ar = Column(String(200), nullable=False)
    area = Column(String(200))
    damage_type = Column(String(20))
    source = Column(String(50))
    # ... other fields

    # Relationships
    photos = relationship("Photo", back_populates="mosque")
    locations = relationship("Location", back_populates="mosque")

    def to_dict(self):
        """Convert to dictionary for JSON/display"""
        return {
            'mosque_id': self.mosque_id,
            'name': self.name_ar,
            'area': self.area,
            'province': self.province.name_ar,
            'damage_type': self.damage_type,
            'photo_count': len(self.photos),
            'has_location': len(self.locations) > 0
        }


# database/manager.py
class DatabaseManager:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def get_mosques(self, filters=None):
        """Get mosques with optional filters"""
        session = self.Session()
        query = session.query(Mosque)

        if filters:
            if 'province_id' in filters:
                query = query.filter(Mosque.province_id == filters['province_id'])
            if 'verified_only' in filters:
                query = query.filter(Mosque.is_verified == True)

        return query.all()

    def update_mosque(self, mosque_id, updates, changed_by):
        """Update mosque and log to audit trail"""
        session = self.Session()
        mosque = session.query(Mosque).get(mosque_id)

        # Store old values for audit
        old_values = mosque.to_dict()

        # Apply updates
        for key, value in updates.items():
            setattr(mosque, key, value)

        mosque.updated_by = changed_by
        mosque.updated_at = datetime.now()

        # Log to audit
        audit = AuditLog(
            table_name='mosques',
            record_id=mosque_id,
            action='UPDATE',
            old_values=old_values,
            new_values=updates,
            changed_by=changed_by
        )
        session.add(audit)

        session.commit()


# gui/main_window.py
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager(CONFIG['database_url'])
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Mosque Database Management v1.5")
        self.setGeometry(100, 100, 1400, 800)

        # Create menu bar
        menubar = self.menuBar()

        file_menu = menubar.addMenu('File')
        file_menu.addAction('Import Telegram Export', self.import_telegram)
        file_menu.addAction('Export Data', self.export_data)
        file_menu.addAction('Exit', self.close)

        # Create layout
        central_widget = QWidget()
        layout = QHBoxLayout()

        # Left: Province tree
        self.province_tree = self.create_province_tree()
        layout.addWidget(self.province_tree, 1)

        # Center: Mosque list
        self.mosque_table = self.create_mosque_table()
        layout.addWidget(self.mosque_table, 3)

        # Right: Details panel
        self.details_panel = self.create_details_panel()
        layout.addWidget(self.details_panel, 2)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def import_telegram(self):
        """Open import dialog"""
        dialog = ImportDialog(self.db, self)
        if dialog.exec_():
            # Refresh data
            self.load_mosques()

    def edit_mosque(self, mosque_id):
        """Open edit dialog"""
        dialog = EditMosqueDialog(mosque_id, self.db, self)
        if dialog.exec_():
            # Refresh display
            self.load_mosque_details(mosque_id)
```

---

## 🚀 Implementation Roadmap

### Phase 1: Database Setup (Day 1)
- [x] Design SQL schema
- [ ] Create PostgreSQL database
- [ ] Implement SQLAlchemy models
- [ ] Create migration scripts
- [ ] Import existing CSV data to database
- [ ] Test CRUD operations

### Phase 2: Core Processing (Day 2-3)
- [x] Conversation analyzer (completed!)
- [ ] Excel matcher with intelligent merging
- [ ] File organizer (province folders)
- [ ] Database import pipeline
- [ ] Test with sample data

### Phase 3: Basic GUI (Day 4-5)
- [ ] Main window with mosque list
- [ ] Province tree navigation
- [ ] Details panel
- [ ] Basic search and filter
- [ ] Edit dialog
- [ ] Test GUI ↔ database integration

### Phase 4: Import Workflow (Day 6)
- [ ] Import Telegram dialog
- [ ] Progress tracking
- [ ] Error handling
- [ ] Result validation
- [ ] Test end-to-end import

### Phase 5: Advanced Features (Day 7)
- [ ] Map view (Leaflet integration)
- [ ] Duplicate detection UI
- [ ] Audit log viewer
- [ ] Statistics dashboard
- [ ] Export functionality

### Phase 6: Polish & Deploy (Day 8-9)
- [ ] User authentication
- [ ] Settings/preferences
- [ ] Help documentation
- [ ] Package as standalone app
- [ ] User testing and fixes

---

## 💰 Estimated Costs

### Development
- **Time:** 8-9 days (if working solo)
- **AI API:** ~$0.50 per import (Claude Haiku)

### Infrastructure (if deployed as web app)
- PostgreSQL hosting: $0-$20/month (free tiers available)
- Web hosting: $0-$10/month

### Tools & Libraries (all free/open-source)
- Python: Free
- PyQt6: Free (GPL/Commercial license available)
- PostgreSQL: Free
- Leaflet (maps): Free

**Total initial cost: ~$0** (if using desktop app)

---

## 🎯 Success Metrics

### Data Organization
- ✅ >95% mosques have province assigned
- ✅ >80% mosques have photos linked
- ✅ >70% mosques have GPS location
- ✅ >50% mosques verified by human

### User Experience
- ✅ Import new Telegram export in <20 minutes
- ✅ Search mosque by name in <1 second
- ✅ Edit and save mosque in <30 seconds
- ✅ Export full database in <5 minutes

### Data Quality
- ✅ Duplicate rate <5%
- ✅ Missing critical data <10%
- ✅ Audit log for all changes
- ✅ Database passes integrity checks

---

## 📝 Next Steps

1. **Immediate:** Wait for conversation analyzer to complete
2. **Review:** Analyze results and validate approach
3. **Decide:** Desktop app (PyQt6) vs Web app (Flask+React)?
4. **Setup:** Create PostgreSQL database
5. **Implement:** Start with Phase 1 (database) and Phase 2 (processing)
6. **Build:** GUI incrementally with user feedback
7. **Test:** End-to-end workflow with real data
8. **Deploy:** Package and deliver

---

## ❓ Questions to Resolve

1. **Desktop vs Web?** Which do you prefer for the GUI?
2. **Authentication?** Do you need multi-user with permissions?
3. **Cloud storage?** Should photos be uploaded to cloud or stay local?
4. **Auto-sync?** Should it periodically check for new Telegram data?
5. **Languages?** Arabic-only UI or Arabic + English?

---

**Status:** Plan ready for review and implementation approval.
