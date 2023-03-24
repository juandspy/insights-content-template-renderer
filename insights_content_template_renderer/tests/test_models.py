from insights_content_template_renderer.models import *
from pathlib import Path
import json


test_data = {}
test_data_path = Path(__file__).with_name("request_data_example.json")
with test_data_path.open(encoding="UTF-8") as f:
    test_data = json.load(f)

def test_renderer_request():
    req = RendererRequest.parse_obj(test_data)
    assert req.\
        report_data.\
        reports["5d5892d3-1f74-4ccf-91af-548dfc9767aa"].\
        reports[0].component == \
            "ccx_rules_ocp.external.rules.nodes_requirements_check.report"

