# Version 3 - Advanced AI & GIS-Powered Mosque Reconstruction Platform

**Status:** Future Planning
**Based On:** Version 2 (Real-time System)
**Timeline:** 1-2 months development
**Budget:** $20-30/month operational cost

---

## 🎯 Version 3 Vision

### **From Data Collection to Intelligence Platform**

Version 2 provides **real-time data collection**.
Version 3 transforms it into an **intelligent reconstruction planning system** with advanced AI and GIS capabilities.

### **Strategic Goals**
1. 🤖 **AI-powered damage assessment** from photos
2. 🗺️ **Full GIS integration** for reconstruction planning
3. 📊 **Predictive analytics** for resource allocation
4. 🌐 **Public transparency** with donation tracking
5. 📱 **Mobile-first** field data collection
6. 🔗 **API-driven** ecosystem for partners

---

## 📋 Problem Statement

### **V2 Limitations to Address**
1. **Manual damage assessment** - Experts must review each photo
2. **No spatial analysis** - Can't plan reconstruction by region
3. **Limited insights** - Just data storage, no intelligence
4. **Desktop-only** - Field workers need mobile access
5. **Closed system** - Hard for partners to integrate
6. **No donation tracking** - Can't link donors to specific mosques

### **V3 Solutions**
1. **Claude Vision AI** → Automatic damage assessment from photos
2. **PostGIS + QGIS** → Advanced spatial analysis and mapping
3. **Machine Learning** → Predict reconstruction costs and timelines
4. **Progressive Web App** → Mobile + desktop + offline support
5. **GraphQL API** → Flexible integration for partners
6. **Blockchain** → Transparent donation tracking (optional)

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    DATA SOURCES                           │
├──────────────────────────────────────────────────────────┤
│  V2 Bot  │  Mobile App  │  Web Forms  │  Partner APIs   │
└─────┬────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────┐
│                 AI PROCESSING LAYER                       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────────┐  ┌────────────────┐                 │
│  │  Claude Vision │  │  OCR Engine    │                 │
│  │  Image Analysis│  │  Text Extract  │                 │
│  └────────┬───────┘  └────────┬───────┘                 │
│           │                   │                          │
│           ▼                   ▼                          │
│  ┌─────────────────────────────────────┐                │
│  │     Damage Assessment Engine        │                │
│  │  • Crack detection                  │                │
│  │  • Structural integrity             │                │
│  │  • Severity scoring (0-100)         │                │
│  │  • Cost estimation                  │                │
│  └─────────────────┬───────────────────┘                │
│                    │                                     │
└────────────────────┼─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                  GIS LAYER (PostGIS)                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────────────────────────────────────────┐     │
│  │  Spatial Analysis                              │     │
│  │  • Proximity analysis (mosques near each other)│     │
│  │  • Heat maps (damage concentration)            │     │
│  │  • Buffer zones (reconstruction zones)         │     │
│  │  • Route optimization (site visits)            │     │
│  └────────────────────────────────────────────────┘     │
│                                                           │
│  ┌────────────────────────────────────────────────┐     │
│  │  Map Layers                                    │     │
│  │  • Satellite imagery                           │     │
│  │  • Infrastructure (roads, utilities)           │     │
│  │  • Demographics                                │     │
│  │  • Conflict zones                              │     │
│  └────────────────────────────────────────────────┘     │
│                                                           │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│              INTELLIGENCE & ML LAYER                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  Cost Prediction │  │  Priority Engine │            │
│  │  Model (ML)      │  │  Scoring System  │            │
│  └──────────────────┘  └──────────────────┘            │
│                                                           │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  Resource        │  │  Timeline        │            │
│  │  Allocation      │  │  Forecasting     │            │
│  └──────────────────┘  └──────────────────┘            │
│                                                           │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                  API & INTEGRATION                        │
├──────────────────────────────────────────────────────────┤
│  GraphQL API  │  REST API  │  Webhooks  │  WebSockets  │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                 PRESENTATION LAYER                        │
├──────────────────────────────────────────────────────────┤
│  Web Dashboard  │  Mobile App  │  GIS Desktop  │  Reports│
└──────────────────────────────────────────────────────────┘
```

---

## 🤖 Component 1: AI Image Analysis & Damage Assessment

### **Purpose**
Automatically analyze mosque photos to assess damage severity, estimate repair costs, and prioritize reconstruction.

### **Features**

#### **1. Automated Damage Detection**

```python
# Using Claude Vision API

