import json
import DoT
import js2py
from logger import logger

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

class RuleNotFound(Exception):
    pass

class TemplateNotFound(Exception):
    pass


def get_reported_module(report):
    return report['rule_id'].split('|')[0]


def get_reported_error_key(report):
    return report['rule_id'].split('|')[1]


def get_template_function(template_name, rule_content, report):
    template_text = rule_content[template_name]

    reported_error_key = get_reported_error_key(report)
    error_key_content = rule_content['error_keys'][reported_error_key]

    if template_name in error_key_content and error_key_content[template_name]:
        template_text = error_key_content[template_name]

    if template_text == None or template_text == "":
        reported_module = get_reported_module(report)
        raise TemplateNotFound(f'Template \'{template_name}\' has not been found for rule \'{reported_module}\' and error key \'{reported_error_key}\'.')

    return js2py.eval_js(DoT.template(template_text, DoT_settings))


def render_resolution(rule_content, report):
    resolution_template = get_template_function('resolution', rule_content, report)
    return resolution_template(report['details'])


def render_reason(rule_content, report):
    reason_template = get_template_function('reason', rule_content, report)
    return reason_template(report['details'])


def render_report(report, content):
    reported_module = get_reported_module(report)
    reported_error_key = get_reported_error_key(report)

    for rule in content:
        if reported_module == rule['plugin']['python_module'].split('.')[-1]:
           
            report_result = {}
            report_result['rule_id'] = reported_module
            report_result['error_key'] = reported_error_key
            report_result['resolution'] = render_resolution(rule, report)
            report_result['reason'] = render_reason(rule, report)

            return report_result
    msg = f'The rule content for \'{reported_module}\' has not been found.'
    logger.debug(msg)
    raise RuleNotFound(msg)


def render_reports(request_data):
    logger.info("Loading content and report data")
    if not ['content', 'report_data'].is_subset(request_data.keys()):
        logger.error("The request data do not have the expected structure; either 'content' or 'report_data' element is missing")
        raise 
    content = request_data['content']
    report_data = request_data['report_data']

    result = {}
    result['clusters'] = report_data['clusters']
    result['reports'] = {}

    logger.info("Iterating through the reports of each cluster")
    for cluster_id, cluster_data in report_data['reports'].items():
        for report in cluster_data['reports']:
            try:
                report_result = render_report(report, content)
                result['reports'].setdefault(cluster_id, []).append(report_result)
            except:
                logger.debug(f"The report for rule '{get_reported_module(report)}'" + 
                        f" and error key '{get_reported_error_key(report)}' " + 
                        f"could not be processed")
    logger.info("The reports from the request have been processed")        
    return result
