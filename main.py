import uvicorn
from fastapi import Request, FastAPI
from utils import render_reports
from logger import logger

app = FastAPI()

@app.post("/rendered_reports")
async def rendered_reports(request : Request):
    logger.info("Received request for /rendered_reports")
    data = await request.json()
    return render_reports(data)