async def analyze_mosque_damage(image_path: str) -> DamageReport:
    """
    Analyze mosque photo and return detailed damage assessment.
    """

    with open(image_path, 'rb') as img:
        image_data = base64.b64encode(img.read()).decode()

    prompt = """
    Analyze this photo of a damaged mosque in Syria.

    Assess the following:
    1. **Structural Damage** (0-100 scale):
       - Walls: intact, cracked, partially collapsed, completely destroyed
       - Roof: intact, damaged, partially missing, completely missing
       - Minaret: standing, leaning, collapsed
       - Dome: intact, cracked, collapsed

    2. **Damage Type**:
       - Shelling/bombing
       - Fire damage
       - Natural deterioration
       - Looting/vandalism

    3. **Repair Scope**:
       - Minor repairs (cosmetic)
       - Moderate repairs (structural reinforcement)
       - Major reconstruction (rebuild sections)
       - Complete rebuilding

    4. **Cost Estimate** (in USD):
       - Based on visible damage
       - Include materials + labor

    5. **Safety Status**:
       - Safe to enter
       - Structural assessment needed
       - Unsafe - collapse risk

    6. **Priority Level** (1-5):
       1 = Critical (community needs urgent access)
       5 = Low priority

    Return structured JSON with confidence scores.
    """

    response = anthropic_client.messages.create(
        model="claude-3-opus-20240229",  # Vision model
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    result = json.loads(response.content[0].text)

    return DamageReport(
        structural_score=result['structural_damage'],
        damage_type=result['damage_type'],
        repair_scope=result['repair_scope'],
        cost_estimate=result['cost_estimate'],
        safety_status=result['safety_status'],
        priority=result['priority'],
        confidence=result['confidence'],
        details=result['detailed_findings']
    )
```

#### **2. Multi-Photo Analysis**

```python
def analyze_mosque_collection(photos: List[str]) -> ComprehensiveReport:
    """
    Analyze multiple photos of same mosque to get comprehensive assessment.
    """

    # Analyze each photo
    reports = [analyze_mosque_damage(photo) for photo in photos]

    # Aggregate results
    return ComprehensiveReport(
        overall_damage=max(r.structural_score for r in reports),
        damage_types=set(r.damage_type for r in reports),
        estimated_cost=median(r.cost_estimate for r in reports),
        priority=min(r.priority for r in reports),  # Lowest = highest priority
        photo_count=len(photos),
        consistency_score=calculate_consistency(reports)
    )
```

#### **3. Crack Detection (Computer Vision)**

```python
import cv2
import numpy as np

def detect_cracks(image_path: str) -> CrackReport:
    """
    Use OpenCV to detect cracks in walls/structures.
    """

    # Load image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150)

    # Find contours (potential cracks)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Filter for crack-like shapes
    cracks = []
    for contour in contours:
        # Analyze aspect ratio, length, curvature
        if is_crack_shaped(contour):
            cracks.append({
                'length': cv2.arcLength(contour, False),
                'location': get_bounding_box(contour),
                'severity': classify_crack_severity(contour)
            })

    return CrackReport(
        crack_count=len(cracks),
        total_length=sum(c['length'] for c in cracks),
        severity_distribution={
            'minor': len([c for c in cracks if c['severity'] == 'minor']),
            'moderate': len([c for c in cracks if c['severity'] == 'moderate']),
            'severe': len([c for c in cracks if c['severity'] == 'severe'])
        },
        annotated_image=draw_cracks_on_image(img, cracks)
    )
```

#### **4. Before/After Comparison**

```python
def compare_before_after(before_photo: str, after_photo: str) -> ChangeReport:
    """
    Compare historical photos with current damage photos.
    """

    # Use image similarity algorithms
    similarity_score = structural_similarity(before_photo, after_photo)

    # Detect changes
    diff_image = create_diff_image(before_photo, after_photo)

    # Quantify damage
    damage_percentage = calculate_damage_percentage(diff_image)

    return ChangeReport(
        similarity_score=similarity_score,
        damage_percentage=damage_percentage,
        diff_image=diff_image,
        change_areas=identify_change_regions(diff_image)
    )
```

### **Output Dashboard**

```
┌───────────────────────────────────────────────────────┐
│  🤖 AI Damage Assessment - مسجد الفاروق              │
├───────────────────────────────────────────────────────┤
│  📸 Photos Analyzed: 4                                │
│  🎯 Confidence: 92%                                   │
├───────────────────────────────────────────────────────┤
│  🏗️ STRUCTURAL DAMAGE: 78/100 (Severe)               │
│                                                       │
│  Walls:    ████████░░ 85% damaged                    │
│  Roof:     ███████░░░ 70% damaged                    │
│  Minaret:  ██████████ 100% destroyed                 │
│  Dome:     ████░░░░░░ 45% damaged                    │
│                                                       │
├───────────────────────────────────────────────────────┤
│  💰 COST ESTIMATE                                     │
│  Range: $180,000 - $220,000                          │
│  Median: $200,000                                    │
│                                                       │
│  Breakdown:                                          │
│  • Structural repairs: $120,000                      │
│  • Minaret rebuild: $50,000                          │
│  • Roof restoration: $30,000                         │
│                                                       │
├───────────────────────────────────────────────────────┤
│  ⚠️ SAFETY: Unsafe - Collapse Risk                   │
│  ⏱️ Timeline: 8-12 months                            │
│  🎯 Priority: 2 (High)                               │
│                                                       │
├───────────────────────────────────────────────────────┤
│  📋 RECOMMENDATIONS                                   │
│  1. Immediate stabilization of north wall           │
│  2. Remove debris before reconstruction              │
│  3. Structural engineer assessment required          │
│  4. Community needs temporary prayer space           │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## 🗺️ Component 2: Advanced GIS & Spatial Analysis

### **Purpose**
Transform mosque data into actionable spatial intelligence for reconstruction planning.

### **Technology Stack**
- **PostGIS** - Spatial database extension for PostgreSQL
- **QGIS** - Desktop GIS software for analysis
- **Mapbox/Leaflet** - Web mapping
- **Turf.js** - Spatial analysis in JavaScript
- **GeoPandas** - Python spatial data analysis

### **Features**

#### **1. Spatial Database Schema**

```sql
-- PostGIS-enabled mosque database

CREATE EXTENSION postgis;

CREATE TABLE mosques (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    province_id INT,
    geometry GEOMETRY(Point, 4326),  -- Lat/Lng in WGS84
    damage_severity INT,
    reconstruction_cost NUMERIC,
    priority INT,
    status VARCHAR(50),
    created_at TIMESTAMP
);

-- Spatial index for fast queries
CREATE INDEX idx_mosques_geometry ON mosques USING GIST(geometry);

-- Reconstruction zones (polygons)
CREATE TABLE reconstruction_zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    province_id INT,
    geometry GEOMETRY(Polygon, 4326),
    total_mosques INT,
    completed INT,
    in_progress INT,
    not_started INT,
    total_budget NUMERIC,
    spent NUMERIC
);

-- Infrastructure (roads, utilities)
CREATE TABLE infrastructure (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50),  -- road, water, power, etc.
    geometry GEOMETRY(LineString, 4326),
    status VARCHAR(50),  -- operational, damaged, destroyed
    priority INT
);
```

#### **2. Spatial Queries**

```sql
-- Find mosques within 5km of a point
SELECT id, name, ST_Distance(geometry, ST_MakePoint(36.2, 37.1)::geography) / 1000 AS distance_km
FROM mosques
WHERE ST_DWithin(geometry, ST_MakePoint(36.2, 37.1)::geography, 5000)
ORDER BY distance_km;

-- Find mosques in a specific zone
SELECT m.*
FROM mosques m
JOIN reconstruction_zones z ON ST_Within(m.geometry, z.geometry)
WHERE z.name = 'North Aleppo Zone';

-- Calculate mosque density per square kilometer
SELECT
    province_id,
    COUNT(*) AS mosque_count,
    ST_Area(ST_ConvexHull(ST_Collect(geometry))::geography) / 1000000 AS area_km2,
    COUNT(*) / (ST_Area(ST_ConvexHull(ST_Collect(geometry))::geography) / 1000000) AS density
FROM mosques
GROUP BY province_id;

-- Find optimal reconstruction route (visit all mosques in zone)
WITH zone_mosques AS (
    SELECT geometry FROM mosques WHERE zone_id = 5
)
SELECT ST_MakeLine(geometry ORDER BY id) AS route
FROM zone_mosques;
```

#### **3. Heat Maps**

```python
import folium
from folium.plugins import HeatMap

def create_damage_heatmap(mosques: List[Mosque]) -> folium.Map:
    """
    Create heat map showing damage concentration.
    """

    # Center map on Syria
    m = folium.Map(location=[35.0, 38.0], zoom_start=7)

    # Prepare data: [lat, lng, weight]
    heat_data = [
        [mosque.lat, mosque.lng, mosque.damage_severity / 100]
        for mosque in mosques
    ]

    # Add heat map layer
    HeatMap(
        heat_data,
        radius=15,
        blur=25,
        max_zoom=1,
        gradient={
            0.0: 'green',
            0.5: 'yellow',
            1.0: 'red'
        }
    ).add_to(m)

    return m
```

#### **4. Clustering Analysis**

```python
from sklearn.cluster import DBSCAN
import numpy as np

def identify_reconstruction_zones(mosques: List[Mosque]) -> List[Zone]:
    """
    Use clustering to identify natural reconstruction zones.
    """

    # Extract coordinates
    coords = np.array([[m.lat, m.lng] for m in mosques])

    # DBSCAN clustering (density-based)
    # eps=0.05 means ~5km radius
    clustering = DBSCAN(eps=0.05, min_samples=3).fit(coords)

    # Group mosques by cluster
    zones = {}
    for idx, label in enumerate(clustering.labels_):
        if label not in zones:
            zones[label] = []
        zones[label].append(mosques[idx])

    # Create zone objects
    return [
        Zone(
            id=label,
            mosques=zone_mosques,
            center=calculate_centroid(zone_mosques),
            total_cost=sum(m.reconstruction_cost for m in zone_mosques),
            priority=calculate_zone_priority(zone_mosques)
        )
        for label, zone_mosques in zones.items()
        if label != -1  # -1 = noise
    ]
```

#### **5. Route Optimization**

```python
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def optimize_site_visit_route(mosques: List[Mosque], start_point: Point) -> Route:
    """
    Find optimal route to visit all mosques (Traveling Salesman Problem).
    """

    # Create distance matrix
    locations = [start_point] + [Point(m.lat, m.lng) for m in mosques]
    distance_matrix = calculate_distance_matrix(locations)

    # Setup routing model
    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        1,  # one vehicle
        0   # depot (start point)
    )

    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Solve
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_parameters)

    # Extract route
    route = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        if node > 0:  # Skip depot
            route.append(mosques[node - 1])
        index = solution.Value(routing.NextVar(index))

    return Route(
        stops=route,
        total_distance=solution.ObjectiveValue(),
        estimated_time=calculate_travel_time(solution.ObjectiveValue())
    )
```

### **GIS Desktop Integration**

```python
# Export to QGIS-compatible formats

def export_to_geojson(mosques: List[Mosque]) -> str:
    """Export mosques to GeoJSON for QGIS."""

    features = []
    for mosque in mosques:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [mosque.lng, mosque.lat]
            },
            "properties": {
                "name": mosque.name,
                "province": mosque.province,
                "damage_severity": mosque.damage_severity,
                "cost": mosque.reconstruction_cost,
                "status": mosque.status
            }
        })

    return json.dumps({
        "type": "FeatureCollection",
        "features": features
    })

def export_to_shapefile(mosques: List[Mosque], filename: str):
    """Export to Shapefile for ArcGIS/QGIS."""

    import geopandas as gpd

    gdf = gpd.GeoDataFrame(
        mosques,
        geometry=gpd.points_from_xy([m.lng for m in mosques], [m.lat for m in mosques])
    )

    gdf.to_file(filename, driver='ESRI Shapefile')
```

---

## 📊 Component 3: Predictive Analytics & ML

### **Purpose**
Use machine learning to predict costs, timelines, and optimize reconstruction planning.

### **Models**

#### **1. Cost Prediction Model**

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

class CostPredictionModel:
    """
    Predict reconstruction cost based on damage characteristics.
    """

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)

    def train(self, mosques: List[Mosque]):
        """Train model on historical data."""

        # Features
        X = [
            [
                m.damage_severity,
                m.building_size,
                m.has_minaret,
                m.has_dome,
                m.building_age,
                m.photo_count,
                m.province_cost_index
            ]
            for m in mosques
            if m.actual_cost  # Only mosques with known costs
        ]

        # Target
        y = [m.actual_cost for m in mosques if m.actual_cost]

        # Train
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        self.model.fit(X_train, y_train)

        # Evaluate
        score = self.model.score(X_test, y_test)
        print(f"Model R² score: {score}")

    def predict(self, mosque: Mosque) -> CostEstimate:
        """Predict cost for a mosque."""

        features = [
            [
                mosque.damage_severity,
                mosque.building_size,
                mosque.has_minaret,
                mosque.has_dome,
                mosque.building_age,
                mosque.photo_count,
                mosque.province_cost_index
            ]
        ]

        predicted_cost = self.model.predict(features)[0]

        # Calculate confidence interval
        predictions = [tree.predict(features)[0] for tree in self.model.estimators_]
        std = np.std(predictions)

        return CostEstimate(
            predicted_cost=predicted_cost,
            lower_bound=predicted_cost - (2 * std),
            upper_bound=predicted_cost + (2 * std),
            confidence=self.model.score
        )
