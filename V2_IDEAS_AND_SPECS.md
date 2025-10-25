# Version 2 - Real-Time Mosque Data Collection & Management System

**Status:** Planning / Not Started
**Based On:** Version 1 (Static Export Processing)
**Timeline:** 2-3 weeks development
**Budget:** $5-10/month operational cost

---

## 🎯 Version 2 Vision

### **Core Improvement Over V1**
Version 1 processes **static Telegram exports** manually.
Version 2 adds **real-time data collection and automation**.

### **Key Goals**
1. ✅ **Real-time ingestion** - No more manual exports
2. ✅ **Telegram Bot** - Guided data entry for committees
3. ✅ **Automated workflow** - Process data automatically with n8n
4. ✅ **Web dashboard** - Browse and search mosques
5. ✅ **Validation system** - Built-in data quality checks
6. ✅ **Update capability** - Add/edit mosques after initial collection

---

## 📋 Problem Statement

### **V1 Limitations to Address**
1. **Manual process** - User must export Telegram data manually
2. **Batch processing** - Can't add new mosques easily
3. **No validation** - Data quality issues discovered too late
4. **CSV-only output** - No searchable interface
5. **Messy data** - Committee sends unstructured messages

### **V2 Solutions**
1. **Telegram Bot** → Structured data entry with validation
2. **Live sync** → Real-time database updates
3. **n8n workflow** → Automated processing pipeline
4. **Web UI** → Search, filter, export capabilities
5. **Guided forms** → Committee gets step-by-step prompts

---

## 🏗️ Architecture

### **High-Level Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Telegram Bot    │────────▶│  n8n Workflow    │         │
│  │  (Guided Entry)  │         │  (Orchestration) │         │
│  └──────────────────┘         └──────────────────┘         │
│         │                               │                   │
│         │ Validates                     │ Processes         │
│         │ Stores temp                   │ AI enhance        │
│         ▼                               ▼                   │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   MongoDB        │◀────────│  Claude API      │         │
│  │  (Temp Storage)  │         │  (Enhancement)   │         │
│  └──────────────────┘         └──────────────────┘         │
│                                                              │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  Deduplication   │───▶│  Geocoding       │              │
│  │  Engine          │    │  Service         │              │
│  └──────────────────┘    └──────────────────┘              │
│         │                          │                        │
│         │                          │                        │
│         ▼                          ▼                        │
│  ┌──────────────────────────────────────────┐              │
│  │         PostgreSQL Database               │              │
│  │  (Production - Validated & Enriched)     │              │
│  └──────────────────────────────────────────┘              │
│                                                              │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  Web Dashboard   │    │   REST API       │              │
│  │  (React/Vue)     │◀───│  (FastAPI)       │              │
│  └──────────────────┘    └──────────────────┘              │
│         │                          │                        │
│         │ Search/Filter            │ Export                │
│         │ View Photos              │ Reports               │
│         │ Edit Data                │ Statistics            │
│         │                          │                        │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  Admin Panel     │    │  Mobile View     │              │
│  │  (Management)    │    │  (Responsive)    │              │
│  └──────────────────┘    └──────────────────┘              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 Component 1: Telegram Bot

### **Purpose**
Replace messy Telegram messages with structured, guided data entry.

### **User Experience Flow**

```
Committee Member:
├─ 1. Start Bot: /start
├─ 2. Bot: "Select Province"
│   └─ Buttons: [درعا] [حلب] [حمص] [إدلب] ...
├─ 3. User: Clicks "حلب"
├─ 4. Bot: "What's the mosque name?"
│   └─ User: Types "مسجد الفاروق"
├─ 5. Bot: "What's the area/neighborhood?"
│   └─ User: Types "حي الشهباء"
├─ 6. Bot: "Is it damaged or demolished?"
│   └─ Buttons: [متضرر جزئياً] [مدمر كلياً]
├─ 7. Bot: "Send photos (1-5 images, or /skip)"
│   └─ User: Sends 3 photos
├─ 8. Bot: "Send Google Maps location (or /skip)"
│   └─ User: Sends location or link
├─ 9. Bot: "Any additional notes? (or /skip)"
│   └─ User: Types notes or /skip
├─ 10. Bot: "✅ Mosque saved! Add another? /add or /done"
└─ User: /done
```

### **Technical Implementation**

**Technology:** Python + python-telegram-bot library

