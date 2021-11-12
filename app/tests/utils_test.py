import pytest
import json
from app import utils
from pathlib import Path


test_data = {}
test_data_path = Path(__file__).with_name("request_data_example.json")
with test_data_path.open() as f:
    test_data = json.load(f)


def test_get_reported_error_key():
    cluster_reports = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]
    report = cluster_reports["reports"][0].copy()
    reported_error_key = utils.get_reported_error_key(report)
    assert reported_error_key == "NODES_MINIMUM_REQUIREMENTS_NOT_MET"


def test_get_reported_module():
    cluster_reports = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]
    report = cluster_reports["reports"][0].copy()
    reported_module = utils.get_reported_module(report)
    assert reported_module == "nodes_requirements_check"


def test_get_reported_module_rule_id_missing():
    cluster_reports = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]
    report = cluster_reports["reports"][0].copy()
    del report['rule_id']
    with pytest.raises(ValueError):
        utils.get_reported_module(report)


def test_get_reported_module_rule_id_wrong_format():
    cluster_reports = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]
    report = cluster_reports["reports"][0].copy()
    report['rule_id'] = report['rule_id'].replace('|', ';')
    with pytest.raises(ValueError):
        utils.get_reported_module(report)


def test_render_resolution():
    cluster_reports = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]
    report = cluster_reports["reports"][0].copy()
    rule_content = test_data["content"][2].copy()
    result = 'Red Hat recommends that you configure your nodes to meet the minimum resource ' \
             'requirements.Make sure that:1. Node foo1 (undefined) * Has enough memory, ' \
             'minimum requirement is 16. Currently its only configured with 8.16GB.'
    assert utils.render_resolution(rule_content, report) == result


def test_render_reason():
    cluster_reports = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]
    report = cluster_reports["reports"][0].copy()
    rule_content = test_data["content"][2]
    assert utils.render_reason(rule_content, report) == 'Node not meeting the minimum ' \
                                                        'requirements:1. foo1 * Roles: undefined ' \
                                                        '* Minimum memory requirement is 16, ' \
                                                        'but the node is configured with 8.16.'


def test_render_report():
    cluster_reports = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]
    report = cluster_reports["reports"][0].copy()
    content = test_data["content"].copy()
    result = {
        'rule_id': 'nodes_requirements_check',
        'error_key': 'NODES_MINIMUM_REQUIREMENTS_NOT_MET',
        'resolution': 'Red Hat recommends that you configure your nodes to meet the minimum '
                      'resource requirements.Make sure that:1. Node foo1 (undefined) * Has enough '
                      'memory, minimum requirement is 16. Currently its only configured with '
                      '8.16GB.',
        'reason': 'Node not meeting the minimum requirements:1. foo1 * Roles: undefined * Minimum '
                  'memory requirement is 16, but the node is configured with 8.16.'}
    assert utils.render_report(content, report) == result


def test_render_report_missing_rule_content():
    cluster_reports = test_data["report_data"]["reports"]["5d5892d3-1f74-4ccf-91af-548dfc9767aa"]
    report = cluster_reports["reports"][0].copy()
    content = test_data["content"].copy()
    del content[2]
    with pytest.raises(utils.RuleNotFoundException):
        utils.render_report(content, report)


def test_render_reports():
    result = {
        'clusters': ['5d5892d3-1f74-4ccf-91af-548dfc9767aa'],
        'reports': {
            '5d5892d3-1f74-4ccf-91af-548dfc9767aa': [
                {
                    'rule_id': 'nodes_requirements_check',
                    'error_key': 'NODES_MINIMUM_REQUIREMENTS_NOT_MET',
                    'resolution': 'Red Hat recommends that you configure your nodes to meet the '
                                  'minimum resource requirements.Make sure that:1. Node foo1 ('
                                  'undefined) * Has enough memory, minimum requirement is 16. '
                                  'Currently its only configured with 8.16GB.',
                    'reason': 'Node not meeting the minimum requirements:1. foo1 * Roles: '
                              'undefined * Minimum memory requirement is 16, but the node is '
                              'configured with 8.16.'
                },
                {
                    'rule_id': 'samples_op_failed_image_import_check',
                    'error_key': 'SAMPLES_FAILED_IMAGE_IMPORT_ERR',
                    'resolution': 'Red Hat recommends that you to follow these steps:1. Fix 1, '
                                  'Try running:~~~# oc import-image <for the ImageStream(s) in '
                                  'question>~~~1. Fix 2, Try running:~~~# oc delete '
                                  'configs.samples cluster~~~',
                    'reason': 'Due to a temporary hiccup talking to the Red Hat registry the '
                              'openshift-samples failed to import some of the imagestreams.Source '
                              'of the issue:**Cluster-operator:**  **openshift-samples**- '
                              '*Condition:* Degraded- *Reason:* FailedImageImports- *Message:* '
                              'Samples installed at 4.2.0, with image import failures for these '
                              'imagestreams: php - *Last* Transition: 2020-03-19T08:32:53Z'
                },
                {
                    'rule_id': 'cluster_wide_proxy_auth_check',
                    'error_key': 'AUTH_OPERATOR_PROXY_ERROR',
                    'resolution': 'Red Hat recommends that you to follow steps in the KCS '
                                  'article. * [Authentication operator Degraded with Reason '
                                  '`WellKnownEndpointDegradedError`]('
                                  'https://access.redhat.com/solutions/4569191)',
                    'reason': 'Requests to routes and/or the public API endpoint are not being '
                              'proxied to the cluster.'
                }
            ]
        }
    }
    assert utils.render_reports(test_data) == result


def test_render_reports_missing_content():
    data = test_data.copy()
    del data['content']
    with pytest.raises(ValueError):
        utils.render_reports(data)


def test_render_reports_missing_report_data():
    data = test_data.copy()
    del data['report_data']
    with pytest.raises(ValueError):
        utils.render_reports(data)


def test_render_reports_missing_clusters():
    data = test_data.copy()
    del data['report_data']['clusters']
    with pytest.raises(ValueError):
        utils.render_reports(data)


def test_render_reports_missing_reports():
    data = test_data.copy()
    del data['report_data']['reports']
    with pytest.raises(ValueError):
        utils.render_reports(data)
