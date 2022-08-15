"""
Unit tests for utils.py
"""

import json
from pathlib import Path
import pytest
from insights_content_template_renderer import utils


test_data = {}
test_data_path = Path(__file__).with_name("request_data_example.json")
with test_data_path.open(encoding="UTF-8") as f:
    test_data = json.load(f)


def test_get_reported_error_key():
    """
    Checks that the get_reported_error_key() function parses reported error key correctly.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    reported_error_key = utils.get_reported_error_key(report)
    assert reported_error_key == "NODES_MINIMUM_REQUIREMENTS_NOT_MET"


def test_get_reported_module():
    """
    Checks that the get_reported_module() function parses reported error key correctly.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    reported_module = utils.get_reported_module(report)
    assert reported_module == "ccx_rules_ocp.external.rules.nodes_requirements_check"


def test_get_reported_module_component_field_missing():
    """
    Checks that the get_reported_module() function raises error
    in case the required field is missing.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    del report["component"]
    with pytest.raises(ValueError):
        utils.get_reported_module(report)


def test_get_reported_error_key_key_field_missing():
    """
    Checks that the get_reported_error_key() function raises error
    in case the required field is missing.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    del report["key"]
    with pytest.raises(ValueError):
        utils.get_reported_error_key(report)


def test_render_resolution():
    """
    Checks that th render_resolution() function renders resolution correctly.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    rule_content = test_data["content"][2].copy()
    result = (
        "Red Hat recommends that you configure your nodes to meet the minimum resource "
        "requirements.Make sure that:1. Node foo1 (undefined) * Has enough memory, "
        "minimum requirement is 16. Currently its only configured with 8.16GB."
    )
    assert utils.render_resolution(rule_content, report) == result


def test_render_reason():
    """
    Checks that render_reason() function renders reason correctly.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    rule_content = test_data["content"][2]
    assert (
        utils.render_reason(rule_content, report) == "Node not meeting the minimum "
        "requirements:1. foo1 * Roles: undefined "
        "* Minimum memory requirement is 16, "
        "but the node is configured with 8.16."
    )


def test_render_description():
    """
    Checks that render_reason() function renders reason correctly.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    rule_content = test_data["content"][2]
    assert (
        utils.render_description(rule_content, report)
        == "An OCP node foo1 behaves unexpectedly when it doesn't meet the minimum resource requirements"
    )


def test_render_report():
    """
    Checks that render_report() renders the whole report correctly.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    content = test_data["content"].copy()
    result = {
        "rule_id": "ccx_rules_ocp.external.rules.nodes_requirements_check",
        "error_key": "NODES_MINIMUM_REQUIREMENTS_NOT_MET",
        "resolution": "Red Hat recommends that you configure your nodes to meet the minimum "
        "resource requirements.Make sure that:1. Node foo1 (undefined) * Has enough "
        "memory, minimum requirement is 16. Currently its only configured with "
        "8.16GB.",
        "reason": "Node not meeting the minimum requirements:1. foo1 * Roles: undefined * Minimum "
        "memory requirement is 16, but the node is configured with 8.16.",
        "description": "An OCP node foo1 behaves unexpectedly when it doesn't meet the minimum resource requirements",
    }
    assert utils.render_report(content, report) == result


def test_render_report_missing_rule_content():
    """
    Checks that render_report() function raises exception in case
    that content for the reported rule is missing.
    """
    cluster_reports = test_data["report_data"]["reports"][
        "5d5892d3-1f74-4ccf-91af-548dfc9767aa"
    ]
    report = cluster_reports["reports"][0].copy()
    content = test_data["content"].copy()
    del content[2]
    with pytest.raises(utils.RuleNotFoundException):
        utils.render_report(content, report)


def test_render_reports():
    """
    Checks that render_reports() function renders all reports correctly.
    """
    result = {
        "clusters": ["5d5892d3-1f74-4ccf-91af-548dfc9767aa"],
        "reports": {
            "5d5892d3-1f74-4ccf-91af-548dfc9767aa": [
                {
                    "rule_id": "ccx_rules_ocp.external.rules.nodes_requirements_check",
                    "error_key": "NODES_MINIMUM_REQUIREMENTS_NOT_MET",
                    "description": "An OCP node foo1 behaves unexpectedly when it doesn't meet "
                    "the minimum resource requirements",
                    "resolution": "Red Hat recommends that you configure your nodes to meet the "
                    "minimum resource requirements.Make sure that:1. Node foo1 ("
                    "undefined) * Has enough memory, minimum requirement is 16. "
                    "Currently its only configured with 8.16GB.",
                    "reason": "Node not meeting the minimum requirements:1. foo1 * Roles: "
                    "undefined * Minimum memory requirement is 16, but the node is "
                    "configured with 8.16.",
                },
                {
                    "rule_id": "ccx_rules_ocp.external.rules.samples_op_failed_image_import_check",
                    "error_key": "SAMPLES_FAILED_IMAGE_IMPORT_ERR",
                    "description": "Pods could fail to start if openshift-samples is degraded "
                    "due to FailedImageImport which is caused by a hiccup while "
                    "talking to the Red Hat registry",
                    "resolution": "Red Hat recommends that you to follow these steps:1. Fix 1, "
                    "Try running:~~~# oc import-image <for the ImageStream(s) in "
                    "question>~~~1. Fix 2, Try running:~~~# oc delete "
                    "configs.samples cluster~~~",
                    "reason": "Due to a temporary hiccup talking to the Red Hat registry the "
                    "openshift-samples failed to import some of the imagestreams.Source "
                    "of the issue:**Cluster-operator:**  **openshift-samples**- "
                    "*Condition:* Degraded- *Reason:* FailedImageImports- *Message:* "
                    "Samples installed at 4.2.0, with image import failures for these "
                    "imagestreams: php - *Last* Transition: 2020-03-19T08:32:53Z",
                },
                {
                    "rule_id": "ccx_rules_ocp.external.rules.cluster_wide_proxy_auth_check",
                    "error_key": "AUTH_OPERATOR_PROXY_ERROR",
                    "description": "The authentication operator is degraded when cluster "
                    "is configured to use a cluster-wide proxy",
                    "resolution": "Red Hat recommends that you to follow steps in the KCS "
                    "article. * [Authentication operator Degraded with Reason "
                    "`WellKnownEndpointDegradedError`]("
                    "https://access.redhat.com/solutions/4569191)",
                    "reason": "Requests to routes and/or the public API endpoint are not being "
                    "proxied to the cluster.",
                },
            ]
        },
    }
    assert utils.render_reports(test_data) == result


def test_render_reports_missing_content():
    """
    Checks that render_reports() function raises exception if the content data are missing.
    """
    data = test_data.copy()
    del data["content"]
    with pytest.raises(ValueError):
        utils.render_reports(data)


def test_render_reports_missing_report_data():
    """
    Checks that render_reports() function raises exception if the report data are missing.
    """
    data = test_data.copy()
    del data["report_data"]
    with pytest.raises(ValueError):
        utils.render_reports(data)


def test_render_reports_missing_clusters():
    """
    Checks that render_reports() function raises exception
    if the data for reported clusters are missing.
    """
    data = test_data.copy()
    del data["report_data"]["clusters"]
    with pytest.raises(ValueError):
        utils.render_reports(data)


def test_render_reports_missing_reports():
    """
    Checks that render_reports() function raises exception
    if the data for individual reports are missing.
    """
    data = test_data.copy()
    del data["report_data"]["reports"]
    with pytest.raises(ValueError):
        utils.render_reports(data)
