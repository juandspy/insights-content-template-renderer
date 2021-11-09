import pytest
import json
import utils

test_data = {}
with open("request_data_example.json") as f:
    test_data = json.load(f)

def test_get_reported_error_key():
    report = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]["reports"][0]
    reported_error_key = utils.get_reported_error_key(report)
    assert reported_error_key == "NODES_MINIMUM_REQUIREMENTS_NOT_MET"

def test_get_reported_module():
    report = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]["reports"][0]
    reported_module = utils.get_reported_module(report)
    assert reported_module == "nodes_requirements_check"

def test_render_resolution():
    report = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]["reports"][0]
    rule_content = test_data["content"][2]
    assert utils.render_resolution(rule_content, report) == 'Red Hat recommends that you configure your nodes to meet the minimum resource requirements.Make sure that:1. Node foo1 (undefined) * Has enough memory, minimum requirement is 16. Currently its only configured with 8.16GB.'

def test_render_reason():
    report = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]["reports"][0]
    rule_content = test_data["content"][2]
    assert utils.render_reason(rule_content, report) == 'Node not meeting the minimum requirements:1. foo1 * Roles: undefined * Minimum memory requirement is 16, but the node is configured with 8.16.'
