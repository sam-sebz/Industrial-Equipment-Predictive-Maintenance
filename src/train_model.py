from pathlib import Path
import json, joblib
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"artifacts"; ART.mkdir(exist_ok=True)
( ROOT/"data" ).mkdir(exist_ok=True)
rng=np.random.default_rng(2026); n=15000

temperature=rng.normal(72,11,n).clip(35,115)
vibration=rng.gamma(2.2,1.8,n).clip(.05,18)
pressure=rng.normal(82,10,n).clip(45,120)
rpm=rng.normal(1750,240,n).clip(700,2600)
hours=rng.uniform(100,12000,n)
voltage=rng.normal(415,14,n).clip(360,470)
current=rng.normal(24,5,n).clip(5,45)
ambient=rng.normal(31,5,n).clip(15,48)

z=(-7+.065*(temperature-65)+.23*vibration+.055*np.abs(pressure-82)+.00020*hours
   +.004*np.abs(rpm-1750)+.020*np.abs(voltage-415)+.030*np.maximum(current-25,0)
   +.035*np.maximum(ambient-32,0)+.55*((temperature>92)&(vibration>5)))
prob=1/(1+np.exp(-z)); failure=rng.binomial(1,prob)

X=pd.DataFrame({"temperature_c":temperature,"vibration_mm_s":vibration,
                "pressure_psi":pressure,"rpm":rpm,"operating_hours":hours,
                "voltage_v":voltage,"current_a":current,"ambient_temp_c":ambient})
y=failure
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.20,random_state=42,stratify=y)

models={
"Logistic Regression":Pipeline([("scale",StandardScaler()),("m",LogisticRegression(max_iter=2000,random_state=42))]),
"Random Forest":RandomForestClassifier(n_estimators=300,max_depth=12,min_samples_leaf=3,class_weight="balanced",random_state=42,n_jobs=-1),
"Gradient Boosting":GradientBoostingClassifier(n_estimators=250,learning_rate=.06,max_depth=3,random_state=42)
}
rows=[]; fitted={}
for name,m in models.items():
    m.fit(Xtr,ytr); fitted[name]=m; pred=m.predict(Xte); score=m.predict_proba(Xte)[:,1]
    rows.append([name,accuracy_score(yte,pred),precision_score(yte,pred,zero_division=0),
                 recall_score(yte,pred,zero_division=0),f1_score(yte,pred,zero_division=0),roc_auc_score(yte,score)])

result=pd.DataFrame(rows,columns=["model","accuracy","precision","recall","f1","roc_auc"]).sort_values("f1",ascending=False)
best=result.iloc[0].model
model=fitted[best]
score=model.predict_proba(Xte)[:,1]

tr=[]
for t in np.arange(.10,.61,.02):
    pred=(score>=t).astype(int)
    tr.append([t,precision_score(yte,pred,zero_division=0),recall_score(yte,pred,zero_division=0),f1_score(yte,pred,zero_division=0)])
tdf=pd.DataFrame(tr,columns=["threshold","precision","recall","f1"])
bt=tdf.loc[tdf.f1.idxmax()]

metrics={"records":n,"features":8,"failure_rate":float(y.mean()),
         "models_compared":3,"best_model":best,"best_roc_auc":float(result.iloc[0].roc_auc),
         "threshold":float(bt.threshold),"threshold_precision":float(bt.precision),
         "threshold_recall":float(bt.recall),"threshold_f1":float(bt.f1)}

X.to_csv(ROOT/"data"/"industrial_sensor_data.csv",index=False)
pd.DataFrame({"failure":y}).to_csv(ROOT/"data"/"labels.csv",index=False)
result.to_csv(ART/"model_comparison.csv",index=False)
(ART/"metrics.json").write_text(json.dumps(metrics,indent=2))
joblib.dump(model,ART/"maintenance_model.joblib")
print(json.dumps(metrics,indent=2))
