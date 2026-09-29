# Backend Schema

## equipment
id, name, asset_type, location

## sensor_readings
id, equipment_id, temperature_c, vibration_mm_s, pressure_psi, rpm, operating_hours, voltage_v, current_a, ambient_temp_c, created_at

## predictions
id, equipment_id, risk_probability, risk_level, threshold, created_at

See database/schema.sql.