```

#### **2. Timeline Forecasting**

```python
def predict_reconstruction_timeline(mosque: Mosque, resources: Resources) -> Timeline:
    """
    Estimate reconstruction timeline based on complexity and resources.
    """

    # Base time (months)
    base_time = {
        'minor': 2,
        'moderate': 6,
        'major': 12,
        'complete_rebuild': 18
    }[mosque.repair_scope]

    # Adjust for factors
    complexity_factor = mosque.damage_severity / 50  # 0.0 - 2.0
    resource_factor = 1.0 / (resources.workers / 10)  # More workers = faster
    weather_factor = 1.2 if mosque.region_climate == 'harsh' else 1.0
    security_factor = 1.5 if mosque.in_conflict_zone else 1.0

    estimated_months = base_time * complexity_factor * resource_factor * weather_factor * security_factor

    return Timeline(
        estimated_months=round(estimated_months),
        start_date=date.today(),
        estimated_completion=date.today() + timedelta(days=estimated_months * 30),
        milestones=generate_milestones(estimated_months),
        confidence=0.75
    )
```

#### **3. Priority Scoring Algorithm**

```python
def calculate_reconstruction_priority(mosque: Mosque, context: RegionContext) -> Priority:
    """
    Multi-factor priority scoring system.
    """

    scores = {
        'damage_severity': mosque.damage_severity * 0.25,  # 25% weight
        'community_size': min(mosque.worshipper_count / 1000, 1.0) * 0.20,  # 20%
        'historical_value': mosque.historical_significance * 0.15,  # 15%
        'accessibility': mosque.road_access_score * 0.10,  # 10%
        'security': mosque.security_status * 0.15,  # 15%
        'funding_available': mosque.funding_progress * 0.10,  # 10%
        'regional_need': context.mosque_density_deficit * 0.05  # 5%
    }

    total_score = sum(scores.values())

    # Classify priority
    if total_score > 0.8:
        level = 1  # Critical
    elif total_score > 0.6:
        level = 2  # High
    elif total_score > 0.4:
        level = 3  # Medium
    elif total_score > 0.2:
        level = 4  # Low
    else:
        level = 5  # Deferred

    return Priority(
        level=level,
        score=total_score,
        breakdown=scores,
        reasoning=generate_priority_explanation(scores)
    )
