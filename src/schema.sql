-- PostgreSQL Schema for Mosque Reconstruction Database
-- Project: مشروع إعادة إعمار المساجد

-- Provinces (Topics from Telegram)
CREATE TABLE IF NOT EXISTS provinces (
    id SERIAL PRIMARY KEY,
    name_ar VARCHAR(100) NOT NULL UNIQUE,
    name_en VARCHAR(100),
    topic_id INTEGER UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mosques (Core entity)
CREATE TABLE IF NOT EXISTS mosques (
    id SERIAL PRIMARY KEY,
    province_id INTEGER REFERENCES provinces(id),
    mosque_name VARCHAR(255) NOT NULL,
    area_name VARCHAR(255),
    source_message_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(province_id, mosque_name, area_name)
);

-- Damage Status
CREATE TABLE IF NOT EXISTS damage_status (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    damage_type VARCHAR(50) CHECK (damage_type IN ('damaged', 'demolished', 'unknown')),
    source_file_id INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Files (Excel, photos, etc.)
CREATE TABLE IF NOT EXISTS files (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    sha256 VARCHAR(64),
    mime_type VARCHAR(100),
    message_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Photos linked to mosques
CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    file_id INTEGER REFERENCES files(id),
    file_path TEXT NOT NULL,
    caption TEXT,
    message_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Location data
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    mosque_id INTEGER REFERENCES mosques(id) ON DELETE CASCADE,
    raw_text TEXT,
    gmaps_url TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    confidence VARCHAR(50),
    geocoded_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Message index for provenance tracking
CREATE TABLE IF NOT EXISTS message_index (
    id SERIAL PRIMARY KEY,
    message_id INTEGER UNIQUE NOT NULL,
    topic_id INTEGER,
    date TIMESTAMP,
    from_user VARCHAR(255),
    message_type VARCHAR(50),
    has_photo BOOLEAN DEFAULT FALSE,
    has_file BOOLEAN DEFAULT FALSE,
    has_text BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_mosques_province ON mosques(province_id);
CREATE INDEX idx_photos_mosque ON photos(mosque_id);
CREATE INDEX idx_locations_mosque ON locations(mosque_id);
CREATE INDEX idx_damage_mosque ON damage_status(mosque_id);
CREATE INDEX idx_message_index_topic ON message_index(topic_id);
CREATE INDEX idx_message_index_date ON message_index(date);
