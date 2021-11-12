"""
Contains app initialization and its only endpoint.
"""

from fastapi import Request, FastAPI
from app.utils import render_reports
from app.logger import log

app = FastAPI()


@app.post("/rendered_reports")
async def rendered_reports(request: Request):
    """
    Endpoint for rendering reports based on DoT.js content templates and report details.

    :param request: request containing JSON body with required data
    :return: JSON with rendered reports
    """
    log.info("Received request for /rendered_reports")
    data = await request.json()
    return render_reports(data)
