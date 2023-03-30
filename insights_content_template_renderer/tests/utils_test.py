"""
Unit tests for utils.py
"""

import pydantic
from typing import List
import pytest
from insights_content_template_renderer import utils
from insights_content_template_renderer.models import Report, Content, RendererRequest, RenderedReport, RendererResponse

from insights_content_template_renderer.data import example_request_data


def test_get_reported_error_key():
    """
    Checks that the get_reported_error_key() function parses reported error key correctly.
    """
    cluster_reports = example_request_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    reported_error_key = utils.get_reported_error_key(report)
    assert reported_error_key == "RULE_1"


def test_get_reported_module():
    """
    Checks that the get_reported_module() function parses reported error key correctly.
    """
    cluster_reports = example_request_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    reported_module = utils.get_reported_module(report)
    assert reported_module == "ccx_rules_ocp.external.rules.1"


def test_render_resolution():
    """
    Checks that the render_resolution() function renders resolution correctly.
    """
    cluster_reports = example_request_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    rule_content = Content.parse_obj(example_request_data["content"][0])
    result = "Red Hat recommends you to fix the issues with this node"

    rendered = utils.render_resolution(rule_content, report)
    assert rendered == result


def test_render_reason():
    """
    Checks that render_reason() function renders reason correctly.
    """
    cluster_reports = example_request_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    rule_content = Content.parse_obj(example_request_data["content"][0])
    rendered = utils.render_reason(rule_content, report)
    result = "Node not working."
    assert rendered == result


def test_render_description():
    """
    Checks that render_reason() function renders reason correctly.
    """
    cluster_reports = example_request_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    rule_content = Content.parse_obj(example_request_data["content"][0])
    result = "RULE_1 description foo1"
    rendered = utils.render_description(rule_content, report)

    assert rendered == result



def test_render_report():
    """
    Checks that render_report() renders the whole report correctly.
    """
    cluster_reports = example_request_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    contents = pydantic.parse_obj_as(List[Content], example_request_data["content"])
    result = RenderedReport(
        rule_id = "ccx_rules_ocp.external.rules.1",
        error_key = "RULE_1",
        resolution = "Red Hat recommends you to fix the issues with this node",
        reason = "Node not working.",
        description = "RULE_1 description foo1"
    )
    rendered = utils.render_report(contents, report)
    assert rendered == result


def test_render_report_missing_rule_content():
    """
    Checks that render_report() function raises exception in case
    that content for the reported rule is missing.
    """
    cluster_reports = example_request_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = Report.parse_obj(cluster_reports["reports"][0])
    contents = example_request_data["content"].copy()
    del contents[0]
    contents = pydantic.parse_obj_as(List[Content], contents)
    with pytest.raises(utils.RuleNotFoundException):
        utils.render_report(contents, report)


def test_render_reports():
    """
    Checks that render_reports() function renders all reports correctly.
    """
    result = {
        "clusters": [
            "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
        ],
        "reports": {
            "5d5892d3-1f74-4ccf-91af-548dfc9767aa": [
            {
                "rule_id": "ccx_rules_ocp.external.rules.1",
                "error_key": "RULE_1",
                "resolution": "Red Hat recommends you to fix the issues with this node",
                "reason": "Node not working.",
                "description": "RULE_1 description foo1"
            }
            ]
        }
    }
    req = RendererRequest.parse_obj(example_request_data)
    rendered = utils.render_reports(req)
    assert RendererResponse.parse_obj(rendered) == result
