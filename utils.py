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

def render_reports(request_data):
    content = request_data['content']
    reports = request_data['reports']

    result = {}
    result['clusters'] = reports['clusters']
    result['reports'] = {}

    for cluster_id, cluster_data in reports['reports'].items():
        for report in cluster_data['reports']:
            reported_module = report['rule_id'].split('|')[0]
            reported_error_key = report['rule_id'].split('|')[1]

            for rule in content:
                if reported_module == rule['plugin']['python_module'].split('.')[-1]:

                    resolution = rule['resolution']
                    reason = rule['reason']

                    error_key_content = rule['error_keys'][reported_error_key]
                    if 'resolution' in error_key_content:
                        resolution = error_key_content['resolution']
                    if 'reason' in error_key_content:
                        reason = error_key_content['reason']

                    reason_template = js2py.eval_js(DoT.template(reason, DoT_settings))
                    resolution_template = js2py.eval_js(DoT.template(resolution, DoT_settings))
                    
                    report_result = {}
                    report_result['rule_id'] = reported_module
                    report_result['error_key'] = reported_error_key
                    report_result['resolution'] = resolution_template(report['details'])
                    report_result['reason'] = reason_template(report['details'])

                    result['reports'].setdefault(cluster_id, []).append(report_result)

                    break

    return result
