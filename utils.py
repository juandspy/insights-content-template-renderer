import json
import DoT
import js2py

DoT_settings = {
    "evaluate": r"\{\{([\s\S]+?\}?)\}\}",
    "interpolate": r"\{\{=([\s\S]+?)\}\}",
    "encode": r"\{\{!([\s\S]+?)\}\}",
    "use":  r"\{\{#([\s\S]+?)\}\}",
    "useParams": r"(^|[^\w$])def(?:\.|\[[\'\"])([\w$\.]+)(?:[\'\"]\])?\s*\:\s*([\w$\.]+|\"[^\"]+\"|\'[^\']+\'|\{[^\}]+\})",
    "define": r"\{\{##\s*([\w\.$]+)\s*(\:|=)([\s\S]+?)#\}\}",
    "defineParams": r"^\s*([\w$]+):([\s\S]+)",
    "conditional": r"\{\{\?(\?)?\s*([\s\S]*?)\s*\}\}",
    "iterate": r"\{\{~\s*(?:\}\}|([\s\S]+?)\s*\:\s*([\w$]+)\s*(?:\:\s*([\w$]+))?\s*\}\})",

    "varname": "pydata",
    "strip": True,
    "append": True,
    "selfcontained": False
}


def get_reported_module(report):
    return report['rule_id'].split('|')[0]


def get_reported_error_key(report):
    return report['rule_id'].split('|')[1]


def get_template_function(template_name, rule_content, report):
    template_text = rule_content[template_name]

    reported_error_key = get_reported_error_key(report)
    error_key_content = rule_content['error_keys'][reported_error_key]

    if template_name in error_key_content:
        template_text = error_key_content[template_name]

    return js2py.eval_js(DoT.template(template_text, DoT_settings))


def render_resolution(rule_content, report):
    resolution_template = get_template_function('resolution', rule_content, report)
    return resolution_template(report['details'])


def render_reason(rule_content, reported_error_key):
    reason_template = get_template_function('reason', rule_content, report)
    return reason_template(report['details'])


def render_report(report, content):
    reported_module = get_reported_module()
    reported_error_key = get_reported_error_key()

    for rule in content:
        if reported_module == rule['plugin']['python_module'].split('.')[-1]:
           
            report_result = {}
            report_result['rule_id'] = reported_module
            report_result['error_key'] = reported_error_key
            report_result['resolution'] = render_resolution(rule, report)
            report_result['reason'] = render_reason(rule, report)

            return report_result


def render_reports(request_data):
    content = request_data['content']
    reports = request_data['reports']

    result = {}
    result['clusters'] = reports['clusters']
    result['reports'] = {}

    for cluster_id, cluster_data in reports['reports'].items():
        for report in cluster_data['reports']:
            report_result = render_report(report, content)
            result['reports'].setdefault(cluster_id, []).append(report_result)
            
    return result