```

---

## 📱 Component 4: Mobile Progressive Web App (PWA)

### **Purpose**
Enable field workers to collect data offline, even in areas with poor connectivity.

### **Features**

#### **1. Offline-First Architecture**

```javascript
// Service Worker for offline caching

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('mosque-app-v1').then((cache) => {
      return cache.addAll([
        '/',
        '/index.html',
        '/styles.css',
        '/app.js',
        '/offline.html'
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});

// IndexedDB for offline data storage
import { openDB } from 'idb';

const dbPromise = openDB('mosque-db', 1, {
  upgrade(db) {
    db.createObjectStore('pending_submissions', { keyPath: 'id', autoIncrement: true });
    db.createObjectStore('mosques', { keyPath: 'id' });
  },
});

// Save submission offline
async function saveOffline(mosqueData) {
  const db = await dbPromise;
  await db.add('pending_submissions', {
    ...mosqueData,
    timestamp: Date.now(),
    synced: false
  });
}

// Sync when online
async function syncPendingSubmissions() {
  const db = await dbPromise;
  const pending = await db.getAll('pending_submissions');

  for (const submission of pending) {
    try {
      await fetch('/api/mosques', {
        method: 'POST',
        body: JSON.stringify(submission)
      });

      // Delete from pending
      await db.delete('pending_submissions', submission.id);
    } catch (error) {
      console.log('Still offline, will retry');
    }
  }
}

// Auto-sync when connection restored
window.addEventListener('online', syncPendingSubmissions);
```

#### **2. Camera Integration**

```javascript
// Capture photos with device camera

async function capturePhoto() {
  if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices) {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' }  // Rear camera
    });

    const video = document.getElementById('video');
    video.srcObject = stream;

    // Capture frame
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to blob
    canvas.toBlob((blob) => {
      const file = new File([blob], `mosque_photo_${Date.now()}.jpg`, {
        type: 'image/jpeg'
      });

      // Save offline
      savePhotoOffline(file);
    }, 'image/jpeg', 0.9);
  }
}
```

#### **3. GPS Location**

```javascript
// Get device location

