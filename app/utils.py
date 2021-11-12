from app import DoT
import js2py
from app.logger import log

DoT_settings = {
    "evaluate": r"\{\{([\s\S]+?\}?)\}\}",
    "interpolate": r"\{\{=([\s\S]+?)\}\}",
    "encode": r"\{\{!([\s\S]+?)\}\}",
    "use": r"\{\{#([\s\S]+?)\}\}",
    "useParams": r"(^|[^\w$])def(?:\.|\[[\'\"])([\w$\.]+)(?:[\'\"]\])?\s*\:\s*([\w$\.]+|\"["
                 r"^\"]+\"|\'[^\']+\'|\{[ "
                 r"^\}]+\})",
    "define": r"\{\{##\s*([\w\.$]+)\s*(\:|=)([\s\S]+?)#\}\}",
    "defineParams": r"^\s*([\w$]+):([\s\S]+)",
    "conditional": r"\{\{\?(\?)?\s*([\s\S]*?)\s*\}\}",
    "iterate": r"\{\{~\s*(?:\}\}|([\s\S]+?)\s*\:\s*([\w$]+)\s*(?:\:\s*([\w$]+))?\s*\}\})",
    "varname": "pydata",
    "strip": True,
    "append": True,
    "selfcontained": False}


class RuleNotFoundException(Exception):
    pass


class TemplateNotFoundException(Exception):
    pass


def get_reported_module(report):
    if 'rule_id' not in report.keys():
        raise ValueError("'rule_id' key is not present in report data")
    if '|' not in report['rule_id']:
        raise ValueError(
            f"Value of 'rule_id' in report data is not in the correct format " +
            f"('{report['rule_id']}' does not contain '|')")
    return report['rule_id'].split('|')[0]


def get_reported_error_key(report):
    if 'rule_id' not in report.keys():
        raise ValueError("'rule_id' key is not present in report data")
    if '|' not in report['rule_id']:
        raise ValueError(
            f"Value of 'rule_id' in report data is not in the correct format " +
            f"('{report['rule_id']}' does not contain '|')")
    return report['rule_id'].split('|')[1]


def get_template_function(template_name, rule_content, report):
    template_text = rule_content[template_name]

    reported_error_key = get_reported_error_key(report)
    error_key_content = rule_content['error_keys'][reported_error_key]

    if template_name in error_key_content and error_key_content[template_name]:
        template_text = error_key_content[template_name]

    if template_text is None or template_text == "":
        reported_module = get_reported_module(report)
        raise TemplateNotFoundException(
            f"Template '{template_name}' has not been found for rule '{reported_module}' " +
            f"and error key '{reported_error_key}'.")

    return js2py.eval_js(DoT.template(template_text, DoT_settings))


def render_resolution(rule_content, report):
    resolution_template = get_template_function(
        'resolution', rule_content, report)
    return resolution_template(report['details'])


def render_reason(rule_content, report):
    reason_template = get_template_function('reason', rule_content, report)
    return reason_template(report['details'])


def render_report(content, report):
    try:
        reported_module = get_reported_module(report)
        reported_error_key = get_reported_error_key(report)
    except ValueError as e:
        log.error(e.msg())
        raise e

    for rule in content:
        if reported_module == rule['plugin']['python_module'].split('.')[-1]:
            report_result = {
                'rule_id': reported_module,
                'error_key': reported_error_key,
                'resolution': render_resolution(rule, report),
                'reason': render_reason(rule, report)
            }
            return report_result

    msg = f'The rule content for \'{reported_module}\' has not been found.'
    log.debug(msg)
    raise RuleNotFoundException(msg)


def check_request_data_format(request_data):
    return ('content' in request_data.keys() and
            'report_data' in request_data.keys() and
            'clusters' in request_data['report_data'].keys() and
            'reports' in request_data['report_data'].keys())


def render_reports(request_data):
    log.info("Loading content and report data")

    if not check_request_data_format(request_data):
        msg = "The request data do not have the expected structure"
        log.error(msg)
        raise ValueError(msg)

    content = request_data['content']
    report_data = request_data['report_data']
    result = {'clusters': report_data['clusters'], 'reports': {}}

    log.info("Iterating through the reports of each cluster")

    for cluster_id, cluster_data in report_data['reports'].items():
        for report in cluster_data['reports']:
            try:
                report_result = render_report(content, report)
                result['reports'].setdefault(
                    cluster_id, []).append(report_result)
            except:
                log.debug(
                    f"The report for rule '{get_reported_module(report)}'" +
                    f" and error key '{get_reported_error_key(report)}' " +
                    f"could not be processed")

    log.info("The reports from the request have been processed")

    return result
