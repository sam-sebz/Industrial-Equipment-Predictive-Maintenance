import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"data"/"maintenance.db"
SCHEMA=ROOT/"database"/"schema.sql"

def conn():
    DB.parent.mkdir(exist_ok=True)
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
    with conn() as c:
        c.executescript(SCHEMA.read_text())
        if not c.execute("SELECT 1 FROM equipment LIMIT 1").fetchone():
            c.execute("INSERT INTO equipment(name,asset_type,location) VALUES(?,?,?)",("Compressor-01","Compressor","Plant-A"))
            c.commit()

def add_prediction(eid,p,level,threshold,values):
    now=datetime.now(timezone.utc).isoformat()
    with conn() as c:
        c.execute("INSERT INTO sensor_readings(equipment_id,temperature_c,vibration_mm_s,pressure_psi,rpm,operating_hours,voltage_v,current_a,ambient_temp_c,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(eid,*values,now))
        cur=c.execute("INSERT INTO predictions(equipment_id,risk_probability,risk_level,threshold,created_at) VALUES(?,?,?,?,?)",(eid,p,level,threshold,now))
        c.commit(); return cur.lastrowid

def history(limit=50):
    with conn() as c:
        return [dict(x) for x in c.execute("SELECT p.*,e.name FROM predictions p JOIN equipment e ON e.id=p.equipment_id ORDER BY p.id DESC LIMIT ?",(limit,)).fetchall()]
