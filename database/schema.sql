CREATE TABLE IF NOT EXISTS equipment (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 asset_type TEXT NOT NULL,
 location TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sensor_readings (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 equipment_id INTEGER NOT NULL,
 temperature_c REAL NOT NULL,
 vibration_mm_s REAL NOT NULL,
 pressure_psi REAL NOT NULL,
 rpm REAL NOT NULL,
 operating_hours REAL NOT NULL,
 voltage_v REAL NOT NULL,
 current_a REAL NOT NULL,
 ambient_temp_c REAL NOT NULL,
 created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS predictions (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 equipment_id INTEGER NOT NULL,
 risk_probability REAL NOT NULL,
 risk_level TEXT NOT NULL,
 threshold REAL NOT NULL,
 created_at TEXT NOT NULL
);
