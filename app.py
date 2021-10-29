from fastapi import Request, FastAPI
from utils import render_reports

app = FastAPI()

@app.post("/rendered_reports")
async def rendered_reports(request : Request):
    data = await request.json()
    return render_reports(data)
