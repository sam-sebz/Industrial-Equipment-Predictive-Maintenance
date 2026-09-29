import asyncio,httpx
from src.main import app
from src.db import init_db
init_db()
async def main():
    transport=httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,base_url="http://test") as c:
        assert (await c.get("/api/health")).status_code==200
        r=await c.post("/api/predict",json={"equipment_id":1,"temperature_c":90,"vibration_mm_s":7,"pressure_psi":95,"rpm":1900,"operating_hours":9000,"voltage_v":430,"current_a":30,"ambient_temp_c":38})
        assert r.status_code==200 and "risk_probability" in r.json()
    print("P2 smoke tests passed")
asyncio.run(main())