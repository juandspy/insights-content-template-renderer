from insights_content_template_renderer.models import *
from insights_content_template_renderer.tests.utils_test import test_request_data


def test_renderer_request():
    req = RendererRequest.parse_obj(test_request_data)
    assert req.\
        report_data.\
        reports["5d5892d3-1f74-4ccf-91af-548dfc9767aa"].\
        reports[0].component == \
            "ccx_rules_ocp.external.rules.nodes_requirements_check.report"

