"""
Provides all business logic for this service.
"""

import js2py
from app import DoT
from app.logger import app_log as log
from app.DoT import template_settings

DoT_settings = template_settings
DoT_settings['varname'] = 'pydata'


class RuleNotFoundException(Exception):
    """
    Exception raised if the content data for reported module do not exist.
    """


class TemplateNotFoundException(Exception):
    """
    Exception raised if the template for given reported module
    and field name ('reason'/'resolution') does not exist.
    """


def get_reported_module(report):
    """
    Parses the 'rule_id' field of the report and returns the name of the reported module.

    :param report: dictionary with report details
    :return: name of the reported module
    """
    if 'rule_id' not in report.keys():
        raise ValueError("'rule_id' key is not present in report data")
    if '|' not in report['rule_id']:
        raise ValueError(
            "Value of 'rule_id' in report data is not in the correct format " +
            f"('{report['rule_id']}' does not contain '|')")
    return report['rule_id'].split('|')[0]


def get_reported_error_key(report):
    """
    Parses the 'rule_id' field of the report and returns the reported error key.

    :param report: dictionary with report details
    :return: reported error key
    """
    if 'rule_id' not in report.keys():
        raise ValueError("'rule_id' key is not present in report data")
    if '|' not in report['rule_id']:
        raise ValueError(
            "Value of 'rule_id' in report data is not in the correct format " +
            f"('{report['rule_id']}' does not contain '|')")
    return report['rule_id'].split('|')[1]


def get_template_function(template_name, rule_content, report):
    """
    Retrieves the DoT.js template based on the name of the field in the given content data
    and returns the Python function created with that template.

    :param template_name: field of the template (usually 'reason' or 'resolution')
    :param rule_content: dictionary with content data for the reported rule
    :param report: dictionary with report details
    :return: Python function for rendering report based on given report details
    """
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
    """
    Renders report resolution.

    :param rule_content: dictionary with content data for reported rule
    :param report: dictionary with report details
    :return: string with rendered resolution
    """
    resolution_template = get_template_function(
        'resolution', rule_content, report)
    return resolution_template(report['details'])


def render_reason(rule_content, report):
    """
    Renders report reason.

    :param rule_content: dictionary with content data for reported rule
    :param report: dictionary with report details
    :return: string with rendered reason
    """
    reason_template = get_template_function('reason', rule_content, report)
    return reason_template(report['details'])


def render_report(content, report):
    """
    Renders the given report.

    :param content: dictionary with content data for all rules
    :param report: dictionary with report details
    :return: rendered report
    """
    try:
        reported_module = get_reported_module(report)
        reported_error_key = get_reported_error_key(report)
    except ValueError as exception:
        log.error(str(exception))
        raise exception

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
    """
    Simple check that the request data for /rendered_reports contain the required fields.

    :param request_data: dictionary retrieved from JSON body of the request
    :return: true if the data have required fields, false otherwise
    """
    return ('content' in request_data.keys() and
            'report_data' in request_data.keys() and
            'clusters' in request_data['report_data'].keys() and
            'reports' in request_data['report_data'].keys())


def render_reports(request_data):
    """
    Renders all reports and returns dictionary with the rendered results.

    :param request_data: dictionary retrieved from JSON body of the request
    :return: rendered reports
    """
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
            except (ValueError, RuleNotFoundException, TemplateNotFoundException):
                log.debug(
                    f"The report for rule '{get_reported_module(report)}'" +
                    f" and error key '{get_reported_error_key(report)}' " +
                    "could not be processed")

    log.info("The reports from the request have been processed")

    return result
