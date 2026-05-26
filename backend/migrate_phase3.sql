-- Phase 3 Database Migration
-- Run these in MySQL Workbench on demand_forecasting database

USE demand_forecasting;

-- Add role column to users (if not exists)
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'analyst';

-- Update existing admins to super_admin role
UPDATE users SET role = 'super_admin' WHERE is_admin = 1;
UPDATE users SET role = 'analyst' WHERE is_admin = 0 AND role IS NULL;

-- Create activity_logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100) NULL,
    resource_id INT NULL,
    method VARCHAR(10) NULL,
    endpoint VARCHAR(255) NULL,
    status_code INT NULL,
    ip_address VARCHAR(50) NULL,
    details JSON NULL,
    response_time_ms INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_action (action)
);

-- Create anomaly_detections table
CREATE TABLE IF NOT EXISTS anomaly_detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id INT NOT NULL,
    owner_id INT NOT NULL,
    target_column VARCHAR(100) NOT NULL,
    date_column VARCHAR(100) NOT NULL,
    anomalies JSON NULL,
    anomaly_count INT DEFAULT 0,
    severity VARCHAR(20) DEFAULT 'low',
    summary TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create cache_entries table
CREATE TABLE IF NOT EXISTS cache_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_value TEXT NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cache_key (cache_key),
    INDEX idx_expires_at (expires_at)
);

SELECT 'Phase 3 migration complete!' AS status;