**File Structure:**
```python
mosque_bot/
├── bot.py              # Main bot logic
├── handlers/
│   ├── start.py        # /start command
│   ├── add_mosque.py   # Guided flow
│   ├── edit_mosque.py  # Edit existing
│   └── admin.py        # Admin commands
├── database/
│   ├── mongo.py        # MongoDB connection
│   └── models.py       # Data models
├── validation/
│   └── validators.py   # Input validation
├── config.py           # Bot token, API keys
└── requirements.txt
```

**Key Features:**

1. **State Management**
```python
# Track user's position in data entry flow
user_states = {
    'user_id': {
        'stage': 'awaiting_mosque_name',
        'data': {
            'province': 'حلب',
            'name': None,
            'area': None,
            'photos': [],
            'location': None
        }
    }
}
```

2. **Validation**
```python
def validate_mosque_name(text):
    """Ensure mosque name has required keywords"""
    keywords = ['مسجد', 'جامع', 'مصلى']
    if not any(k in text for k in keywords):
        return False, "اسم المسجد يجب أن يحتوي على كلمة 'مسجد' أو 'جامع' أو 'مصلى'"
    return True, None
```

3. **Photo Handling**
```python
async def handle_photo(update, context):
    """Save photo to storage, link to mosque entry"""
    photo = update.message.photo[-1]  # Highest resolution
    file = await photo.get_file()

    # Save to cloud storage (AWS S3 / Cloudinary)
    photo_url = upload_to_storage(file)

    # Add to user's current mosque entry
    context.user_data['photos'].append(photo_url)
```

4. **Location Handling**
```python
async def handle_location(update, context):
    """Extract coordinates from location or Google Maps link"""
    if update.message.location:
        # Direct location share
        lat = update.message.location.latitude
        lng = update.message.location.longitude
    elif update.message.text and 'maps' in update.message.text:
        # Google Maps link
        lat, lng = extract_coords_from_link(update.message.text)

    context.user_data['location'] = {'lat': lat, 'lng': lng}
```

**Bot Commands:**
- `/start` - Begin data entry
- `/add` - Add new mosque
- `/list` - View submitted mosques
- `/edit [id]` - Edit existing mosque
- `/delete [id]` - Delete mosque
- `/stats` - Show statistics
- `/help` - Show instructions
- `/cancel` - Cancel current operation

**Admin Commands:**
- `/admin` - Admin panel
- `/approve [id]` - Approve mosque
- `/reject [id]` - Reject mosque
- `/export` - Export data
- `/users` - List active users

### **Deployment**
```bash
# Docker container on VPS
docker run -d \
  --name mosque-bot \
  -e BOT_TOKEN=your_token \
  -e MONGO_URI=mongodb://... \
  --restart unless-stopped \
  mosque-bot:latest
```

### **Cost Estimate**
- Telegram Bot API: Free
- VPS Hosting: $5/month (DigitalOcean/Linode)
- MongoDB Atlas: Free tier (512MB)
- **Total: $5/month**

---

## 🔄 Component 2: n8n Workflow Automation

### **Purpose**
Automatically process bot submissions: validate, enhance with AI, deduplicate, import to database.

### **Workflow Design**

```
┌─────────────────────────────────────────────────────────┐
│  Trigger: New Mosque Entry in MongoDB                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 1: Data Validation                                │
│  - Check required fields present                        │
│  - Validate mosque name format                          │
│  - Verify photos uploaded                               │
│  IF INVALID: Send to review queue                       │
└────────────────┬────────────────────────────────────────┘
                 │ Valid
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 2: AI Enhancement (Claude API)                    │
│  - Standardize mosque name                              │
│  - Extract additional info from notes                   │
│  - Generate description                                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 3: Duplicate Detection                            │
│  - Fuzzy match against existing mosques                │
│  - Check: Same name + same province                     │
│  IF DUPLICATE: Flag for manual review                   │
└────────────────┬────────────────────────────────────────┘
                 │ Unique
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 4: Geocoding (if location provided)              │
│  - If lat/lng: Reverse geocode to verify               │
│  - If maps link: Extract coordinates                    │
│  - Store both coordinates and address                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 5: Photo Processing                               │
│  - Optimize/resize images                               │
│  - Generate thumbnails                                  │
│  - Extract EXIF metadata                                │
│  - Optional: AI damage assessment                       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 6: Import to PostgreSQL                           │
│  - Insert into provinces table (if new)                │
│  - Insert into mosques table                            │
│  - Insert into photos table                             │
│  - Insert into locations table                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 7: Notifications                                  │
│  - Send success message to bot user                     │
│  - Notify admin (if required)                           │
│  - Update statistics                                    │
└─────────────────────────────────────────────────────────┘
```

