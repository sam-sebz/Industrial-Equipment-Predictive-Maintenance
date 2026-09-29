from pathlib import Path
import json, joblib, pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from .db import init_db, add_prediction, history

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"artifacts"; UI=ROOT/"ui"
app=FastAPI(title="Predictive Maintenance")

class SensorIn(BaseModel):
    equipment_id:int=1
    temperature_c:float=Field(ge=0,le=150)
    vibration_mm_s:float=Field(ge=0,le=30)
    pressure_psi:float=Field(ge=0,le=200)
    rpm:float=Field(ge=0,le=4000)
    operating_hours:float=Field(ge=0,le=50000)
    voltage_v:float=Field(ge=0,le=600)
    current_a:float=Field(ge=0,le=100)
    ambient_temp_c:float=Field(ge=-20,le=70)

@app.on_event("startup")
def startup(): init_db()

@app.get("/api/health")
def health(): return {"status":"ok"}

@app.get("/api/metrics")
def metrics():
    p=ART/"metrics.json"
    return json.loads(p.read_text()) if p.exists() else {}

@app.post("/api/predict")
def predict(x:SensorIn):
    mp=ART/"maintenance_model.joblib"
    if not mp.exists(): raise HTTPException(503,"Model missing. Run python src/train_model.py")
    payload=x.model_dump(); eid=payload.pop("equipment_id")
    values=list(payload.values())
    model=joblib.load(mp)
    proba=float(model.predict_proba(pd.DataFrame([payload]))[:,1][0])
    threshold=float(metrics().get("threshold",.36))
    level="high" if proba>=threshold else ("medium" if proba>=threshold*.65 else "low")
    pid=add_prediction(eid,proba,level,threshold,values)
    return {"risk_probability":proba,"risk_percent":round(proba*100,2),"risk_level":level,"threshold":threshold,"prediction_id":pid}

@app.get("/api/predictions")
def predictions(): return history()

@app.get("/")
def root(): return FileResponse(UI/"index.html")
