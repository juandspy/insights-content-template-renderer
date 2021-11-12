from fastapi import Request, FastAPI
from app.utils import render_reports
from app.logger import log

app = FastAPI()


@app.post("/rendered_reports")
async def rendered_reports(request: Request):
    log.info("Received request for /rendered_reports")
    data = await request.json()
    return render_reports(data)