### **n8n Nodes Used**

| Node Type | Purpose | Configuration |
|-----------|---------|---------------|
| **MongoDB Trigger** | Watch for new entries | Collection: `temp_mosques` |
| **IF Node** | Validation checks | Condition: All required fields present |
| **HTTP Request** | Call Claude API | POST to Anthropic API |
| **Code Node** | Fuzzy matching | JavaScript with fuzzball library |
| **HTTP Request** | Geocoding | Call Nominatim or Google Maps |
| **PostgreSQL** | Database insert | Parameterized queries |
| **Telegram Node** | Send notifications | Bot API |

### **Workflow Files**
```
n8n_workflows/
├── mosque_ingestion.json      # Main workflow
├── duplicate_check.json        # Duplicate detection
├── photo_processing.json       # Image optimization
└── daily_stats.json            # Statistics reporting
```

### **Deployment**
```bash
# n8n self-hosted
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=secure_password \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n:latest
```

**Cost:** Free (self-hosted) or $20/month (n8n cloud)

---

## 🌐 Component 3: Web Dashboard

### **Purpose**
Browse, search, filter, and export mosque data. Accessible to ministry officials and reconstruction planners.

### **Features**

#### **1. Search & Filter**
- **Text search:** Mosque name, area, province
- **Advanced filters:**
  - Province dropdown
  - Damage type (damaged/demolished)
  - With/without photos
  - With/without location
  - Date range

#### **2. Mosque List View**
```
┌─────────────────────────────────────────────────────────┐
│  🕌 Mosque Database                       [+ Add New]    │
├─────────────────────────────────────────────────────────┤
│  Search: [____________]  Province: [All ▼]  Filter: [...] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 📸 مسجد الفاروق                          حلب    │  │
│  │    حي الشهباء • مدمر كلياً • 3 photos          │  │
│  │    📍 Location available                         │  │
│  │    [View] [Edit] [Export]                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 🕌 مسجد النور                            دمشق   │  │
│  │    الميدان • متضرر جزئياً • 2 photos            │  │
│  │    ⚠️  No location                               │  │
│  │    [View] [Edit] [Export]                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Showing 1-20 of 487 mosques        [1] [2] [3] ... [25]│
└─────────────────────────────────────────────────────────┘
```

#### **3. Mosque Detail View**
```
┌─────────────────────────────────────────────────────────┐
│  🕌 مسجد الفاروق - حلب                        [Edit]    │
├─────────────────────────────────────────────────────────┤
│  Province: حلب                                          │
│  Area: حي الشهباء                                       │
│  Damage: مدمر كلياً (Demolished)                        │
│  Date Added: 2025-10-20                                 │
│  Source: Telegram Bot (User: Ahmad Khalil)             │
├─────────────────────────────────────────────────────────┤
│  📸 Photos (3):                                         │
│  [Image] [Image] [Image]                                │
│  Click to enlarge                                       │
├─────────────────────────────────────────────────────────┤
│  📍 Location:                                           │
│  Lat: 36.2021, Lng: 37.1343                             │
│  [View on Google Maps] [View on OpenStreetMap]         │
│  [Interactive Map]                                      │
├─────────────────────────────────────────────────────────┤
│  📝 Notes:                                              │
│  المسجد بحاجة إلى إعادة بناء كاملة. الكلفة التقديرية   │
│  300,000 دولار. عدد المصلين قبل الدمار: 500              │
├─────────────────────────────────────────────────────────┤
│  [Export PDF] [Export JSON] [Share Link] [Delete]      │
└─────────────────────────────────────────────────────────┘
```

#### **4. Map View**
- Interactive map showing all mosques
- Color-coded markers:
  - 🔴 Red: Demolished
  - 🟠 Orange: Damaged
  - 🟢 Green: Historical (intact)
- Click marker to see mosque details
- Filter markers by province/damage type

#### **5. Statistics Dashboard**
```
┌─────────────────────────────────────────────────────────┐
│  📊 Statistics Dashboard                                 │
├─────────────────────────────────────────────────────────┤
│  Total Mosques: 487                                     │
│  Damaged: 234 (48%)     Demolished: 253 (52%)           │
├─────────────────────────────────────────────────────────┤
│  By Province:                                           │
│  [Bar Chart]                                            │
│  إدلب:    ████████████████ 144                         │
│  حماة:    ███████████████  141                          │
│  حلب:     ████████        85                            │
│  ...                                                    │
├─────────────────────────────────────────────────────────┤
│  Photo Coverage: 65% (317/487 mosques have photos)     │
│  Location Coverage: 72% (351/487 have coordinates)     │
├─────────────────────────────────────────────────────────┤
│  Recent Activity:                                       │
│  • 5 mosques added today                                │
│  • 12 mosques updated this week                         │
│  • Last update: 2 hours ago                             │
└─────────────────────────────────────────────────────────┘
```

