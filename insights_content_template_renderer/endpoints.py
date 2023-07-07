"""
Contains service endpoints.
"""

import logging
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator

from insights_content_template_renderer.utils import render_reports
from insights_content_template_renderer.logging_utils import setup_watchtower
from insights_content_template_renderer.models import RendererRequest, RendererResponse


app = FastAPI()
setup_watchtower()
log = logging.getLogger(__name__)


instrumentator = Instrumentator().instrument(app)

@app.on_event("startup")
async def expose_metrics():
    instrumentator.expose(app, endpoint='/metrics', tags=['metrics'])


@app.post("/rendered_reports", response_model=RendererResponse)
@app.post("/v1/rendered_reports", response_model=RendererResponse)
async def rendered_reports(data: RendererRequest):
    """
    Endpoint for rendering reports based on DoT.js content templates and report details.

    :param data: request containing JSON body with required data
    :return: JSON with rendered reports
    """
    log.info("Received request for /rendered_reports")
    log.debug("Rendering report")
    try:
        rendered_report = render_reports(data)
        log.debug("Report successfully rendered")
    except Exception as exc:
        log.error("error rendering template")
        log.error(f"data:\n{data.json()}")
        log.error(f"exception:\n{exc}")
        return PlainTextResponse("Internal Server Error", 500)
    return rendered_report