function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
        },
        (error) => reject(error),
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    } else {
      reject('Geolocation not supported');
    }
  });
}
```

### **Mobile UI Design**

```
┌─────────────────────────────────────────────┐
│  📱 Mosque Data Collection                  │
│  ============================================│
│                                             │
│  [📸 Take Photo]  [🗺️ Get Location]        │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Province: [حلب ▼]                   │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Mosque Name: [____________]         │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Area: [____________]                │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Damage:                                   │
│  ( ) Partially Damaged                     │
│  (•) Completely Destroyed                  │
│                                             │
│  📸 Photos (3):                            │
│  [thumb] [thumb] [thumb]                   │
│                                             │
│  📍 Location: 36.2021, 37.1343 ✅          │
│                                             │
│  Notes:                                    │
│  ┌─────────────────────────────────────┐   │
│  │ [Optional notes...]                 │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [💾 Save Offline] [✅ Submit Now]        │
│                                             │
│  📊 Pending: 5 submissions (offline)       │
│  🔄 Auto-sync when online                  │
└─────────────────────────────────────────────┘
```

---

## 🔗 Component 5: GraphQL API & Partner Integration

### **Purpose**
Flexible API for third-party integrations (donors, NGOs, government systems).

### **GraphQL Schema**

```graphql
type Mosque {
  id: ID!
  name: String!
  province: Province!
  location: Location!
  damageAssessment: DamageAssessment
  reconstructionPlan: ReconstructionPlan
  photos: [Photo!]!
  donations: [Donation!]!
  timeline: Timeline
  status: Status!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Province {
  id: ID!
  name: String!
  mosques(filter: MosqueFilter): [Mosque!]!
  statistics: ProvinceStatistics!
}

type DamageAssessment {
  severity: Int!  # 0-100
  structuralDamage: StructuralDamage!
  costEstimate: Money!
  aiConfidence: Float!
  assessedBy: String
  assessedAt: DateTime!
}

type ReconstructionPlan {
  scope: String!
  estimatedCost: Money!
  timeline: Timeline!
  priority: Int!
  phases: [Phase!]!
}

type Donation {
  id: ID!
  donor: Donor!
  amount: Money!
  purpose: String
  date: DateTime!
  transactionId: String
}

# Queries
type Query {
  # Get single mosque
  mosque(id: ID!): Mosque

  # Search mosques
  mosques(
    filter: MosqueFilter
    sort: MosqueSort
    pagination: Pagination
  ): MosqueConnection!

  # Get province
  province(id: ID!): Province
  provinces: [Province!]!

  # Statistics
  statistics(provinceId: ID): Statistics!

  # Search by location
  mosquesNearPoint(
    lat: Float!
    lng: Float!
    radiusKm: Float!
  ): [Mosque!]!
}

# Mutations
type Mutation {
  # Create/Update
  createMosque(input: CreateMosqueInput!): Mosque!
  updateMosque(id: ID!, input: UpdateMosqueInput!): Mosque!

  # Donations
  recordDonation(input: DonationInput!): Donation!

  # Status updates
  updateReconstructionStatus(
    mosqueId: ID!
    status: Status!
    notes: String
  ): Mosque!
}

# Subscriptions (real-time)
type Subscription {
  # New mosque added
  mosqueAdded(provinceId: ID): Mosque!

  # Reconstruction progress updated
  reconstructionProgress(mosqueId: ID!): ProgressUpdate!

  # New donation received
  donationReceived(mosqueId: ID!): Donation!
}

# Input types
input MosqueFilter {
  provinceId: ID
  damageLevel: DamageLevel
  status: Status
  hasPhotos: Boolean
  hasLocation: Boolean
  search: String
}

enum DamageLevel {
  MINOR
  MODERATE
  SEVERE
  DESTROYED
}

enum Status {
  ASSESSED
  PLANNED
  FUNDED
  IN_PROGRESS
  COMPLETED
}
```

### **Example GraphQL Queries**

```graphql
# Get mosque with full details
query GetMosque($id: ID!) {
  mosque(id: $id) {
    id
    name
    province {
      name
    }
    location {
      lat
      lng
    }
    damageAssessment {
      severity
      costEstimate {
        amount
        currency
      }
      aiConfidence
    }
    photos {
      url
      thumbnail
      capturedAt
    }
    donations {
      donor {
        name
      }
      amount {
        amount
        currency
      }
      date
    }
    timeline {
      startDate
      estimatedCompletion
      progress
    }
  }
}

# Search mosques by damage level
query SearchDamagedMosques {
  mosques(
    filter: {
      damageLevel: SEVERE
      status: PLANNED
      provinceId: "5"  # Aleppo
    }
    sort: { field: PRIORITY, order: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    edges {
      node {
        id
        name
        damageAssessment {
          severity
          costEstimate {
            amount
          }
        }
        reconstructionPlan {
          priority
        }
      }
    }
    pageInfo {
      hasNextPage
      total
    }
  }
}

# Get statistics
query GetStatistics {
  statistics {
    totalMosques
    byStatus {
      assessed
      planned
      funded
      inProgress
      completed
    }
    byDamageLevel {
      minor
      moderate
      severe
      destroyed
    }
    totalCost {
      estimated
      actual
      funded
    }
  }
}

# Subscribe to real-time updates
subscription WatchProgress($mosqueId: ID!) {
  reconstructionProgress(mosqueId: $mosqueId) {
    mosqueId
    progress
    message
    timestamp
  }
}
```

### **Partner Integration Examples**

#### **1. Donor Platform**

```javascript
// Donor platform queries available mosques

const query = `
  query AvailableMosques {
    mosques(filter: { status: PLANNED }) {
      id
      name
      province { name }
      reconstructionPlan {
        estimatedCost {
          amount
          currency
        }
        priority
      }
      photos { thumbnail }
    }
  }
`;

// Display mosques, allow donation selection
```

#### **2. NGO Reporting**

```javascript
// NGO generates progress report

const query = `
  query ProjectProgress($ngoId: ID!) {
    mosques(filter: { fundedBy: $ngoId }) {
      name
      status
      timeline {
        progress
        estimatedCompletion
      }
      donations {
        total
      }
    }
  }
`;
```

#### **3. Government Dashboard**

```javascript
// Ministry dashboard showing national progress

const query = `
  query NationalOverview {
    provinces {
      name
      statistics {
        totalMosques
        completed
        inProgress
        planned
      }
    }
    statistics {
      totalCost {
        estimated
        actual
        funded
        remaining
      }
    }
  }
`;
```

---

## 💎 Component 6: Blockchain Donation Tracking (Optional)

### **Purpose**
Provide transparent, immutable donation tracking for international donors.

### **Features**

```solidity
// Smart Contract (Ethereum/Polygon)

pragma solidity ^0.8.0;

contract MosqueReconstruction {
    struct Mosque {
        string name;
        string location;
        uint256 estimatedCost;
        uint256 collectedFunds;
        address[] donors;
        bool reconstructionComplete;
    }

    mapping(uint256 => Mosque) public mosques;
    uint256 public mosqueCount;

    event DonationReceived(
        uint256 indexed mosqueId,
        address indexed donor,
        uint256 amount,
        uint256 timestamp
    );

    event ReconstructionComplete(
        uint256 indexed mosqueId,
        uint256 totalCost,
        uint256 timestamp
    );

    function donateTo Mosque(uint256 mosqueId) public payable {
        require(msg.value > 0, "Donation must be > 0");
        require(!mosques[mosqueId].reconstructionComplete, "Already completed");

        mosques[mosqueId].collectedFunds += msg.value;
        mosques[mosqueId].donors.push(msg.sender);

        emit DonationReceived(mosqueId, msg.sender, msg.value, block.timestamp);
    }

    function markComplete(uint256 mosqueId) public onlyOwner {
        mosques[mosqueId].reconstructionComplete = true;
        emit ReconstructionComplete(
            mosqueId,
            mosques[mosqueId].collectedFunds,
            block.timestamp
        );
    }

    function getDonors(uint256 mosqueId) public view returns (address[] memory) {
        return mosques[mosqueId].donors;
    }
}
```

---

## 💰 V3 Cost Breakdown

| Component | Monthly Cost | One-Time |
|-----------|--------------|----------|
| **VPS (8GB RAM)** | $20 | - |
| **Claude Vision API** | $5-10 | - |
| **PostGIS Hosting** | Included | - |
| **Mapbox API** | Free tier | - |
| **Photo Storage (S3)** | $3-5 | - |
| **Domain + SSL** | $1 | $12/year |
| **GraphQL API** | Free | - |
| **ML Training** | - | $50-100 |
| **Blockchain (optional)** | $2-3 | Gas fees |
| **Total** | **$31-39/month** | **$50-112** |

---

## 🚀 V2 to V3 Comparison

| Feature | Version 2 | Version 3 |
|---------|-----------|-----------|
| **Damage Assessment** | Manual | AI-powered (Claude Vision) |
| **Cost Estimation** | Fixed formulas | ML prediction |
| **Mapping** | Basic markers | Full GIS analysis |
| **Planning** | List-based | Spatial intelligence |
| **Mobile** | Responsive web | PWA with offline |
| **API** | REST only | REST + GraphQL |
| **Analytics** | Basic stats | Predictive ML models |
| **Donations** | Database only | + Blockchain option |
| **Integration** | Limited | Full partner ecosystem |
| **Cost** | $15/month | $30/month |

---

## 📦 V3 Deliverables

### **For Field Teams:**
- Mobile PWA app
- Offline data collection
- GPS + camera integration
- Arabic interface

### **For Planners:**
- GIS desktop integration
- QGIS/ArcGIS exports
- Route optimization
- Zone planning

### **For Ministry:**
- Full dashboard
- Predictive analytics
- Progress tracking
- Budget management

### **For Partners:**
- GraphQL API
- Webhook integrations
- Real-time subscriptions
- Documentation

### **For Donors:**
- Transparent tracking
- Photo verification
- Progress updates
- Blockchain receipts

---

## 🎯 Next Steps to Start V3

1. ✅ **Complete V2** - Get real-time system working
2. ✅ **Collect training data** - 100+ mosques with damage assessments
3. ✅ **Setup PostGIS** - Migrate to spatial database
4. ✅ **Train ML models** - Cost prediction, priority scoring
5. ✅ **Build PWA** - Mobile app with offline support
6. ✅ **Implement GraphQL** - API for partners
7. ✅ **Deploy GIS layers** - Satellite imagery, infrastructure

---

**Document Version:** 1.0
**Created:** October 25, 2025
**Status:** Planning Phase
**Owner:** [Your Name]

---

**Ready to start V3 after V2 is stable!** 🚀