#### **6. Export Options**
- **CSV** - Full data export
- **Excel** - Formatted spreadsheet with multiple sheets
- **PDF Report** - Print-friendly document
- **GeoJSON** - For GIS applications
- **JSON API** - For developers

### **Technology Stack**

**Frontend:**
- **Framework:** React + TypeScript
- **UI Library:** Ant Design or Material-UI
- **Maps:** Leaflet.js (OpenStreetMap)
- **State Management:** React Query
- **Styling:** TailwindCSS

**Backend:**
- **API Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **Authentication:** JWT tokens
- **File Storage:** AWS S3 or Cloudinary

**File Structure:**
```
mosque-dashboard/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MosqueList.tsx
│   │   │   ├── MosqueDetail.tsx
│   │   │   ├── MapView.tsx
│   │   │   └── Statistics.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Browse.tsx
│   │   │   └── Admin.tsx
│   │   ├── api/
│   │   │   └── mosques.ts
│   │   └── App.tsx
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/
│   ├── api/
│   │   ├── main.py           # FastAPI app
│   │   ├── routes/
│   │   │   ├── mosques.py    # CRUD endpoints
│   │   │   ├── auth.py       # Authentication
│   │   │   └── export.py     # Export endpoints
│   │   ├── models/
│   │   │   └── mosque.py     # Pydantic models
│   │   └── database.py       # DB connection
│   ├── requirements.txt
│   └── Dockerfile
│
└── docker-compose.yml        # Run everything
```

### **API Endpoints**

```python
# FastAPI Routes

# Mosques
GET    /api/mosques              # List all (paginated)
GET    /api/mosques/{id}         # Get single mosque
POST   /api/mosques              # Create new
PUT    /api/mosques/{id}         # Update
DELETE /api/mosques/{id}         # Delete

# Search & Filter
GET    /api/mosques/search?q=    # Text search
GET    /api/mosques/filter?province=&damage=

# Statistics
GET    /api/stats                # Overall statistics
GET    /api/stats/province/{id}  # Province-specific

# Export
GET    /api/export/csv           # Export all to CSV
GET    /api/export/geojson       # Export for GIS
GET    /api/export/pdf/{id}      # Generate PDF report

# Authentication
POST   /api/auth/login           # Login
POST   /api/auth/refresh         # Refresh token
POST   /api/auth/logout          # Logout
```

### **Deployment**

```bash
# Using Docker Compose
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: mosques
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres/mosques

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

**Cost:**
- VPS (4GB RAM): $10-15/month
- Or use free tier: Vercel (frontend) + Railway (backend)

---

## 🔐 Component 4: Authentication & Permissions

### **User Roles**

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Public** | View mosques (read-only) | General public, donors |
| **Committee** | Add/edit own submissions | Field workers |
| **Moderator** | Approve/reject entries | Data validators |
| **Admin** | Full access, user management | Ministry officials |
| **API User** | Read-only API access | Developers, analysts |

### **Implementation**

```python
# JWT-based authentication
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY)
    user = get_user_from_db(payload['sub'])
    if not user:
        raise HTTPException(status_code=401)
    return user

def require_role(role: str):
    def decorator(func):
        async def wrapper(current_user = Depends(get_current_user)):
            if current_user.role != role:
                raise HTTPException(status_code=403)
            return await func(current_user)
        return wrapper
    return decorator

# Usage
@app.post("/api/mosques")
@require_role("committee")
async def create_mosque(data, user):
    # Only committee members can add mosques
    pass
```

---

## 📊 Data Migration from V1 to V2

### **Migration Script**

```python
# migrate_v1_to_v2.py

import pandas as pd
import psycopg2

def migrate():
    # 1. Read V1 CSV outputs
    excel_mosques = pd.read_csv('v1/out_csv/excel_mosques_master.csv')
    ai_mosques = pd.read_csv('v1/out_csv/ai_extracted_mosques.csv')
    merged = pd.read_csv('v1/out_csv/merged_mosques.csv')

    # 2. Connect to V2 PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)

    # 3. Insert provinces
    provinces = merged['province'].unique()
    for province in provinces:
        cursor.execute(
            "INSERT INTO provinces (name) VALUES (%s) ON CONFLICT DO NOTHING",
            (province,)
        )

    # 4. Insert mosques
    for _, row in merged.iterrows():
        cursor.execute("""
            INSERT INTO mosques (
                province_id, name, area, damage_type, notes, source
            ) VALUES (
                (SELECT id FROM provinces WHERE name=%s),
                %s, %s, %s, %s, %s
            )
        """, (row['province'], row['name'], row['area'],
              row['damage_type'], row['notes'], 'v1_migration'))

    # 5. Insert photos, locations, etc.
    # ...

    conn.commit()
    print("✅ Migration complete!")

if __name__ == "__main__":
    migrate()
```

---

## 🚀 Development Roadmap

### **Week 1: Core Bot**
- Day 1-2: Setup Telegram bot skeleton
- Day 3-4: Implement guided flow
- Day 5: Add validation
- Day 6-7: Testing with sample users

### **Week 2: Workflow & Database**
- Day 1-2: Setup n8n workflows
- Day 3-4: Connect to PostgreSQL
- Day 5: Duplicate detection
- Day 6-7: Photo processing

### **Week 3: Web Dashboard**
- Day 1-2: Backend API (FastAPI)
- Day 3-5: Frontend UI (React)
- Day 6: Authentication
- Day 7: Testing & bug fixes

### **Week 4: Polish & Deploy**
- Day 1-2: Migrate V1 data
- Day 3-4: User testing
- Day 5: Fix bugs
- Day 6: Documentation
- Day 7: Production deployment

---

## 💰 Cost Breakdown

| Component | Monthly Cost | Notes |
|-----------|--------------|-------|
| **VPS (4GB)** | $10 | DigitalOcean/Linode |
| **MongoDB Atlas** | Free | 512MB tier |
| **PostgreSQL** | $0 | Self-hosted on VPS |
| **Claude API** | $2-5 | ~500 requests/month |
| **Photo Storage (S3)** | $1-2 | First 5GB |
| **Domain** | $1/month | .com domain |
| **SSL Certificate** | Free | Let's Encrypt |
| **n8n** | Free | Self-hosted |
| **Total** | **$14-18/month** | |

**One-time costs:**
- Development: 4 weeks × $0 (self-built)
- Testing: 1 week

---

## 📈 Success Metrics

### **Performance Targets**
- Bot response time: <2 seconds
- API response time: <500ms
- Dashboard load time: <3 seconds
- Concurrent users: 50+

### **Data Quality Targets**
- Duplicate rate: <5%
- Data completeness: >90%
- Photo coverage: >70%
- Location accuracy: >85%

### **User Adoption**
- Active bot users: 20+ committees
- Daily submissions: 10-30 mosques
- Dashboard users: 50+ monthly

---

## 🔄 V1 to V2 Comparison

| Feature | Version 1 | Version 2 |
|---------|-----------|-----------|
| **Data Entry** | Unstructured messages | Guided bot flow |
| **Processing** | Manual export + script | Real-time automation |
| **Validation** | Post-processing | Real-time checks |
| **Deduplication** | Batch fuzzy matching | Live detection |
| **Interface** | CSV files only | Web dashboard |
| **Updates** | Re-run entire pipeline | Edit individual mosques |
| **Photos** | Manual organization | Auto-processed |
| **Geocoding** | Manual | Automatic |
| **Cost** | $0.15 one-time | $15/month |
| **Maintenance** | None (static) | Ongoing |

---

## 📦 Deliverables

### **For Committees:**
- Telegram bot with instructions
- User manual (Arabic)
- Training video

### **For Ministry:**
- Web dashboard access
- Admin credentials
- API documentation
- Monthly reports

### **For Developers:**
- GitHub repository
- API documentation
- Deployment guide
- Database schema

---

## 🎯 Next Steps to Start V2

1. ✅ **Complete V1** - Get 400-500 mosques in clean database
2. ✅ **Tag V1 repository** - `git tag v1.0.0`
3. ✅ **Create V2 repository** - New GitHub repo
4. ✅ **Setup development environment** - Docker, Node.js, Python
5. ✅ **Build bot prototype** - Test with 2-3 users
6. ✅ **Iterate based on feedback**

---

**Document Version:** 1.0
**Created:** October 25, 2025
**Status:** Planning Phase
**Owner:** [Your Name]

---

**Ready to start V2 after V1 is complete!** 🚀
